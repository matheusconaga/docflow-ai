from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional

# SCHEMA FOR GUARANTEEING THE RESPONSE OF DOCUMENTS ENDPOINTS
class DocumentResponse(BaseModel):

    id: str
    class_id: Optional[str] = None
    teacher_id: str
    filename: str
    file_path: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
