import sqlite3

def add_phone_column():
    conn = sqlite3.connect('jobsify.db')
    cursor = conn.cursor()

    # Check if phone column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'phone' not in columns:
        # Add phone column
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        print("Phone column added to users table")
    else:
        print("Phone column already exists")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_phone_column()
