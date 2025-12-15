from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

_connect_args = {}
# Удобно для локальной разработки/тестов на SQLite.
if settings.db_url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(settings.db_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
