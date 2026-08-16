import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False) # in cents
    status = Column(String(50), nullable=False) # e.g. PAID, PENDING, REFUNDED
    plan_name = Column(String(50), nullable=False)
    is_refund_requested = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="billing_history")
