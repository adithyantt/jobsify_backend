#!/usr/bin/env python3
"""
Fix existing notifications to make them clickable.
This script updates old notifications that have type='general' and reference_id=NULL
to have the correct type and reference_id based on the message content.
"""

import re
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./jobsify.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def extract_job_id_from_message(message):
    """Extract job ID from message like 'Your report on job ID 27 has been banned.'"""
    match = re.search(r'job ID (\d+)', message)
    if match:
        return int(match.group(1))
    return None

def extract_worker_id_from_message(message):
    """Extract worker ID from message like 'Your report on worker ID 5 has been banned.'"""
    match = re.search(r'worker ID (\d+)', message)
    if match:
        return int(match.group(1))
    return None

def extract_name_from_message(message):
    """Extract name from approval/rejection messages like 'Your worker profile 'Rahul' has been approved...'"""
    match = re.search(r"'([^']+)'", message)
    if match:
        return match.group(1)
    return None


def fix_notifications():
    db = SessionLocal()
    try:
        # Get all notifications with type='general' or NULL reference_id
        result = db.execute(text("""
            SELECT id, message, type, reference_id 
            FROM notifications 
            WHERE type = 'general' OR reference_id IS NULL
        """))
        
        notifications = result.fetchall()
        print(f"Found {len(notifications)} notifications to fix")
        
        fixed_count = 0
        
        for notif in notifications:
            notif_id = notif.id
            message = notif.message
            
            # Try to extract job ID from report messages
            job_id = extract_job_id_from_message(message)
            if job_id:
                db.execute(text("""
                    UPDATE notifications 
                    SET type = 'job', reference_id = :ref_id 
                    WHERE id = :id
                """), {"ref_id": job_id, "id": notif_id})
                print(f"  Fixed notification {notif_id}: type='job', reference_id={job_id}")
                fixed_count += 1
                continue
            
            # Try to extract worker ID from report messages
            worker_id = extract_worker_id_from_message(message)
            if worker_id:
                db.execute(text("""
                    UPDATE notifications 
                    SET type = 'worker', reference_id = :ref_id 
                    WHERE id = :id
                """), {"ref_id": worker_id, "id": notif_id})
                print(f"  Fixed notification {notif_id}: type='worker', reference_id={worker_id}")
                fixed_count += 1
                continue
            
            # Handle approval/rejection messages for jobs
            if "job" in message.lower() and ("approved" in message.lower() or "rejected" in message.lower()):
                name = extract_name_from_message(message)
                if name:
                    # Try to find job by title
                    result = db.execute(text("""
                        SELECT id FROM jobs WHERE title = :title LIMIT 1
                    """), {"title": name})
                    job_row = result.fetchone()
                    if job_row:
                        db.execute(text("""
                            UPDATE notifications 
                            SET type = 'job', reference_id = :ref_id 
                            WHERE id = :id
                        """), {"ref_id": job_row.id, "id": notif_id})
                        print(f"  Fixed notification {notif_id}: type='job', reference_id={job_row.id} (from title '{name}')")
                        fixed_count += 1
                        continue
            
            # Handle approval/rejection messages for workers
            if "worker profile" in message.lower() and ("approved" in message.lower() or "rejected" in message.lower()):
                name = extract_name_from_message(message)
                if name:
                    # Try to find worker by name
                    result = db.execute(text("""
                        SELECT id FROM workers WHERE name = :name LIMIT 1
                    """), {"name": name})
                    worker_row = result.fetchone()
                    if worker_row:
                        db.execute(text("""
                            UPDATE notifications 
                            SET type = 'worker', reference_id = :ref_id 
                            WHERE id = :id
                        """), {"ref_id": worker_row.id, "id": notif_id})
                        print(f"  Fixed notification {notif_id}: type='worker', reference_id={worker_row.id} (from name '{name}')")
                        fixed_count += 1
                        continue
            
            print(f"  Could not fix notification {notif_id}: {message[:50]}...")

        
        db.commit()
        print(f"\n✅ Fixed {fixed_count} notifications!")
        
        # Show summary
        result = db.execute(text("""
            SELECT type, COUNT(*) as count 
            FROM notifications 
            GROUP BY type
        """))
        print("\nNotification types after fix:")
        for row in result.fetchall():
            print(f"  {row.type}: {row.count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_notifications()
