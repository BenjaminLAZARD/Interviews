from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# "mysql+pymysql://user:password@localhost:5000/beavr_db" if using a more scalable
# approach with mysql. Here we chose sqlite for the demo (more lightweight)
SQLITE_DB_FILEPATH = "./app_test.db"
DATABASE_URL = f"sqlite:///{SQLITE_DB_FILEPATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # arg required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency for getting the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
