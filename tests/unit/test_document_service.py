from app.services.document_service import (
    DocumentService
)


def test_allowed_extensions():

    assert ".pdf" in (
        DocumentService.ALLOWED_EXTENSIONS
    )

    assert ".png" in (
        DocumentService.ALLOWED_EXTENSIONS
    )


def test_allowed_mime_types():

    assert (
        "application/pdf"
        in DocumentService.ALLOWED_MIME_TYPES
    )

    assert (
        "image/png"
        in DocumentService.ALLOWED_MIME_TYPES
    )


def test_max_file_size():

    assert (
        DocumentService.MAX_FILE_SIZE
        == 10 * 1024 * 1024
    )