from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.rag_schema import (ChunkSource, RAGQueryRequest,
                                    RAGQueryResponse, RAGSearchRequest)
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/query", response_model=RAGQueryResponse)
def rag_query(request: RAGQueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return RAGService.query(
        db=db,
        query=request.query,
        teacher_id=current_user.id,
        class_id=request.class_id,
        top_k=request.top_k,
        chunk_type=request.chunk_type,
    )


@router.post("/search", response_model=list[ChunkSource])
def rag_search(request: RAGSearchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return RAGService.search(
        db=db,
        query=request.query,
        teacher_id=current_user.id,
        class_id=request.class_id,
        top_k=request.top_k,
        chunk_type=request.chunk_type,
    )
