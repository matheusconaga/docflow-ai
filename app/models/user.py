import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(255), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password_hash = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False, default="teacher")  # teacher, admin, student

    is_active = Column(Boolean, default=True)

    # Billing & Subscription
    plan_type = Column(String(50), default="free") # free, essencial, pro
    ai_credits = Column(Integer, default=5) # 5 for free, 35 for essencial, 100 for pro
    plan_expires_at = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)

    # Profile fields
    bio = Column(Text, nullable=True)

    school = Column(String(255), nullable=True)

    position = Column(String(255), nullable=True)

    subject = Column(String(255), nullable=True)

    grade = Column(String(255), nullable=True)

    specialties = Column(String(500), nullable=True)

    avatar_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    classes = relationship("ClassModel", back_populates="teacher", cascade="all, delete-orphan")
