import sqlite3

def check_jobs_schema():
    conn = sqlite3.connect('jobsify.db')
    cursor = conn.cursor()

    # Get column info for jobs table
    cursor.execute("PRAGMA table_info(jobs)")
    columns = cursor.fetchall()

    print("Jobs table columns:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")

    conn.close()

if __name__ == "__main__":
    check_jobs_schema()
