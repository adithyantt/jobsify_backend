#!/usr/bin/env python3
"""
Add availability columns to workers table
"""
import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), "jobsify.db")

def add_availability_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(workers)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add availability_type column if not exists
    if "availability_type" not in columns:
        print("Adding availability_type column...")
        cursor.execute("""
            ALTER TABLE workers 
            ADD COLUMN availability_type TEXT DEFAULT 'everyday'
        """)
        print("✅ availability_type column added")
    else:
        print("ℹ️ availability_type column already exists")
    
    # Add available_days column if not exists
    if "available_days" not in columns:
        print("Adding available_days column...")
        cursor.execute("""
            ALTER TABLE workers 
            ADD COLUMN available_days TEXT
        """)
        print("✅ available_days column added")
    else:
        print("ℹ️ available_days column already exists")
    
    conn.commit()
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    add_availability_columns()
