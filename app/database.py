from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL
DATABASE_URL = "sqlite:///./jobsify.db"

# Create DB Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session (used in APIs)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# ✅ THIS FUNCTION IS REQUIRED  FASTAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
