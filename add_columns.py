import sys
sys.path.append("/app")

from sqlalchemy import text
from app.db.database import SessionLocal

def add_columns():
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS school VARCHAR(255);"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS position VARCHAR(255);"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS subject VARCHAR(255);"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS grade VARCHAR(255);"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS specialties VARCHAR(500);"))
        db.commit()
        print("Colunas adicionadas com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()
