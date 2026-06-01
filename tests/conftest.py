import os

os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app

# IMPORT MODELS
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_structured import DocumentStructured

# TEST DATABASE
TEST_DATABASE_URL = os.getenv("DATABASE_TEST_URL")

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# CREATE TEST TABLES
@pytest.fixture(scope="session", autouse=True)
def setup_db():

    # ENABLE PGVECTOR
    with test_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


# DATABASE SESSION
@pytest.fixture
def db_session():

    connection = test_engine.connect()

    transaction = connection.begin()

    db = TestingSessionLocal(bind=connection)

    try:
        yield db

    finally:
        db.close()
        transaction.rollback()
        connection.close()


# OVERRIDE FASTAPI DB
@pytest.fixture(autouse=True)
def override_get_db(db_session):

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    yield

    app.dependency_overrides.clear()


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
                "/documents/upload",
                files={"file": (filename, file, content_type)},
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


# CHUNK DOCUMENT
@pytest.fixture
def chunk_document(client):

    def _chunk(document_id: str):

        response = client.post(f"/documents/{document_id}/chunk")

        return response

    return _chunk