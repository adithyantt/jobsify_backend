import sqlite3
import os

db_path = "jobsify.db"

if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current columns
cursor.execute("PRAGMA table_info(reports)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print("Current columns in reports table:", column_names)

# Add missing columns
columns_to_add = {
    'user_id': 'INTEGER',
    'created_at': 'DATETIME'
}

for col_name, col_type in columns_to_add.items():
    if col_name not in column_names:
        print(f"Adding {col_name} column...")
        cursor.execute(f"ALTER TABLE reports ADD COLUMN {col_name} {col_type}")
        print(f"✅ {col_name} added!")
    else:
        print(f"✓ {col_name} already exists")

conn.commit()
conn.close()
print("\n✅ Database migration complete!")
