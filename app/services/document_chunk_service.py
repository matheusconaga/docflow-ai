from fastapi import HTTPException

from app.ai.chunking.orchestrator.document_chunker import DocumentChunker
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured


class DocumentChunkService:

    @staticmethod
    def chunk_document(db, document_id: str):

        structured_document = (
            db.query(DocumentStructured)
            .filter(DocumentStructured.document_id == document_id)
            .first()
        )

        if not structured_document:
            raise HTTPException(status_code=404, detail="Structured document not found")

        # VERIFY IF CHUNKS ALREADY EXIST
        existing_chunk = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.structured_document_id == structured_document.id)
            .first()
        )

        if existing_chunk:
            raise HTTPException(status_code=400, detail="Chunks already generated")

        chunks_data = DocumentChunker.generate_all_chunks(structured_document)

        created_chunks = []

        for index, chunk_data in enumerate(chunks_data):

            chunk = DocumentChunk(
                structured_document_id=structured_document.id,
                chunk_type=chunk_data["chunk_type"],
                chunk_order=index,
                content=chunk_data["content"],
                chunk_metadata=chunk_data.get("chunk_metadata"),
            )

            db.add(chunk)

            created_chunks.append(chunk)

        db.commit()

        for chunk in created_chunks:
            db.refresh(chunk)

        return created_chunks
