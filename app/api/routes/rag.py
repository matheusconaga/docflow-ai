from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.rag_schema import (
    ChunkSource,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSearchRequest,
)
from app.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGQueryResponse)
def rag_query(request: RAGQueryRequest, db: Session = Depends(get_db)):
    return RAGService.query(
        db=db,
        query=request.query,
        top_k=request.top_k,
        chunk_type=request.chunk_type,
        mode=request.mode,
    )


@router.post("/search", response_model=list[ChunkSource])
def rag_search(request: RAGSearchRequest, db: Session = Depends(get_db)):
    return RAGService.search(
        db=db,
        query=request.query,
        top_k=request.top_k,
        chunk_type=request.chunk_type,
    )
