from fastapi import HTTPException
import pytest

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured
from app.services.document_chunk_service import DocumentChunkService


class TestDocumentChunkService:

    def test_should_generate_chunks(
        self,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="structured",
            extracted_text="Texto"
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        structured = DocumentStructured(
            document_id=document.id,
            subject="Educação Física",
            level="1º Ano",
            contents=["Danças"],
            skills=[
                {
                    "code": "EF01",
                    "description": "Experimentar movimentos"
                }
            ],
            methodologies=["Aulas práticas"],
            assessment=["Participação"],
        )

        db_session.add(structured)
        db_session.commit()
        db_session.refresh(structured)

        chunks = DocumentChunkService.chunk_document(
            db=db_session,
            document_id=document.id,
        )

        assert len(chunks) > 0

        assert chunks[0].structured_document_id == structured.id

    def test_should_not_duplicate_chunks(
        self,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="structured",
            extracted_text="Texto"
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        structured = DocumentStructured(
            document_id=document.id,
            subject="Educação Física",
            level="1º Ano",
            contents=["Danças"],
            skills=[
                {
                    "code": "EF01",
                    "description": "Experimentar movimentos"
                }
            ],
            methodologies=["Aulas práticas"],
            assessment=["Participação"],
        )

        db_session.add(structured)
        db_session.commit()
        db_session.refresh(structured)

        # FIRST GENERATION
        DocumentChunkService.chunk_document(
            db=db_session,
            document_id=document.id,
        )

        # SECOND GENERATION MUST FAIL
        with pytest.raises(HTTPException) as exc:

            DocumentChunkService.chunk_document(
                db=db_session,
                document_id=document.id,
            )

        assert exc.value.status_code == 400

        assert exc.value.detail == "Chunks already generated"