from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):

    id: str

    structured_document_id: str

    chunk_type: str

    content: str

    chunk_metadata: Optional[dict[str, str]]

    embedding: Optional[list[float]] = None

    created_at: datetime

    class Config:
        from_attributes = True
