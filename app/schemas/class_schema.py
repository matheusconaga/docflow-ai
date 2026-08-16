from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClassCreate(BaseModel):
    name: str
    subject: str
    grade: str
    students_count: int

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    students_count: Optional[int] = None
    status: Optional[str] = None
    average_grade: Optional[float] = None
    next_class_topic: Optional[str] = None
    status_message: Optional[str] = None

class ClassResponse(BaseModel):
    id: str
    name: str
    subject: str
    grade: str
    students_count: int
    status: str
    average_grade: float
    next_class_topic: str
    status_message: str
    teacher_id: str
    is_locked: Optional[bool] = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
