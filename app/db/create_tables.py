from app.db.database import engine, Base
from app.models.document import Document

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")