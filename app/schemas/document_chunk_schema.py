from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):

    id: str

    structured_document_id: str

    chunk_type: str

    content: str

    chunk_metadata: Optional[dict[str, Any]]

    embedding: Optional[list[float]] = None

    created_at: datetime

    class Config:
        from_attributes = True
