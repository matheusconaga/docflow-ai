from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class SkillItem(BaseModel):
    code: str | None = None
    description: str


class DocumentStructuredResponse(BaseModel):

    id: str

    document_id: str

    subject: str

    level: str

    contents: List[str]

    skills: List[SkillItem]

    methodologies: List[str]

    assessment: List[str]

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
