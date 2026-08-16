from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: Optional[str] = "info"

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
