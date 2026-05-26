from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.models.document import Document
from app.models.document_structured import DocumentStructured
from app.services.document_structured_service import DocumentStructuredService


class TestDocumentStructuredService:

    @patch("app.services.document_structured_service.DocumentStructurer.structure")
    def test_should_structure_document_successfully(
        self,
        mock_structure,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="processed",
            extracted_text="Texto extraído do documento",
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        mock_structure.return_value = {
            "subject": "Ensino Religioso",
            "level": "1º Ano",
            "contents": ["Sentimentos", "Memórias"],
            "skills": [{"code": "EF01ER05", "description": "Identificar sentimentos"}],
            "methodologies": ["Roda de conversa"],
            "assessment": ["Participação"],
        }

        result = DocumentStructuredService.structure_document(
            db=db_session, document_id=document.id
        )

        assert result.subject == "Ensino Religioso"
        assert result.level == "1º Ano"

        updated_document = (
            db_session.query(Document).filter(Document.id == document.id).first()
        )

        assert updated_document.status == "structured"

    def test_should_raise_404_when_document_not_found(
        self,
        db_session,
    ):

        with pytest.raises(HTTPException) as exc:
            DocumentStructuredService.structure_document(
                db=db_session, document_id="invalid-id"
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Document not found"

    def test_should_raise_error_when_document_not_processed(
        self,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="uploaded",
            extracted_text="Texto",
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        with pytest.raises(HTTPException) as exc:
            DocumentStructuredService.structure_document(
                db=db_session, document_id=document.id
            )

        assert exc.value.status_code == 400

    def test_should_raise_error_when_document_has_no_text(
        self,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="processed",
            extracted_text=None,
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        with pytest.raises(HTTPException) as exc:
            DocumentStructuredService.structure_document(
                db=db_session, document_id=document.id
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Document has no extracted text"

    def test_should_raise_error_when_document_already_structured(
        self,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="structured",
            extracted_text="Texto",
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        structured = DocumentStructured(
            document_id=document.id,
            subject="Matemática",
            level="1º Ano",
            contents=["Números"],
            skills=[],
            methodologies=[],
            assessment=[],
        )

        db_session.add(structured)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:

            DocumentStructuredService.structure_document(
                db=db_session,
                document_id=document.id,
            )

        assert exc.value.status_code == 400

        assert exc.value.detail == "Document already structured"

    def test_should_raise_error_when_structure_already_exists(
        self,
        db_session,
    ):

        document = Document(
            filename="test.pdf",
            stored_filename="test.pdf",
            file_path="/tmp/test.pdf",
            status="processed",
            extracted_text="Texto",
        )

        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        structured = DocumentStructured(
            document_id=document.id,
            subject="Português",
            level="1º Ano",
            contents=["Conteúdo"],
            skills=[],
            methodologies=[],
            assessment=[],
        )

        db_session.add(structured)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            DocumentStructuredService.structure_document(
                db=db_session, document_id=document.id
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Document already structured"
