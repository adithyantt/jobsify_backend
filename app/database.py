import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL - use absolute path to avoid issues
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), '../jobsify.db')}"

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

# 👇 IMPORT ALL MODELS SO SQLAlchemy KNOWS THEM
from app.models.user import User
from app.models.job import Job
from app.models.workers import Worker
from app.models.report import Report

# 👇 CREATE TABLES
Base.metadata.create_all(bind=engine)
