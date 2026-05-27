from app.db.database import Base, engine
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
from app.models.document_structured import DocumentStructured  # noqa: F401

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
