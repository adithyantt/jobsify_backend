"""
Simple migration script to create reviews table using raw SQL.
"""

import sqlite3
import os

# Database path - same as in database.py
DB_PATH = os.path.join(os.path.dirname(__file__), 'jobsify.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if reviews table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews'")
    if cursor.fetchone():
        print("✅ Reviews table already exists!")
        conn.close()
        return
    
    # Create reviews table
    cursor.execute("""
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
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_reviews_worker_id ON reviews (worker_id)")
    cursor.execute("CREATE INDEX idx_reviews_reviewer_email ON reviews (reviewer_email)")
    
    conn.commit()
    conn.close()
    print("✅ Reviews table created successfully!")
    print("✅ Indexes created on worker_id and reviewer_email")

if __name__ == "__main__":
    migrate()
