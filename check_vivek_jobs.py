import sqlite3

# Connect to the database
conn = sqlite3.connect('jobsify.db')
cursor = conn.cursor()

# Check jobs for the specific email
email = 'vivekkrishna960@gmail.com'
cursor.execute('SELECT * FROM jobs WHERE user_email = ?', (email,))
jobs = cursor.fetchall()

print(f"Jobs for {email}: {len(jobs)}")
for job in jobs:
    print(job)

# Also check all jobs to see the structure
cursor.execute('SELECT COUNT(*) FROM jobs')
total_jobs = cursor.fetchone()[0]
print(f"\nTotal jobs in database: {total_jobs}")

# Check distinct emails
cursor.execute('SELECT DISTINCT user_email FROM jobs')
emails = cursor.fetchall()
print(f"\nDistinct user emails in jobs table: {emails}")

conn.close()
