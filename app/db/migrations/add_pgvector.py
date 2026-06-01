"""
Migration: Enable pgvector and convert embedding column from JSON to vector(3072).

Run once before starting the app:
    python -m app.db.migrations.add_pgvector
"""

import psycopg2

from app.core.config import DATABASE_URL


def run():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("Enabling pgvector extension...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    print("Converting embedding column from JSON to vector(3072)...")
    cur.execute("ALTER TABLE documents_chunks DROP COLUMN IF EXISTS embedding;")
    cur.execute("ALTER TABLE documents_chunks ADD COLUMN embedding vector(3072);")

    print("Migration complete.")
    print("Re-generate embeddings via: POST /documents/{document_id}/embeddings")

    cur.close()
    conn.close()


if __name__ == "__main__":
    run()
