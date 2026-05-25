from fastapi import HTTPException
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.ai.parsing.extractor import Extractor
from app.models.document import Document


class ExtractDocumentService:

    @staticmethod
    def extract_document(db: Session, document_id: str):

        # ADD CAST FOR NEON RECOGNIZE ID=STR LIKE VIABLE
        document = (
            db.query(Document)
            .filter(cast(Document.id, String) == cast(document_id, String))
            .first()
        )

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        extracted_text = Extractor.extract(document.file_path)

        document.extracted_text = extracted_text
        document.status = "processed"

        db.add(document)
        db.commit()
        db.refresh(document)

        return document
