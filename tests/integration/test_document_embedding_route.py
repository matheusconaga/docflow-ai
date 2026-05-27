from unittest.mock import patch

class TestDocumentEmbeddingRoute:

    @patch(
        "app.ai.embeddings.orchestrator.embedding_generator.EmbeddingGenerator.generate"
    )
    def test_should_generate_embeddings_route(
        self,
        mock_generate,
        client,
        db_session,
    ):

        mock_generate.return_value = [0.1, 0.2, 0.3]

        from app.models.document import Document
        from app.models.document_chunk import DocumentChunk
        from app.models.document_structured import DocumentStructured

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

        response = client.post(
            f"/documents/{document.id}/embeddings"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["embedding"] == [0.1, 0.2, 0.3]