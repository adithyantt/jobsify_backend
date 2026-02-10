import sqlite3

# Connect to the database
conn = sqlite3.connect('jobsify.db')
cursor = conn.cursor()

# Add missing columns to jobs table
columns_to_add = [
    ("verified", "BOOLEAN DEFAULT 0"),
    ("urgent", "BOOLEAN DEFAULT 0"),
    ("salary", "VARCHAR"),
    ("created_at", "VARCHAR DEFAULT ''")
]

for column_name, column_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}")
        print(f"Column '{column_name}' added successfully to jobs table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column '{column_name}' already exists.")
        else:
            print(f"Error adding column '{column_name}': {e}")

# Commit and close
conn.commit()
conn.close()
