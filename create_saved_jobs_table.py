#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def create_saved_jobs_table():
    """Create the saved_jobs table in the database."""

    # Connect to the database
    conn = sqlite3.connect('jobsify.db')
    cursor = conn.cursor()

    try:
        # Create saved_jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                job_id INTEGER NOT NULL,
                saved_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                UNIQUE(user_email, job_id)
            )
        ''')

        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_email ON saved_jobs(user_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_saved_jobs_job_id ON saved_jobs(job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_saved_jobs_saved_at ON saved_jobs(saved_at)')

        conn.commit()
        print("✅ Saved jobs table created successfully!")

    except Exception as e:
        print(f"❌ Error creating saved jobs table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_saved_jobs_table()
