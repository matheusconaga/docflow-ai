import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from app.db.database import Base


class DocumentChunk(Base):

    __tablename__ = "documents_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    structured_document_id = Column(
        String,
        ForeignKey("documents_structured.id", ondelete="CASCADE"),
        nullable=False,
    )

    # CHUNK CATEGORY
    # EXAMPLE:
    # lesson_plan
    # activity
    # assessment
    # bncc
    # recommendation
    # insight
    chunk_type = Column(String, nullable=False)

    # CHUNK POSITION
    # USED TO REBUILD CONTEXT ORDER
    chunk_order = Column(Integer, nullable=False)

    # MAIN CHUNK CONTENT
    content = Column(Text, nullable=False)

    # EXTRA PEDAGOGICAL CONTEXT
    # EXAMPLE:
    # subject
    # level
    # skill_codes
    # methodologies
    chunk_metadata = Column(JSON, nullable=True)

    # VECTOR EMBEDDING
    # USED FOR SEMANTIC SEARCH
    embedding = Column(Vector(3072), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    structured_document = relationship("DocumentStructured", back_populates="chunks")
