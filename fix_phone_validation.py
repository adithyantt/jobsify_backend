"""
Fix script to correct invalid phone numbers in the database.
The phone numbers have 11 digits but should have 10 digits.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "jobsify.db")

def fix_phone_numbers():
    """Fix phone numbers that are not exactly 10 digits."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    fixed_count = 0
    
    # Fix jobs table
    print("\n=== Fixing jobs table ===")
    cursor.execute("SELECT id, phone FROM jobs WHERE phone IS NOT NULL")
    jobs = cursor.fetchall()
    
    for job_id, phone in jobs:
        if phone:
            # Remove any non-digit characters
            phone_clean = ''.join(c for c in str(phone) if c.isdigit())
            
            if len(phone_clean) != 10:
                print(f"Job {job_id}: '{phone}' -> '{phone_clean}' (length: {len(phone_clean)})")
                
                # Take the last 10 digits (most likely to be the correct number)
                if len(phone_clean) > 10:
                    phone_clean = phone_clean[-10:]
                    print(f"  -> Taking last 10 digits: '{phone_clean}'")
                
                cursor.execute("UPDATE jobs SET phone = ? WHERE id = ?", (phone_clean, job_id))
                fixed_count += 1
    
    # Fix workers table
    print("\n=== Fixing workers table ===")
    cursor.execute("SELECT id, phone FROM workers WHERE phone IS NOT NULL")
    workers = cursor.fetchall()
    
    for worker_id, phone in workers:
        if phone:
            phone_clean = ''.join(c for c in str(phone) if c.isdigit())
            
            if len(phone_clean) != 10:
                print(f"Worker {worker_id}: '{phone}' -> '{phone_clean}' (length: {len(phone_clean)})")
                
                if len(phone_clean) > 10:
                    phone_clean = phone_clean[-10:]
                    print(f"  -> Taking last 10 digits: '{phone_clean}'")
                
                cursor.execute("UPDATE workers SET phone = ? WHERE id = ?", (phone_clean, worker_id))
                fixed_count += 1
    
    # Fix users table
    print("\n=== Fixing users table ===")
    cursor.execute("SELECT id, phone FROM users WHERE phone IS NOT NULL")
    users = cursor.fetchall()
    
    for user_id, phone in users:
        if phone:
            phone_clean = ''.join(c for c in str(phone) if c.isdigit())
            
            if len(phone_clean) != 10:
                print(f"User {user_id}: '{phone}' -> '{phone_clean}' (length: {len(phone_clean)})")
                
                if len(phone_clean) > 10:
                    phone_clean = phone_clean[-10:]
                    print(f"  -> Taking last 10 digits: '{phone_clean}'")
                
                cursor.execute("UPDATE users SET phone = ? WHERE id = ?", (phone_clean, user_id))
                fixed_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n=== Total records fixed: {fixed_count} ===")
    return fixed_count

if __name__ == "__main__":
    fix_phone_numbers()
