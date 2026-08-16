from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.activity import Activity
from app.models.activity_submission import ActivitySubmission
from app.models.student_model import StudentModel
from app.models.class_model import ClassModel
from app.core.security import get_current_user

router = APIRouter()

class GlobalSubmissionResponse(BaseModel):
    id: str
    activity_id: str
    activity_title: str
    class_name: str
    student_id: str
    student_name: str
    status: str
    submitted_at: str
    ai_score: Optional[float]
    final_score: Optional[float]

class DetailedSubmissionResponse(GlobalSubmissionResponse):
    answers: dict
    structured_content: Optional[dict]
    question_scores: Optional[dict]
    ai_feedback: Optional[str]
    final_feedback: Optional[str]

class SubmissionApproveRequest(BaseModel):
    final_score: float
    final_feedback: str
    question_scores: Optional[dict] = None

@router.get("/pending", response_model=List[GlobalSubmissionResponse])
def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Pega todas as atividades do professor
    activities = db.query(Activity).filter(Activity.teacher_id == current_user.id).all()
    activity_ids = [act.id for act in activities]
    
    if not activity_ids:
        return []
        
    submissions = db.query(ActivitySubmission).filter(
        ActivitySubmission.activity_id.in_(activity_ids),
        ActivitySubmission.status == "pending_review"
    ).order_by(ActivitySubmission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        act = next((a for a in activities if a.id == sub.activity_id), None)
        class_obj = db.query(ClassModel).filter(ClassModel.id == act.class_id).first() if act else None
        student = db.query(StudentModel).filter(StudentModel.id == sub.student_id).first()
        
        result.append(GlobalSubmissionResponse(
            id=sub.id,
            activity_id=sub.activity_id,
            activity_title=act.title if act else "Desconhecido",
            class_name=class_obj.name if class_obj else "Geral",
            student_id=sub.student_id,
            student_name=student.name if student else "Desconhecido",
            status=sub.status,
            submitted_at=sub.submitted_at.isoformat(),
            ai_score=sub.ai_score,
            final_score=sub.final_score
        ))
        
    return result

@router.get("/{sub_id}", response_model=DetailedSubmissionResponse)
def get_submission_details(
    sub_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ActivitySubmission).filter(ActivitySubmission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
        
    act = db.query(Activity).filter(Activity.id == sub.activity_id, Activity.teacher_id == current_user.id).first()
    if not act:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    student = db.query(StudentModel).filter(StudentModel.id == sub.student_id).first()
    class_obj = db.query(ClassModel).filter(ClassModel.id == act.class_id).first()

    return DetailedSubmissionResponse(
        id=sub.id,
        activity_id=sub.activity_id,
        activity_title=act.title,
        class_name=class_obj.name if class_obj else "Geral",
        student_id=sub.student_id,
        student_name=student.name if student else "Desconhecido",
        status=sub.status,
        submitted_at=sub.submitted_at.isoformat(),
        ai_score=sub.ai_score,
        final_score=sub.final_score,
        answers=sub.answers,
        structured_content=act.structured_content,
        question_scores=sub.question_scores,
        ai_feedback=sub.ai_feedback,
        final_feedback=sub.final_feedback
    )

@router.put("/{sub_id}/approve")
def approve_global_submission(
    sub_id: str,
    data: SubmissionApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ActivitySubmission).filter(ActivitySubmission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Entrega não encontrada")
        
    act = db.query(Activity).filter(Activity.id == sub.activity_id, Activity.teacher_id == current_user.id).first()
    if not act:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    sub.final_score = data.final_score
    sub.final_feedback = data.final_feedback
    if data.question_scores is not None:
        sub.question_scores = data.question_scores
    sub.status = "reviewed"
    db.commit()
    
    return {"status": "success"}
