from pydantic import BaseModel, EmailStr
from datetime import datetime

class PreRegistrationCreate(BaseModel):
    email: EmailStr
    role: str
    area: str

class PreRegistrationResponse(BaseModel):
    id: str
    email: str
    role: str
    area: str
    created_at: datetime

    class Config:
        from_attributes = True
