from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


class VectorRetriever:

    @staticmethod
    def search(
        db: Session,
        query_embedding: list[float],
        top_k: int = 5,
        chunk_type: str | None = None,
    ) -> list[DocumentChunk]:
        query = db.query(DocumentChunk).filter(DocumentChunk.embedding.isnot(None))

        if chunk_type:
            query = query.filter(DocumentChunk.chunk_type == chunk_type)

        results = (
            query.order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )

        return results
