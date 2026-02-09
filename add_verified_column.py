import sqlite3

# Connect to the database
conn = sqlite3.connect('jobsify.db')
cursor = conn.cursor()

# Add the 'verified' column to the users table
try:
    cursor.execute("ALTER TABLE users ADD COLUMN verified BOOLEAN DEFAULT 0")
    print("Column 'verified' added successfully to users table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'verified' already exists.")
    else:
        print(f"Error adding column: {e}")

# Commit and close
conn.commit()
conn.close()
