from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.class_model import ClassModel
from app.models.billing_history import BillingHistory
from app.schemas.admin import AdminUserResponse, AdminMetricsResponse, TransactionResponse, ChartDataPoint
from app.core.security import require_role

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role("admin"))]
)

@router.get("/users", response_model=List[AdminUserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    response = []
    for user in users:
        docs_count = db.query(func.count(Document.id)).filter(Document.teacher_id == user.id).scalar() or 0
        classes_count = db.query(func.count(ClassModel.id)).filter(ClassModel.teacher_id == user.id).scalar() or 0
        
        response.append(AdminUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            plan=user.plan_type.capitalize() if user.plan_type else "Free",
            status="active" if user.is_active else "suspended",
            joinDate=user.created_at.strftime("%Y-%m-%d"),
            documentsGenerated=docs_count,
            classesCount=classes_count
        ))
    return response

@router.get("/metrics", response_model=AdminMetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    
    # MRR calculation (Sum of amount where status is PAID in the last month, assuming simple logic)
    # We'll just sum all PAID amounts and divide by 100 since amount is in cents
    mrr_cents = db.query(func.sum(BillingHistory.amount)).filter(BillingHistory.status == "PAID").scalar() or 0
    mrr = mrr_cents / 100.0

    # For credits used, maybe sum of total documents for now
    total_credits = db.query(func.count(Document.id)).scalar() or 0
    
    # Churn rate dummy calculation
    suspended_users = total_users - active_users
    churn_rate = (suspended_users / total_users * 100) if total_users > 0 else 0.0

    # Chart data calculation
    pt_months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    monthly_data = {i: {"revenue": 0.0, "users": 0} for i in range(12)}
    
    paid_txs = db.query(BillingHistory).filter(BillingHistory.status == "PAID").all()
    for tx in paid_txs:
        m_index = tx.created_at.month - 1
        monthly_data[m_index]["revenue"] += (tx.amount / 100.0)
        
    all_users_list = db.query(User).all()
    for u in all_users_list:
        m_index = u.created_at.month - 1
        monthly_data[m_index]["users"] += 1
        
    chart_data = []
    # Only include months that have at least some users or revenue, or maybe the current year up to now
    current_month = datetime.utcnow().month - 1
    # Find the earliest month with data
    earliest_month = 0
    for i in range(12):
        if monthly_data[i]["users"] > 0 or monthly_data[i]["revenue"] > 0:
            earliest_month = i
            break
            
    for i in range(earliest_month, current_month + 1):
        chart_data.append(ChartDataPoint(
            name=pt_months[i],
            revenue=monthly_data[i]["revenue"],
            users=monthly_data[i]["users"]
        ))

    return AdminMetricsResponse(
        totalUsers=total_users,
        activeUsers=active_users,
        mrr=mrr,
        totalCreditsUsed=total_credits,
        churnRate=round(churn_rate, 2),
        chartData=chart_data
    )

@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(BillingHistory).order_by(BillingHistory.created_at.desc()).limit(50).all()
    response = []
    for t in transactions:
        user = db.query(User).filter(User.id == t.user_id).first()
        response.append(TransactionResponse(
            id=t.id,
            userId=t.user_id,
            userName=user.name if user else "Usuário Deletado",
            amount=t.amount / 100.0,
            date=t.created_at.strftime("%Y-%m-%d"),
            status=t.status.lower(),
            plan=t.plan_name
        ))
    return response

@router.post("/users/{user_id}/toggle-status")
def toggle_user_status(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Can't suspend yourself easily but we allow for now or skip self check
    user.is_active = not user.is_active
    db.commit()
    return {"status": "success", "is_active": user.is_active}
