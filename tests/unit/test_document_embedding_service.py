from unittest.mock import patch

import pytest

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured
from app.services.document_embedding_service import DocumentEmbeddingService


class TestDocumentEmbeddingService:

    @patch(
        "app.ai.embeddings.orchestrator.embedding_generator.EmbeddingGenerator.generate"
    )
    def test_should_generate_embeddings(
        self,
        mock_generate,
        db_session,
    ):

        mock_generate.return_value = [0.1] * 3072

        document = Document(
            filename="lesson-plan.pdf",
            stored_filename="lesson-plan.pdf",
            file_path="/tmp/lesson-plan.pdf",
            status="processed",
            extracted_text="Texto pedagógico extraído",
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        structured = DocumentStructured(
            document_id=document.id,
            subject="Math",
            level="5th Grade",
            contents=["Fractions"],
            skills=[],
            methodologies=[],
            assessment=[],
        )

        db_session.add(structured)
        db_session.commit()
        db_session.refresh(structured)

        chunk = DocumentChunk(
            structured_document_id=structured.id,
            chunk_type="lesson_plan",
            chunk_order=0,
            content="Chunk content",
        )

        db_session.add(chunk)
        db_session.commit()

        result = DocumentEmbeddingService.generate_embeddings(
            db=db_session,
            document_id=document.id,
        )

        assert len(result) == 1
        assert len(result[0].embedding) == 3072
        assert result[0].embedding[0] == pytest.approx(0.1)