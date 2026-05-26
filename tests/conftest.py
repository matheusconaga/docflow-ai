import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, engine
from app.main import app
# IMPORT MODELS
from app.models.document import Document
from app.models.document_structured import DocumentStructured


# CREATE TEST TABLES
@pytest.fixture(scope="session", autouse=True)
def setup_db():

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


# DATABASE SESSION
@pytest.fixture
def db_session():

    Session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = Session()

    try:
        yield db

    finally:
        db.close()


# FASTAPI CLIENT
@pytest.fixture
def client():

    return TestClient(app)


# UPLOAD DOCUMENT
@pytest.fixture
def upload_file(client):

    def _upload(file_path: str, filename: str, content_type: str):

        with open(file_path, "rb") as file:

            response = client.post(
                "/documents/upload", files={"file": (filename, file, content_type)}
            )

        return response

    return _upload


# EXTRACT DOCUMENT
@pytest.fixture
def extract_document(client):

    def _extract(document_id: str):

        response = client.post(f"/documents/{document_id}/extract")

        return response

    return _extract


# STRUCTURE DOCUMENT
@pytest.fixture
def structure_document(client):

    def _structure(document_id: str):

        response = client.post(f"/documents/{document_id}/structure")

        return response

    return _structure
