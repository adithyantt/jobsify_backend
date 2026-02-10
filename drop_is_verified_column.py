#!/usr/bin/env python3
"""
Script to drop the is_verified column from the jobs table
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'jobsify.db')

def drop_is_verified_column():
    print("Dropping is_verified column from jobs table...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all data from jobs table
        cursor.execute("SELECT id, title, category, description, location, phone, latitude, longitude, user_email, verified, urgent, salary, created_at FROM jobs")
        jobs_data = cursor.fetchall()

        print(f"Found {len(jobs_data)} jobs in database")

        # Create new table without is_verified column
        cursor.execute("""
            CREATE TABLE jobs_new (
                id INTEGER PRIMARY KEY,
                title VARCHAR NOT NULL,
                category VARCHAR NOT NULL,
                description VARCHAR NOT NULL,
                location VARCHAR NOT NULL,
                phone VARCHAR NOT NULL,
                latitude VARCHAR,
                longitude VARCHAR,
                user_email TEXT NOT NULL,
                verified BOOLEAN DEFAULT 0,
                urgent BOOLEAN DEFAULT 0,
                salary VARCHAR,
                created_at VARCHAR
            )
        """)

        # Insert data into new table
        cursor.executemany("""
            INSERT INTO jobs_new (id, title, category, description, location, phone, latitude, longitude, user_email, verified, urgent, salary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, jobs_data)

        # Drop old table
        cursor.execute("DROP TABLE jobs")

        # Rename new table
        cursor.execute("ALTER TABLE jobs_new RENAME TO jobs")

        conn.commit()
        print("✅ Successfully dropped is_verified column")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

    return True

if __name__ == "__main__":
    success = drop_is_verified_column()
    exit(0 if success else 1)
