"""
Migration script to add new columns to jobs table:
- required_workers
- hired_count
- is_hidden
"""
import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), "jobsify.db")
    print(f"Database path: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add required_workers column
    if "required_workers" not in columns:
        print("Adding required_workers column...")
        cursor.execute("ALTER TABLE jobs ADD COLUMN required_workers INTEGER DEFAULT 1")
    else:
        print("required_workers column already exists")
    
    # Add hired_count column
    if "hired_count" not in columns:
        print("Adding hired_count column...")
        cursor.execute("ALTER TABLE jobs ADD COLUMN hired_count INTEGER DEFAULT 0")
    else:
        print("hired_count column already exists")
    
    # Add is_hidden column
    if "is_hidden" not in columns:
        print("Adding is_hidden column...")
        cursor.execute("ALTER TABLE jobs ADD COLUMN is_hidden INTEGER DEFAULT 0")
    else:
        print("is_hidden column already exists")
    
    conn.commit()
    
    # Verify columns were added
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Updated columns: {columns}")
    
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
