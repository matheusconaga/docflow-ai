from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.student_model import StudentModel
from app.schemas.student_schema import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter(prefix="/classes", tags=["Students"])

@router.get("/{class_id}/students", response_model=List[StudentResponse])
def get_students(
    class_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all students for a specific class. Validates if teacher owns the class."""
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id, 
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
        
    return db_class.students

@router.post("/{class_id}/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    class_id: str,
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a student to a specific class."""
    db_class = db.query(ClassModel).filter(
        ClassModel.id == class_id, 
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_class:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
        
    db_student = StudentModel(
        **data.model_dump(),
        class_id=class_id
    )
    
    # Increment students count
    db_class.students_count += 1
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific student."""
    db_student = db.query(StudentModel).join(ClassModel).filter(
        StudentModel.id == student_id,
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
        
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific student and decrement class count."""
    db_student = db.query(StudentModel).join(ClassModel).filter(
        StudentModel.id == student_id,
        ClassModel.teacher_id == current_user.id
    ).first()
    
    if not db_student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
    # Decrement students count
    db_class = db_student.class_
    if db_class.students_count > 0:
        db_class.students_count -= 1
        
    db.delete(db_student)
    db.commit()
    return None
