#!/usr/bin/env python3
"""
Add test jobs to the database for testing the my jobs endpoint
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'jobsify.db')

def add_test_jobs():
    """Add test jobs to the database"""
    print(f"Connecting to database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Test email to use
        test_email = "test@example.com"
        
        # Check if jobs already exist for this email
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_email = ?", (test_email,))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"Found {existing_count} existing jobs for {test_email}")
            print("Skipping job creation to avoid duplicates")
            return True
        
        # Add test jobs
        test_jobs = [
            {
                "title": "House Cleaning",
                "category": "Cleaning",
                "description": "Need someone to clean my 2BHK apartment",
                "location": "Kochi, Kerala",
                "phone": "9876543210",
                "latitude": "9.9312",
                "longitude": "76.2673",
                "user_email": test_email,
                "verified": 1,
                "urgent": 0,
                "salary": "500",
                "created_at": datetime.now().isoformat()
            },
            {
                "title": "Plumbing Work",
                "category": "Plumbing",
                "description": "Fix leaking kitchen sink",
                "location": "Ernakulam, Kerala",
                "phone": "9876543211",
                "latitude": "9.9816",
                "longitude": "76.2999",
                "user_email": test_email,
                "verified": 1,
                "urgent": 1,
                "salary": "300",
                "created_at": datetime.now().isoformat()
            },
            {
                "title": "Garden Maintenance",
                "category": "Gardening",
                "description": "Monthly garden maintenance required",
                "location": "Aluva, Kerala",
                "phone": "9876543212",
                "latitude": "10.1076",
                "longitude": "76.3457",
                "user_email": test_email,
                "verified": 0,
                "urgent": 0,
                "salary": "1000",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        for job in test_jobs:
            cursor.execute("""
                INSERT INTO jobs (
                    title, category, description, location, phone,
                    latitude, longitude, user_email, verified, urgent,
                    salary, created_at, is_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job["title"], job["category"], job["description"],
                job["location"], job["phone"], job["latitude"],
                job["longitude"], job["user_email"], job["verified"],
                job["urgent"], job["salary"], job["created_at"],
                job["verified"]  # is_verified same as verified
            ))
            print(f"Added job: {job['title']}")
        
        conn.commit()
        print(f"\n✅ Successfully added {len(test_jobs)} test jobs for {test_email}")
        
        # Verify the jobs were added
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_email = ?", (test_email,))
        count = cursor.fetchone()[0]
        print(f"Total jobs for {test_email}: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = add_test_jobs()
    exit(0 if success else 1)
