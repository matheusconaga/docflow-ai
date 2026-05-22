import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    func
)

from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


# DOCUMENT MODEL FOR NEON DB AND SQLALCHEMY ORM
class Document(Base):

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    filename = Column(
        String,
        nullable=False
    )

    stored_filename = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        default="uploaded"
    )

    created_at = Column(
        DateTime,
        default=func.now()
    )