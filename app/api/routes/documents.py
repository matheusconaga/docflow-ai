from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
# DOCUMENTS SCHEMAS
from app.schemas.document_schema import DocumentResponse
from app.schemas.document_structured_schema import DocumentStructuredResponse
from app.schemas.extract_document_schema import ExtractDocumentResponse
# DOCUMENTS SERVICES
from app.services.document_service import DocumentService
from app.services.document_structured_service import DocumentStructuredService
from app.services.extract_document_service import ExtractDocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


# ROUTE FOR UPLOADING A DOCUMENT
# RECEIVES FILE, SAVES IT
# CREATES DOCUMENT RECORD
@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    document = await DocumentService.upload_document(db=db, file=file)

    return document


# ROUTE FOR EXTRACTING TEXT
# RECEIVES DOCUMENT ID
# EXTRACTS TEXT
# UPDATES DOCUMENT RECORD
@router.post("/{document_id}/extract", response_model=(ExtractDocumentResponse))
def extract_document(document_id: str, db: Session = Depends(get_db)):
    document = ExtractDocumentService.extract_document(db=db, document_id=document_id)

    return document


# ROUTE FOR STRUCTURE EXTRACT_TEXT


@router.post("/{document_id}/structure", response_model=DocumentStructuredResponse)
def structure_document(document_id: str, db: Session = Depends(get_db)):
    return DocumentStructuredService.structure_document(db=db, document_id=document_id)
