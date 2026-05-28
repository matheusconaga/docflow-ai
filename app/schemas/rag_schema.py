from typing import Optional

from pydantic import BaseModel


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    chunk_type: Optional[str] = None


class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    chunk_type: Optional[str] = None


class ChunkSource(BaseModel):
    id: str
    chunk_type: str
    content: str
    chunk_metadata: Optional[dict] = None

    model_config = {"from_attributes": True}


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[ChunkSource]
