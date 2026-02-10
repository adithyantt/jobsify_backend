import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('jobsify.db')
cursor = conn.cursor()

# Update jobs where created_at is NULL or empty
current_time = datetime.now().isoformat()
cursor.execute("""
    UPDATE jobs
    SET created_at = ?
    WHERE created_at IS NULL OR created_at = ''
""", (current_time,))

# Check how many were updated
updated_count = cursor.rowcount
print(f"Updated {updated_count} jobs with created_at")

# Commit and close
conn.commit()
conn.close()

print("Database fix completed.")
