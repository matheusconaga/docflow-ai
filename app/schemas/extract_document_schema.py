from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ExtractDocumentResponse(BaseModel):

    id: UUID
    filename: str
    extracted_text: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )