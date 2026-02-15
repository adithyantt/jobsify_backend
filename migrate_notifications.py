import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'jobsify.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns exist
cursor.execute("PRAGMA table_info(notifications)")
columns = [col[1] for col in cursor.fetchall()]

# Add type column if it doesn't exist
if 'type' not in columns:
    print("Adding 'type' column to notifications table...")
    cursor.execute("ALTER TABLE notifications ADD COLUMN type VARCHAR(50) DEFAULT 'general'")
    print("✅ Added 'type' column")

# Add reference_id column if it doesn't exist
if 'reference_id' not in columns:
    print("Adding 'reference_id' column to notifications table...")
    cursor.execute("ALTER TABLE notifications ADD COLUMN reference_id INTEGER")
    print("✅ Added 'reference_id' column")

# Commit changes
conn.commit()
conn.close()

print("\n✅ Database migration completed successfully!")
print("The notifications table now has 'type' and 'reference_id' columns.")
