from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("/", response_model=List[ClassResponse])
def get_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all classes for the logged in teacher."""
    classes = db.query(ClassModel).filter(
        ClassModel.teacher_id == current_user.id,
        ClassModel.is_deleted == False
    ).all()
    return classes

@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new class for the logged in teacher."""
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
    return None
