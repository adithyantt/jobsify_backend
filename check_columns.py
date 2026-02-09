import sqlite3

def check_columns():
    conn = sqlite3.connect('jobsify.db')
    cursor = conn.cursor()

    # Get column info for users table
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()

    print("Users table columns:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")

    conn.close()

if __name__ == "__main__":
    check_columns()
