#!/usr/bin/env python3
"""
Database Check and Fix Script
This script checks if the jobs table has the required user_email column
and adds it if missing.
"""

import sqlite3
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'jobsify.db')

def check_and_fix_database():
    """Check database schema and fix missing columns"""
    print(f"Checking database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check jobs table columns
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        
        print("\nCurrent jobs table columns:")
        column_names = []
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            column_names.append(col[1])
        
        # Check if user_email column exists
        if 'user_email' not in column_names:
            print("\n⚠️  user_email column is MISSING! Adding it now...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN user_email TEXT DEFAULT 'unknown@example.com'")
            conn.commit()
            print("✅ user_email column added successfully!")
        else:
            print("\n✅ user_email column exists")
        
        # Check other required columns
        required_columns = {
            'verified': 'BOOLEAN DEFAULT 0',
            'urgent': 'BOOLEAN DEFAULT 0',
            'salary': 'TEXT',
            'created_at': 'TEXT'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in column_names:
                print(f"\n⚠️  {col_name} column is MISSING! Adding it now...")
                cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
                conn.commit()
                print(f"✅ {col_name} column added successfully!")
            else:
                print(f"✅ {col_name} column exists")
        
        # Show updated schema
        cursor.execute("PRAGMA table_info(jobs)")
        updated_columns = cursor.fetchall()
        print("\nUpdated jobs table schema:")
        for col in updated_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if there are any jobs without user_email
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_email IS NULL OR user_email = ''")
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            print(f"\n⚠️  Found {null_count} jobs with NULL/empty user_email")
            cursor.execute("UPDATE jobs SET user_email = 'unknown@example.com' WHERE user_email IS NULL OR user_email = ''")
            conn.commit()
            print(f"✅ Updated {null_count} jobs with default user_email")
        
        print("\n✅ Database check and fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = check_and_fix_database()
    exit(0 if success else 1)
