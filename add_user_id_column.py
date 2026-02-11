import sqlite3
import os

db_path = "jobsify.db"

if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if user_id column exists
cursor.execute("PRAGMA table_info(reports)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

if 'user_id' in column_names:
    print("user_id column already exists!")
else:
    print("Adding user_id column to reports table...")
    cursor.execute("ALTER TABLE reports ADD COLUMN user_id INTEGER")
    conn.commit()
    print("Column added successfully!")

conn.close()
print("Done!")
