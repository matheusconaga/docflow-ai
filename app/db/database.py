import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_TEST_URL, DATABASE_URL

# USE TEST DATABASE ONLY DURING TESTS
if os.getenv("TESTING") == "true":
    database_url = DATABASE_TEST_URL
else:
    database_url = DATABASE_URL

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
