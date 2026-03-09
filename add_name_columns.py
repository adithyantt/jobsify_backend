"""
Migration script to add first_name and last_name columns to users and workers tables.
"""
import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), "jobsify.db")

print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current schema
print("\n=== Checking current schema ===")

# Check users table
cursor.execute("PRAGMA table_info(users)")
users_columns = cursor.fetchall()
print("\nUsers table columns:")
for col in users_columns:
    print(f"  - {col[1]} ({col[2]})")

users_column_names = [col[1] for col in users_columns]

# Check workers table
cursor.execute("PRAGMA table_info(workers)")
workers_columns = cursor.fetchall()
print("\nWorkers table columns:")
for col in workers_columns:
    print(f"  - {col[1]} ({col[2]})")

workers_column_names = [col[1] for col in workers_columns]

# Add first_name and last_name to users table if they don't exist
print("\n=== Adding columns to users table ===")
if "first_name" not in users_column_names:
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN first_name VARCHAR(100)")
        print("  Added first_name column")
    except Exception as e:
        print(f"  Error adding first_name: {e}")
else:
    print("  first_name column already exists")

if "last_name" not in users_column_names:
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_name VARCHAR(100)")
        print("  Added last_name column")
    except Exception as e:
        print(f"  Error adding last_name: {e}")
else:
    print("  last_name column already exists")

# Add first_name and last_name to workers table if they don't exist
print("\n=== Adding columns to workers table ===")
if "first_name" not in workers_column_names:
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN first_name VARCHAR(100)")
        print("  Added first_name column")
    except Exception as e:
        print(f"  Error adding first_name: {e}")
else:
    print("  first_name column already exists")

if "last_name" not in workers_column_names:
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN last_name VARCHAR(100)")
        print("  Added last_name column")
    except Exception as e:
        print(f"  Error adding last_name: {e}")
else:
    print("  last_name column already exists")

# Commit changes and close
conn.commit()
conn.close()

print("\n=== Migration complete! ===")
print("Please restart the backend server to apply changes.")
