import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class LessonPlanTemplate(Base):
    __tablename__ = "lesson_plan_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String, nullable=False)
    html_content = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
