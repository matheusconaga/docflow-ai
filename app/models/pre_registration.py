import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String

from app.db.database import Base


class PreRegistration(Base):
    __tablename__ = "pre_registrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
