import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from app.db.database import Base


# DOCUMENT MODEL FOR NEON DB AND SQLALCHEMY ORM
class Document(Base):

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    filename = Column(String, nullable=False)

    stored_filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    extracted_text = Column(Text, nullable=True)

    status = Column(String, default="uploaded")

    created_at = Column(DateTime, default=datetime.utcnow)
