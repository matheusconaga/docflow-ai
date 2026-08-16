import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base

class ClassModel(Base):
    __tablename__ = "classes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    grade = Column(String(255), nullable=False)
    students_count = Column(Integer, default=0)
    status = Column(String(50), default="healthy")  # healthy, warning, critical
    average_grade = Column(Float, default=0.0)
    next_class_topic = Column(String(255), default="Nenhum tópico definido")
    status_message = Column(String(500), default="A turma está progredindo bem.")
    
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    teacher = relationship("User", back_populates="classes")
    students = relationship("StudentModel", back_populates="class_", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="class_", cascade="all, delete-orphan")
    lesson_plans = relationship("LessonPlan", back_populates="class_", cascade="all, delete-orphan")
