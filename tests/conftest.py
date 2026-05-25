import pytest
from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app
from app.models.document import Document


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def upload_file(client):
    def _upload(file_path: str, filename: str, content_type: str):
        with open(file_path, "rb") as file:
            response = client.post(
                "/documents/upload", files={"file": (filename, file, content_type)}
            )
        return response

    return _upload


@pytest.fixture
def extract_document(client):
    def _extract(document_id: str):
        response = client.post(f"/documents/{document_id}/extract")
        return response

    return _extract
