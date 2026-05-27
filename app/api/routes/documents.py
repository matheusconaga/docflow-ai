from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.document_chunk_schema import DocumentChunkResponse
from app.schemas.document_embedding_schema import DocumentEmbeddingResponse
# DOCUMENTS SCHEMAS
from app.schemas.document_schema import DocumentResponse
from app.schemas.document_structured_schema import DocumentStructuredResponse
from app.schemas.extract_document_schema import ExtractDocumentResponse
from app.services.document_chunk_service import DocumentChunkService
from app.services.document_embedding_service import DocumentEmbeddingService
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


# ROUTE FOR GENERATING CHUNKS
@router.post("/{document_id}/chunk", response_model=list[DocumentChunkResponse])
def chunk_document(document_id: str, db: Session = Depends(get_db)):

    return DocumentChunkService.chunk_document(db=db, document_id=document_id)


# ROUTE FOR GENERATING EMBEDDINGS
@router.post(
    "/{document_id}/embeddings", response_model=list[DocumentEmbeddingResponse]
)
def generate_embeddings(document_id: str, db: Session = Depends(get_db)):

    return DocumentEmbeddingService.generate_embeddings(
        db=db,
        document_id=document_id,
    )
