#!/usr/bin/env python3
"""
Debug script for vivekkrishna960@gmail.com jobs issue
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'jobsify.db')

def debug_vivek_jobs():
    print("Debugging vivekkrishna960@gmail.com jobs...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check total jobs
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        print(f"Total jobs in database: {total_jobs}")

        # Check jobs for vivekkrishna960@gmail.com
        email = "vivekkrishna960@gmail.com"
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE user_email = ?", (email,))
        vivek_jobs = cursor.fetchone()[0]
        print(f"Jobs for {email}: {vivek_jobs}")

        # List all distinct user_emails
        cursor.execute("SELECT DISTINCT user_email FROM jobs")
        emails = cursor.fetchall()
        print(f"Distinct user emails: {[email[0] for email in emails]}")

        # Check if the email exists in lowercase
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE LOWER(user_email) = LOWER(?)", (email,))
        vivek_jobs_lower = cursor.fetchone()[0]
        print(f"Jobs for {email} (case insensitive): {vivek_jobs_lower}")

        # Show sample jobs
        cursor.execute("SELECT id, title, user_email FROM jobs LIMIT 5")
        sample_jobs = cursor.fetchall()
        print("Sample jobs:")
        for job in sample_jobs:
            print(f"  ID: {job[0]}, Title: {job[1]}, Email: {job[2]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_vivek_jobs()
