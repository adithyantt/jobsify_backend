#!/usr/bin/env python3
"""
Update admin passwords. Run this to set new passwords for admin users.
"""

import bcrypt
from app.database import SessionLocal
from app.models.user import User

# Set your desired admin passwords here
ADMIN_PASSWORDS = {
    "admin@jobsify.com": "admin123",  # Change to your preferred password
    "jobsify.admin@gmail.com": "admin123",  # Change to your preferred password
    "superadmin@jobsify.com": "admin123",  # Change to your preferred password
}

def update_admin_passwords():
    """Update passwords for predefined admin users."""
    db = SessionLocal()
    try:
        print("🔐 Updating admin passwords...")
        
        for email, new_password in ADMIN_PASSWORDS.items():
            admin = db.query(User).filter(User.email == email).first()
            
            if not admin:
                print(f"  ❌ Admin {email} not found")
                continue
            
            # Hash new password
            hashed_password = bcrypt.hashpw(
                new_password.encode(),
                bcrypt.gensalt()
            ).decode()
            
            # Update password
            admin.password = hashed_password
            db.commit()
            print(f"  ✅ Updated password for {email}")
        
        print("\n🎉 Admin password update complete!")
        print("\n📋 Current admin credentials:")
        for email, password in ADMIN_PASSWORDS.items():
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_passwords()
