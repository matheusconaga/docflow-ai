from app.db.database import Base, engine
from app.models.document import Document  # noqa: F401

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
