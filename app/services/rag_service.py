from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.embeddings.orchestrator.embedding_generator import \
    EmbeddingGenerator
from app.ai.rag.generator import RAGGenerator
from app.ai.rag.retriever import VectorRetriever


class RAGService:

    @staticmethod
    def query(
        db: Session,
        query: str,
        teacher_id: str,
        class_id: str | None = None,
        top_k: int = 5,
        chunk_type: str | None = None,
    ) -> dict:
        query_embedding = EmbeddingGenerator.generate(query)

        chunks = VectorRetriever.search(
            db=db,
            query_embedding=query_embedding,
            teacher_id=teacher_id,
            class_id=class_id,
            top_k=top_k,
            chunk_type=chunk_type,
        )

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail="Nenhum chunk relevante encontrado para a consulta",
            )

        answer = RAGGenerator.generate(query=query, chunks=chunks)

        return {"answer": answer, "sources": chunks}

    @staticmethod
    def search(
        db: Session,
        query: str,
        teacher_id: str,
        class_id: str | None = None,
        top_k: int = 5,
        chunk_type: str | None = None,
    ) -> list:
        query_embedding = EmbeddingGenerator.generate(query)

        chunks = VectorRetriever.search(
            db=db,
            query_embedding=query_embedding,
            teacher_id=teacher_id,
            class_id=class_id,
            top_k=top_k,
            chunk_type=chunk_type,
        )

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail="Nenhum chunk relevante encontrado para a consulta",
            )

        return chunks
