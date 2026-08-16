import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.database import Base


# DOCUMENT MODEL FOR NEON DB AND SQLALCHEMY ORM
class Document(Base):

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(String(36), ForeignKey("classes.id", ondelete="CASCADE"), nullable=True)

    filename = Column(String, nullable=False)

    stored_filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    extracted_text = Column(Text, nullable=True)

    status = Column(String, default="uploaded")

    created_at = Column(DateTime, default=datetime.utcnow)

    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    class_ = relationship("ClassModel", back_populates="documents")
    teacher = relationship("User")
