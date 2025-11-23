
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.config import settings
from app.crud.user import get_password_hash, verify_password

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/dev.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_users():
    db = SessionLocal()
    try:
        print("Checking users in database...")
        result = db.execute(text("SELECT id, username, role, is_active, password_hash FROM users"))
        users = result.fetchall()
        
        if not users:
            print("No users found in database!")
            return

        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Active: {user.is_active}")
            print(f"Password Hash: {user.password_hash[:20]}...")
            
            # Test password verification for common passwords
            test_passwords = ["password", "admin", "operator", "manager", "SecurePass123", "password123"]
            found = False
            for pwd in test_passwords:
                if verify_password(pwd, user.password_hash):
                    print(f"  [SUCCESS] Password matches: '{pwd}'")
                    found = True
                    break
            
            if not found:
                print("  [WARNING] Could not verify password with common defaults.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
