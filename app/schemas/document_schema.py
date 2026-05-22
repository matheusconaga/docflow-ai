from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# SCHEMA FOR GARANTING THE RESPONSE OF DOCUMENTS ENDPOINTS
class DocumentResponse(BaseModel):

    id: UUID
    filename: str
    file_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True