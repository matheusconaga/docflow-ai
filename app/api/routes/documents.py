from fastapi import APIRouter, UploadFile, File, Depends 
from sqlalchemy.orm import Session

from app.db.database import get_db 

# DOCUMENTS SCHEMAS
from app.schemas.document_schema import DocumentResponse
from app.schemas.extract_document_schema import ExtractDocumentResponse

# DOCUMENTS SERVICES
from app.services.document_service import DocumentService
from app.services.extract_document_service import ExtractDocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# ROUTE FOR UPLOADING A DOCUMENT, RECEIVING THE FILE, SAVING IT IN THE FILE SYSTEM 
# AND CREATING THE DOCUMENT RECORD IN THE DATABASE, RETURNING THE CREATED DOCUMENT AS RESPONSE
@router.post(
    "/upload",
    response_model=DocumentResponse
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db) 
):
    document = await DocumentService.upload_document(
        db=db,
        file=file
    )

    return document

# ROUTE FOR EXTRACTING TEXT FROM A DOCUMENT, RECEIVING THE DOCUMENT ID, EXTRACTING THE TEXT USING THE EXTRACTOR MODULE, 
# UPDATING THE DOCUMENT RECORD IN THE DATABASE WITH THE EXTRACTED TEXT AND RETURNING THE UPDATED DOCUMENT AS RESPONSE

@router.post(
    "/{document_id}/extract",
    response_model=ExtractDocumentResponse
)
def extract_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = (
        ExtractDocumentService.extract_document(
            db=db,
            document_id=document_id
        )
    )

    return document