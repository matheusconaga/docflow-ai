from sqlalchemy import text

from app.db.database import SessionLocal, engine, get_db


def test_database_connection():

    connection = engine.connect()

    assert connection.closed is False

    connection.close()


def test_database_session():

    db = SessionLocal()

    result = db.execute(text("SELECT 1"))

    assert result.scalar() == 1

    db.close()


def test_get_db():

    generator = get_db()

    db = next(generator)

    assert db is not None

    db.close()
