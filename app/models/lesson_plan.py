import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base

class LessonPlan(Base):
    __tablename__ = "lesson_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    objectives = Column(Text, nullable=False)
    duration = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    template = Column(String, nullable=False)
    
    methodologies = Column(JSONB, default=[])
    resources = Column(JSONB, default=[])
    special_needs = Column(Text, nullable=True)
    
    generated_content = Column(Text, nullable=False)
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    teacher = relationship("User")
    class_ = relationship("ClassModel", back_populates="lesson_plans")
