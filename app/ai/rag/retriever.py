from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured
from app.models.document import Document


class VectorRetriever:

    @staticmethod
    def search(
        db: Session,
        query_embedding: list[float],
        teacher_id: str,
        class_id: str | None = None,
        top_k: int = 5,
        chunk_type: str | None = None,
    ) -> list[DocumentChunk]:
        
        # Build the security filter condition
        security_condition = and_(Document.class_id.is_(None), Document.teacher_id == teacher_id)
        if class_id:
            security_condition = or_(Document.class_id == class_id, security_condition)
            
        query = db.query(DocumentChunk).join(
            DocumentStructured, DocumentChunk.structured_document_id == DocumentStructured.id
        ).join(
            Document, DocumentStructured.document_id == Document.id
        ).filter(
            DocumentChunk.embedding.isnot(None),
            security_condition
        )

        if chunk_type:
            query = query.filter(DocumentChunk.chunk_type == chunk_type)

        results = (
            query.order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )

        return results
