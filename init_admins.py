#!/usr/bin/env python3
"""
Initialize predefined admin users in the database.
Run this script once to create admin accounts.
"""

import bcrypt
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User

# Predefined admin emails and their passwords
# You can change these passwords before running the script
ADMIN_USERS = [
    {
        "email": "admin@jobsify.com",
        "password": "admin123",  # Change this!
        "name": "Admin"
    },
    {
        "email": "jobsify.admin@gmail.com",
        "password": "admin123",  # Change this!
        "name": "Jobsify Admin"
    },
    {
        "email": "superadmin@jobsify.com",
        "password": "admin123",  # Change this!
        "name": "Super Admin"
    }
]

def init_admin_users():
    """Create predefined admin users if they don't exist."""
    db = SessionLocal()
    try:
        print("🔐 Initializing admin users...")
        
        for admin_data in ADMIN_USERS:
            # Check if admin already exists
            existing_user = db.query(User).filter(User.email == admin_data["email"]).first()
            
            if existing_user:
                # Update role to admin if not already
                if existing_user.role != "admin":
                    existing_user.role = "admin"
                    existing_user.email_verified = True
                    db.commit()
                    print(f"  ✅ Updated {admin_data['email']} to admin role")
                else:
                    print(f"  ℹ️  Admin {admin_data['email']} already exists")
                continue
            
            # Hash password
            hashed_password = bcrypt.hashpw(
                admin_data["password"].encode(),
                bcrypt.gensalt()
            ).decode()
            
            # Create admin user
            new_admin = User(
                name=admin_data["name"],
                email=admin_data["email"],
                password=hashed_password,
                role="admin",
                phone=None,
                verified=True,
                email_verified=True  # Admins don't need email verification
            )
            
            db.add(new_admin)
            db.commit()
            print(f"  ✅ Created admin: {admin_data['email']}")
        
        print("\n🎉 Admin initialization complete!")
        print("\n⚠️  IMPORTANT: Change the default passwords in production!")
        print("   You can modify the passwords in init_admins.py and run again.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    init_admin_users()
