import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String

from app.db.database import Base


class DocumentStructured(Base):

    __tablename__ = "documents_structured"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    document_id = Column(
        String, ForeignKey("documents.id"), nullable=False, unique=True
    )

    subject = Column(String, nullable=False)

    level = Column(String, nullable=False)

    contents = Column(JSON, nullable=False)

    skills = Column(JSON, nullable=False)

    methodologies = Column(JSON, nullable=False)

    assessment = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
