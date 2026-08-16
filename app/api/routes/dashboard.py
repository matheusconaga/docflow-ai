from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics", response_model=Dict[str, Any])
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard metrics for the logged-in teacher.
    Currently fetches real total_classes and returns placeholders for other metrics 
    that will be implemented over time.
    """
    total_classes = db.query(ClassModel).filter(ClassModel.teacher_id == current_user.id).count()
    
    # Calculate average performance from classes if there are any
    classes = db.query(ClassModel).filter(ClassModel.teacher_id == current_user.id).all()
    avg_performance = 0
    if classes and len(classes) > 0:
        total_perf = sum(c.average_grade for c in classes)
        avg_performance = round(total_perf / len(classes))
    
    return {
        "total_classes": total_classes,
        "total_documents": 0, # To be implemented
        "total_lesson_plans": 0, # To be implemented
        "total_activities": 0, # To be implemented
        "saved_hours": 0, # To be implemented
        "average_performance": avg_performance
    }
