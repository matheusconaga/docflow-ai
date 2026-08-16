import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base

class ActivitySubmission(Base):
    __tablename__ = "activity_submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_id = Column(String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    answers = Column(JSON, nullable=False)
    
    ai_score = Column(Float, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    
    question_scores = Column(JSON, nullable=True) # { "0": 10.0, "1": 0.0 }
    
    final_score = Column(Float, nullable=True)
    final_feedback = Column(Text, nullable=True)
    
    status = Column(String(50), default="pending_review", nullable=False) # pending_review, reviewed
    
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="submissions")
    student = relationship("StudentModel")
