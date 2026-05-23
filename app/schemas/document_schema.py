from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


# SCHEMA FOR GUARANTEEING THE RESPONSE OF DOCUMENTS ENDPOINTS
class DocumentResponse(BaseModel):

    id: UUID
    filename: str
    file_path: str
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )