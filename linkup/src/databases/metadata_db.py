import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

articles_metadata_engine = create_engine(
    f"""sqlite:///{os.getenv("ARTICLES_METADATA_DB_FILE")}""",
    connect_args={"check_same_thread": False},  # arg required for SQLite
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=articles_metadata_engine
)

Base = declarative_base()


# Dependency for getting the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
