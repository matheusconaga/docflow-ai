from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.pre_registration import PreRegistration
from app.schemas.pre_registration import PreRegistrationCreate, PreRegistrationResponse
from app.services.email_service import send_welcome_email
from app.core.security import require_role

router = APIRouter(
    prefix="/pre-register",
    tags=["Pre-Registration"],
)

@router.post("/", response_model=PreRegistrationResponse)
def create_pre_registration(data: PreRegistrationCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(PreRegistration).filter(PreRegistration.email == data.email).first()
    if existing:
        # Se já existir, podemos retornar o mesmo para não estressar o usuário, mas evitamos enviar 2 emails
        return existing

    new_reg = PreRegistration(
        email=data.email,
        role=data.role,
        area=data.area
    )
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)

    # Envia o e-mail de boas-vindas
    send_welcome_email(new_reg.email)

    return new_reg

@router.get("/", response_model=List[PreRegistrationResponse], dependencies=[Depends(require_role("admin"))])
def get_all_pre_registrations(db: Session = Depends(get_db)):
    return db.query(PreRegistration).order_by(PreRegistration.created_at.desc()).all()
