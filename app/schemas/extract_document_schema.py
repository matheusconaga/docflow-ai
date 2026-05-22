from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ExtractDocumentResponse(BaseModel):

    id: UUID
    filename: str
    extracted_text: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True