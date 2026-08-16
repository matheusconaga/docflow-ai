from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    conn.execute(text("UPDATE documents SET is_deleted = false WHERE is_deleted IS NULL"))
    conn.execute(text("UPDATE classes SET is_deleted = false WHERE is_deleted IS NULL"))
    conn.execute(text("UPDATE students SET is_deleted = false WHERE is_deleted IS NULL"))
    conn.execute(text("UPDATE notifications SET is_deleted = false WHERE is_deleted IS NULL"))
    conn.commit()
print("Nulls fixed!")
