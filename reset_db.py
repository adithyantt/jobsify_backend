import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Delete the old database
db_path = "jobsify.db"
if os.path.exists(db_path):
    print(f"Removing old database: {db_path}")
    os.remove(db_path)
    print("Old database removed.")

# Import and run the database initialization
from app.init_db import Base, engine
from app.models.user import User
from app.models.job import Job
from app.models.workers import Worker
from app.models.report import Report

print("Creating new database tables with updated schema...")
Base.metadata.create_all(bind=engine)
print("Database recreated successfully!")

# Initialize admin users
print("\nInitializing admin users...")
from init_admins import init_admins
init_admins()
print("Done! You can now run the server.")
