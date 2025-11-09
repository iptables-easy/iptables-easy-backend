from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Update DATABASE_URL to use psycopg driver instead of psycopg2
# Format: postgresql+psycopg://user:password@host:port/database
database_url = settings.DATABASE_URL
if "postgresql://" in database_url and "postgresql+psycopg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
