
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.document import Document
from app.ai.parsing.extractor import Extractor


class ExtractDocumentService:

    @staticmethod
    def extract_document(
        db: Session,
        document_id: str
    ):

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        extracted_text = Extractor.extract(
            document.file_path
        )

        document.extracted_text = extracted_text

        document.status = "processed"
        
        db.add(document)

        db.commit()

        db.refresh(document)

        return document