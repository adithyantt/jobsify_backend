import sqlite3
import os

# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), 'jobsify.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fix jobs table - invalid categories
print("Fixing jobs table categories...")
cursor.execute("SELECT id, category FROM jobs")
jobs = cursor.fetchall()
for job_id, category in jobs:
    if category == "Plumbing":
        cursor.execute("UPDATE jobs SET category = ? WHERE id = ?", ("Plumber", job_id))
        print(f"  Job {job_id}: Plumbing -> Plumber")
    elif category == "Cleaning":
        cursor.execute("UPDATE jobs SET category = ? WHERE id = ?", ("Cleaner", job_id))
        print(f"  Job {job_id}: Cleaning -> Cleaner")

# Fix jobs table - short descriptions
print("\nFixing jobs table descriptions...")
cursor.execute("SELECT id, description FROM jobs")
jobs = cursor.fetchall()
for job_id, description in jobs:
    if description and len(description) < 10:
        # Pad the description to meet minimum requirement
        new_desc = description + " Service provided"
        cursor.execute("UPDATE jobs SET description = ? WHERE id = ?", (new_desc, job_id))
        print(f"  Job {job_id}: '{description}' -> '{new_desc}'")

# Fix workers table - invalid roles
print("\nFixing workers table roles...")
cursor.execute("SELECT id, role FROM workers")
workers = cursor.fetchall()
for worker_id, role in workers:
    role_lower = role.lower() if role else ""
    if role_lower == "plumbing":
        cursor.execute("UPDATE workers SET role = ? WHERE id = ?", ("Plumber", worker_id))
        print(f"  Worker {worker_id}: plumbing -> Plumber")
    elif role_lower == "painting" or role_lower == "painter":
        cursor.execute("UPDATE workers SET role = ? WHERE id = ?", ("Painter", worker_id))
        print(f"  Worker {worker_id}: {role} -> Painter")
    elif role_lower == "cleaning" or role_lower == "cleaner":
        cursor.execute("UPDATE workers SET role = ? WHERE id = ?", ("Cleaner", worker_id))
        print(f"  Worker {worker_id}: {role} -> Cleaner")
    elif role_lower == "driver":
        cursor.execute("UPDATE workers SET role = ? WHERE id = ?", ("Driver", worker_id))
        print(f"  Worker {worker_id}: driver -> Driver")
    elif role_lower == "electrician":
        cursor.execute("UPDATE workers SET role = ? WHERE id = ?", ("Electrician", worker_id))
        print(f"  Worker {worker_id}: electrician -> Electrician")
    elif role_lower == "carpenter":
        cursor.execute("UPDATE workers SET role = ? WHERE id = ?", ("Carpenter", worker_id))
        print(f"  Worker {worker_id}: carpenter -> Carpenter")

conn.commit()
print("\n✅ Database migration completed successfully!")
conn.close()
