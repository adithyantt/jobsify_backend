import sqlite3
import os

# Get the correct database path
db_path = os.path.join(os.path.dirname(__file__), 'jobsify.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add the 'urgent' column to the jobs table
try:
    cursor.execute("ALTER TABLE jobs ADD COLUMN urgent BOOLEAN DEFAULT 0")
    print("Column 'urgent' added successfully to jobs table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'urgent' already exists.")
    else:
        print(f"Error adding column: {e}")

# Commit and close
conn.commit()
conn.close()
