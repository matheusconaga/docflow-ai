from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.class_model import ClassModel
from app.models.document import Document
from app.models.lesson_plan import LessonPlan
from app.models.activity import Activity

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
    total_docs = db.query(Document).filter(Document.teacher_id == current_user.id).count()
    total_plans = db.query(LessonPlan).filter(LessonPlan.teacher_id == current_user.id).count()
    total_activities = db.query(Activity).filter(Activity.teacher_id == current_user.id).count()
    
    # Calculate saved hours. Let's assume each lesson plan saves 1 hour, each activity saves 2 hours, and each document saves 30 mins
    saved_hours = (total_plans * 1) + (total_activities * 2) + int(total_docs * 0.5)
    
    # Calculate average performance from classes if there are any
    classes = db.query(ClassModel).filter(ClassModel.teacher_id == current_user.id).all()
    avg_performance = 0
    if classes and len(classes) > 0:
        total_perf = sum(c.average_grade for c in classes)
        avg_performance = round(total_perf / len(classes))
    
    return {
        "total_classes": total_classes,
        "total_documents": total_docs,
        "total_lesson_plans": total_plans,
        "total_activities": total_activities,
        "saved_hours": saved_hours,
        "average_performance": avg_performance
    }

@router.get("/history", response_model=List[Dict[str, Any]])
def get_dashboard_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(Document).filter(Document.teacher_id == current_user.id).order_by(Document.created_at.desc()).limit(5).all()
    plans = db.query(LessonPlan).filter(LessonPlan.teacher_id == current_user.id).order_by(LessonPlan.created_at.desc()).limit(5).all()
    activities = db.query(Activity).filter(Activity.teacher_id == current_user.id).order_by(Activity.created_at.desc()).limit(5).all()
    
    history = []
    
    for doc in docs:
        history.append({
            "id": doc.id,
            "title": doc.filename,
            "type": "document",
            "status": "Concluído",
            "statusVariant": "success",
            "created_at": doc.created_at.isoformat()
        })
        
    for plan in plans:
        history.append({
            "id": plan.id,
            "title": plan.topic,
            "type": "lesson_plan",
            "status": "Concluído",
            "statusVariant": "success",
            "created_at": plan.created_at.isoformat()
        })
        
    for act in activities:
        history.append({
            "id": act.id,
            "title": act.title,
            "type": "activity",
            "status": "Concluído",
            "statusVariant": "success",
            "created_at": act.created_at.isoformat()
        })
        
    history.sort(key=lambda x: x["created_at"], reverse=True)
    return history[:5]
