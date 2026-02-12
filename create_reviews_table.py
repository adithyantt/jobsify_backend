"""
Script to create the reviews table in the database.
Run this after updating the models.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL - same as in database.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobsify.db")

def create_reviews_table():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Create reviews table
    with engine.connect() as conn:
        # Check if table already exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'"))
        if result.fetchone():
            print("Reviews table already exists!")
            return
        
        # Create the reviews table
        conn.execute(text("""
            CREATE TABLE reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                reviewer_email VARCHAR NOT NULL,
                reviewer_name VARCHAR,
                rating INTEGER NOT NULL,
                comment VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers (id)
            )
        """))
        
        # Create index on worker_id for faster queries
        conn.execute(text("""
            CREATE INDEX idx_reviews_worker_id ON reviews (worker_id)
        """))
        
        # Create index on reviewer_email
        conn.execute(text("""
            CREATE INDEX idx_reviews_reviewer_email ON reviews (reviewer_email)
        """))
        
        conn.commit()
        print("✅ Reviews table created successfully!")
        print("✅ Indexes created on worker_id and reviewer_email")

if __name__ == "__main__":
    create_reviews_table()
