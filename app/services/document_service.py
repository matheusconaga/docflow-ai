import os
import uuid

from pathlib import Path

from fastapi import (
    UploadFile,
    HTTPException
)

from sqlalchemy.orm import Session
from app.models.document import Document


# DIRECTORY RESPONSIBLE FOR STORING UPLOADED FILES
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"


class DocumentService:

    # ALLOWED FILE EXTENSIONS
    ALLOWED_EXTENSIONS = [
        ".pdf",
        ".docx",
        ".png",
        ".jpg",
        ".jpeg"
    ]

    # ALLOWED MIME TYPES
    ALLOWED_MIME_TYPES = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg"
    ]

    # MAXIMUM FILE SIZE (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @staticmethod
    async def upload_document(
        db: Session,
        file: UploadFile
    ):

        os.makedirs(
            UPLOAD_DIR,
            exist_ok=True
        )

        # GET FILE EXTENSION
        file_extension = (
            Path(file.filename)
            .suffix
            .lower()
        )

        # VALIDATE EXTENSION
        if (
            file_extension
            not in DocumentService.ALLOWED_EXTENSIONS
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid file extension"
            )

        # VALIDATE MIME TYPE
        if (
            file.content_type
            not in DocumentService.ALLOWED_MIME_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid MIME type"
            )

        # READ FILE CONTENT
        file_content = await file.read()

        # VALIDATE FILE SIZE
        if (
            len(file_content)
            > DocumentService.MAX_FILE_SIZE
        ):

            raise HTTPException(
                status_code=400,
                detail="File exceeds maximum size of 10MB"
            )

        # GENERATE UNIQUE FILENAME
        unique_filename = (
            f"{uuid.uuid4()}{file_extension}"
        )

        file_path = (
            f"{UPLOAD_DIR}/{unique_filename}"
        )

        # SAVE FILE
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # CREATE DOCUMENT RECORD
        document = Document(
            filename=file.filename,
            stored_filename=unique_filename,
            file_path=file_path,
            status="uploaded"
        )

        db.add(document)

        db.commit()

        db.refresh(document)

        return document