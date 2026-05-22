from fastapi import APIRouter
from fastapi import UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.schemas.document_schema import DocumentResponse
from app.services.document_service import DocumentService


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
    file: UploadFile = File(...)
):

    db: Session = SessionLocal()

    document = DocumentService.upload_document(
        db=db,
        file=file
    )

    return document