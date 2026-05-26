from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.structuring.document_structurer import DocumentStructurer
from app.models.document import Document
from app.models.document_structured import DocumentStructured


class DocumentStructuredService:

    @staticmethod
    def structure_document(db: Session, document_id: str):

        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # VERIFY IF STRUCTURE ALREADY EXISTS
        existing_structure = (
            db.query(DocumentStructured)
            .filter(DocumentStructured.document_id == document.id)
            .first()
        )

        if existing_structure:
            raise HTTPException(status_code=400, detail="Document already structured")

        # MUST BE PROCESSED
        if document.status != "processed":
            raise HTTPException(
                status_code=400, detail="Document must be processed before extracting"
            )

        # MUST HAVE EXTRACTED TEXT
        if not document.extracted_text:
            raise HTTPException(
                status_code=400, detail="Document has no extracted text"
            )

        structured_data = DocumentStructurer.structure(document.extracted_text)

        structured_document = DocumentStructured(
            document_id=document.id,
            subject=structured_data["subject"],
            level=structured_data["level"],
            contents=structured_data["contents"],
            skills=structured_data["skills"],
            methodologies=structured_data["methodologies"],
            assessment=structured_data["assessment"],
        )

        db.add(structured_document)

        # UPDATE DOCUMENT STATUS
        document.status = "structured"

        db.commit()

        db.refresh(structured_document)

        return structured_document
