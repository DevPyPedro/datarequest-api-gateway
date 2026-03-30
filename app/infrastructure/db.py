from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """
    Initialize database structures required by the application.
    Creates schema and mapped tables when they do not exist.
    """
    # Ensure mapped models are imported before create_all.
    from app.domain.entities.users import User  # noqa: F401

    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS user_auth"))

    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency to get a database session.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
