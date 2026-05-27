from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentEmbeddingResponse(BaseModel):

    id: str

    structured_document_id: str

    chunk_type: str

    chunk_order: int

    content: str

    chunk_metadata: Optional[dict]

    embedding: Optional[list[float]]

    created_at: datetime

    class Config:
        from_attributes = True
