import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.notification_model import NotificationModel
from app.db.database import SessionLocal
from app.services.extract_document_service import ExtractDocumentService
from app.services.document_structured_service import DocumentStructuredService
from app.services.document_chunk_service import DocumentChunkService
from app.services.document_embedding_service import DocumentEmbeddingService

# DIRECTORY RESPONSIBLE FOR STORING UPLOADED FILES
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"


class DocumentService:

    # ALLOWED FILE EXTENSIONS
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".png", ".jpg", ".jpeg"]

    # ALLOWED MIME TYPES
    ALLOWED_MIME_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg",
    ]

    # MAXIMUM FILE SIZE (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @staticmethod
    async def upload_document(db: Session, file: UploadFile, teacher_id: str, class_id: str | None = None):

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # GET FILE EXTENSION
        file_extension = Path(file.filename).suffix.lower()

        # VALIDATE EXTENSION
        if file_extension not in DocumentService.ALLOWED_EXTENSIONS:

            raise HTTPException(status_code=400, detail="Invalid file extension")

        # VALIDATE MIME TYPE
        if file.content_type not in DocumentService.ALLOWED_MIME_TYPES:

            raise HTTPException(status_code=400, detail="Invalid MIME type")

        # READ FILE CONTENT
        file_content = await file.read()

        # VALIDATE FILE SIZE
        if len(file_content) > DocumentService.MAX_FILE_SIZE:

            raise HTTPException(
                status_code=400, detail="File exceeds maximum size of 10MB"
            )

        # GENERATE UNIQUE FILENAME
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        file_path = f"{UPLOAD_DIR}/{unique_filename}"

        # SAVE FILE
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # CREATE DOCUMENT RECORD
        db_document = Document(
            filename=file.filename,
            stored_filename=unique_filename,
            file_path=file_path,
            teacher_id=teacher_id,
            class_id=class_id,
            status="uploaded",
        )

        db.add(db_document)

        db.commit()

        db.refresh(db_document)

        return db_document

    @staticmethod
    def process_document_pipeline(document_id: str, teacher_id: str):
        db = SessionLocal()
        try:
            # 1. Extract text
            ExtractDocumentService.extract_document(db=db, document_id=document_id)
            
            # 2. Structure text
            DocumentStructuredService.structure_document(db=db, document_id=document_id)
            
            # 3. Chunk text
            DocumentChunkService.chunk_document(db=db, document_id=document_id)
            
            # 4. Generate Embeddings
            DocumentEmbeddingService.generate_embeddings(db=db, document_id=document_id)

            # Update status to processed
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "processed"
                
                # Create Success Notification
                notification = NotificationModel(
                    user_id=teacher_id,
                    title="Documento Processado",
                    message=f"O documento '{doc.filename}' foi processado e já pode ser lido pela Inteligência Artificial.",
                    type="success"
                )
                db.add(notification)
                
            db.commit()

        except Exception as e:
            # Update status to error
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "error"
                
                # Create Error Notification
                notification = NotificationModel(
                    user_id=teacher_id,
                    title="Erro no Processamento",
                    message=f"Houve um erro ao processar o documento '{doc.filename}'. Detalhes: {str(e)}",
                    type="error"
                )
                db.add(notification)
                
            db.commit()
            print(f"Failed to process document {document_id}: {str(e)}")
        finally:
            db.close()
