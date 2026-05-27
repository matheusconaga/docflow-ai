from fastapi import HTTPException

from app.ai.embeddings.orchestrator.embedding_generator import \
    EmbeddingGenerator
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured


class DocumentEmbeddingService:

    @staticmethod
    def generate_embeddings(db, document_id: str):

        structured_document = (
            db.query(DocumentStructured)
            .filter(DocumentStructured.document_id == document_id)
            .first()
        )

        if not structured_document:
            raise HTTPException(status_code=404, detail="Structured document not found")

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.structured_document_id == structured_document.id)
            .all()
        )

        if not chunks:
            raise HTTPException(status_code=404, detail="Chunks not found")

        for chunk in chunks:

            # SKIP IF EMBEDDING ALREADY EXISTS
            if chunk.embedding:
                continue

            embedding = EmbeddingGenerator.generate(chunk.content)

            chunk.embedding = embedding

        db.commit()

        for chunk in chunks:
            db.refresh(chunk)

        return chunks
