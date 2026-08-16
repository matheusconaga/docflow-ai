import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    activity_type = Column(String, nullable=False) # Ex: Prova, Exercício
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False) # Fácil, Médio, Difícil
    questions_count = Column(Integer, nullable=False)
    
    generated_content = Column(Text, nullable=False) # Legacy text or backup
    structured_content = Column(JSON, nullable=True) # JSON with the questions
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    teacher = relationship("User")
    class_ = relationship("ClassModel", back_populates="activities")
    submissions = relationship("ActivitySubmission", back_populates="activity", cascade="all, delete-orphan")
