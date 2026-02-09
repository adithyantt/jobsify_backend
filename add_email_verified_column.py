import sqlite3

# Connect to the database
conn = sqlite3.connect('jobsify.db')
cursor = conn.cursor()

# Add the 'email_verified' column to the users table
try:
    cursor.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0")
    print("Column 'email_verified' added successfully to users table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'email_verified' already exists.")
    else:
        print(f"Error adding column: {e}")

# Commit and close
conn.commit()
conn.close()
