import sys
sys.path.append("/app")

from sqlalchemy import text
from app.db.database import SessionLocal

def add_columns():
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);"))
        db.commit()
        print("Coluna avatar_url adicionada com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()
