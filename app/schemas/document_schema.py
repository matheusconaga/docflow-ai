from datetime import datetime

from pydantic import BaseModel, ConfigDict


# SCHEMA FOR GUARANTEEING THE RESPONSE OF DOCUMENTS ENDPOINTS
class DocumentResponse(BaseModel):

    id: str
    filename: str
    file_path: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
