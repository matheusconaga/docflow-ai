import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from datetime import datetime, timedelta
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.billing_history import BillingHistory
from app.services.abacatepay_service import create_checkout, verify_abacatepay_webhook
from app.core.plan_config import PLAN_LIMITS, get_credit_limit

router = APIRouter(prefix="/billing", tags=["Billing"])

class CheckoutRequest(BaseModel):
    plan_type: str # "essencial" or "pro"

@router.post("/checkout")
async def generate_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gera um link de pagamento no AbacatePay para o plano escolhido."""
    if data.plan_type not in ["essencial", "pro"]:
        raise HTTPException(status_code=400, detail="Plano inválido.")

    try:
        url = await create_checkout(
            plan_type=data.plan_type,
            user_id=current_user.id,
            email=current_user.email,
            name=current_user.name
        )
        return {"url": url}
    except Exception as e:
        print(f"Error generating checkout: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar checkout no AbacatePay.")


@router.post("/webhook")
async def abacatepay_webhook(request: Request, db: Session = Depends(get_db)):
    """Recebe notificações de pagamento do AbacatePay."""
    # Obter raw body e header de assinatura
    raw_body = await request.body()
    # Header real dependeria da doc, usando um fallback se não vier
    signature = request.headers.get("x-abacatepay-signature", "")
    secret = os.getenv("ABACATEPAY_WEBHOOK_SECRET", "")

    # Validação (desativada para localhost se não houver secret)
    if not verify_abacatepay_webhook(raw_body, signature, secret):
        raise HTTPException(status_code=400, detail="Assinatura inválida.")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload inválido.")

    event = payload.get("event")
    data = payload.get("data", {})

    if event == "checkout.completed":
        # Pagamento confirmado!
        checkout_data = data.get("checkout", {})
        metadata = checkout_data.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_type = metadata.get("plan_type")

        if not user_id or not plan_type:
            # Tentar buscar pelo customer_id se não houver metadata (fallback avançado)
            return {"status": "ignored", "reason": "Missing metadata.user_id"}

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Rollover de Créditos — desconta o que já foi usado no ciclo anterior
            old_limit = get_credit_limit(user.plan_type)
            used_credits = max(0, old_limit - user.ai_credits)

            user.plan_type = plan_type
            user.plan_expires_at = datetime.utcnow() + timedelta(days=30)
            user.cancel_at_period_end = False

            # Novo limite de créditos - descontando os já usados no ciclo
            new_limit = get_credit_limit(plan_type)
            user.ai_credits = max(0, new_limit - used_credits)
            
            # Registrar Histórico
            amount = checkout_data.get("amount", 0)
            history_record = BillingHistory(
                user_id=user.id,
                amount=amount,
                status="PAID",
                plan_name=plan_type.capitalize()
            )
            db.add(history_record)
            
            db.commit()
            print(f"User {user.email} upgraded to {plan_type}! History logged.")
            return {"status": "success"}
        else:
            print(f"User {user_id} not found for webhook upgrade.")
            return {"status": "error", "reason": "User not found"}

    return {"status": "ignored"}

@router.get("/history")
def get_billing_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(BillingHistory).filter(
        BillingHistory.user_id == current_user.id
    ).order_by(BillingHistory.created_at.desc()).all()
    
    return [
        {
            "id": h.id,
            "amount": h.amount,
            "status": h.status,
            "plan_name": h.plan_name,
            "is_refund_requested": h.is_refund_requested,
            "created_at": h.created_at.isoformat()
        } for h in history
    ]

@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.plan_type == "free":
        raise HTTPException(status_code=400, detail="Você já está no plano Gratuito.")
        
    current_user.cancel_at_period_end = True
    db.commit()
    return {"status": "success", "message": "Sua assinatura será cancelada no final do período ativo."}

class RefundRequest(BaseModel):
    history_id: str

@router.post("/refund")
def request_refund(
    data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(BillingHistory).filter(
        BillingHistory.id == data.history_id,
        BillingHistory.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Fatura não encontrada.")
        
    if history.is_refund_requested:
        raise HTTPException(status_code=400, detail="Reembolso já solicitado para esta fatura.")
        
    history.is_refund_requested = True
    db.commit()
    
    return {"status": "success", "message": "Reembolso solicitado com sucesso."}
