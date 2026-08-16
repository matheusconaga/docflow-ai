from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StudentCreate(BaseModel):
    name: str
    email: Optional[str] = None
    has_special_needs: bool = False
    special_needs_description: Optional[str] = None
    avatar_url: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    has_special_needs: Optional[bool] = None
    special_needs_description: Optional[str] = None
    avatar_url: Optional[str] = None

class StudentResponse(BaseModel):
    id: str
    class_id: str
    name: str
    email: Optional[str] = None
    has_special_needs: bool
    special_needs_description: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
