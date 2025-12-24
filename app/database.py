from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#SQLite database URL

DATABASE_URL = "sqllite:///./jobsify.db"

# Create DB Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

#Create session (used in the APis)
SessionLocal = sessionmaker(bind-engine)

# Base  class for models
Base = declarative_base()
