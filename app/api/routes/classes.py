from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.student_model import StudentModel
from app.models.activity import Activity
from app.models.activity_submission import ActivitySubmission
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse
from app.core.plan_config import PLAN_LIMITS, get_class_limit

router = APIRouter(prefix="/classes", tags=["Classes"])


def get_limit(plan_type: str) -> int:
    return get_class_limit(plan_type)


def auto_unlock_on_upgrade(db: Session, user: User):
    """If user upgraded to a higher plan, unlock classes that no longer need to be locked,
    keeping the user's explicit selection whenever possible."""
    limit = get_limit(user.plan_type)
    
    # Count currently active (unlocked) classes
    active_count = db.query(ClassModel).filter(
        ClassModel.teacher_id == user.id,
        ClassModel.is_deleted == False,
        ClassModel.is_locked == False
    ).count()
    
    # If under the limit, unlock locked classes (oldest first) until we fill up
    if active_count < limit:
        slots_available = limit - active_count
        locked_classes = db.query(ClassModel).filter(
            ClassModel.teacher_id == user.id,
            ClassModel.is_deleted == False,
            ClassModel.is_locked == True
        ).order_by(ClassModel.created_at.asc()).limit(slots_available).all()
        
        for c in locked_classes:
            c.is_locked = False
        
        if locked_classes:
            db.commit()


@router.get("/", response_model=List[ClassResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all classes for the logged in teacher.
    Auto-unlocks classes if the user upgraded to a higher plan."""
    auto_unlock_on_upgrade(db, current_user)
    
    classes = db.query(ClassModel).filter(
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False
    ).order_by(ClassModel.created_at.asc()).all()
    
    return classes


class LockSelectionRequest(BaseModel):
    active_class_ids: List[str]


@router.post("/lock-selection", status_code=status.HTTP_200_OK)
def lock_selection(
    data: LockSelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allow the user to choose which classes stay active when over plan limit.
    All classes NOT in active_class_ids will be locked. Once chosen, the selection
    is persisted in the DB and cannot be changed until a plan upgrade."""
    limit = get_limit(current_user.plan_type)

    if len(data.active_class_ids) > limit:
        raise HTTPException(
            status_code=400,
            detail=f"Você só pode manter {limit} turma(s) ativa(s) no seu plano atual."
        )

    all_classes = db.query(ClassModel).filter(
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False
    ).all()

    for c in all_classes:
        c.is_locked = c.id not in data.active_class_ids

    db.commit()
    return {"message": "Seleção de turmas salva com sucesso."}


@router.get("/lock-status")
def get_lock_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if the user needs to choose which classes to keep active."""
    limit = get_limit(current_user.plan_type)
    
    all_classes = db.query(ClassModel).filter(
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False
    ).all()
    
    total = len(all_classes)
    locked_count = sum(1 for c in all_classes if c.is_locked)
    active_count = total - locked_count
    
    # User needs to choose if they have more active classes than their limit allows
    # AND they haven't made a selection yet (all classes still unlocked with count > limit)
    needs_selection = (active_count > limit)
    
    return {
        "needs_selection": needs_selection,
        "total": total,
        "active_count": active_count,
        "limit": limit,
        "plan_type": current_user.plan_type
    }


@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new class for the logged in teacher."""
    limit = get_limit(current_user.plan_type)
    
    active_count = db.query(ClassModel).filter(
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False,
        ClassModel.is_locked == False
    ).count()
    
    if active_count >= limit:
        raise HTTPException(
            status_code=403, 
            detail=f"Limite de turmas atingido. Seu plano atual ({current_user.plan_type}) permite até {limit} turma(s) ativa(s). Faça upgrade para criar mais turmas."
        )

    db_class = ClassModel(
        **data.model_dump(),
        teacher_id=current_user.id
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


@router.get("/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific class by ID."""
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id,
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    return db_class


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: str,
    data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific class."""
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id,
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_class, key, value)
        
    db.commit()
    db.refresh(db_class)
    return db_class


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific class."""
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id,
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
        
    db.delete(db_class)
    db.commit()
    
    return {"status": "success"}


@router.get("/{class_id}/grades")
def get_class_grades(
    class_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar se a turma pertence ao professor
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id,
        ClassModel.teacher_id == current_user.id
    ).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    # Pegar todas as atividades da turma (as colunas)
    activities = db.query(Activity).filter(
        Activity.class_id == class_id,
        Activity.is_deleted == False
    ).order_by(Activity.created_at.asc()).all()

    # Pegar todos os alunos da turma (as linhas)
    students = db.query(StudentModel).filter(
        StudentModel.class_id == class_id
    ).order_by(StudentModel.name.asc()).all()

    # Pegar todas as submissões dessas atividades (as células)
    activity_ids = [act.id for act in activities]
    submissions = []
    if activity_ids:
        submissions = db.query(ActivitySubmission).filter(
            ActivitySubmission.activity_id.in_(activity_ids),
            ActivitySubmission.status == "reviewed"
        ).all()

    columns = [{"id": a.id, "title": a.title, "date": a.created_at.isoformat()} for a in activities]
    
    rows = []
    for student in students:
        student_grades = {}
        for sub in submissions:
            if sub.student_id == student.id and sub.final_score is not None:
                student_grades[sub.activity_id] = sub.final_score
        
        rows.append({
            "student_id": student.id,
            "student_name": student.name,
            "grades": student_grades
        })

    return {
        "activities": columns,
        "students": rows
    }
