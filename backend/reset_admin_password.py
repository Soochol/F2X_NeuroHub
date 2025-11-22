"""
Reset admin password to admin123.
"""
from app.database import SessionLocal
from app.crud import user as user_crud
from app.core.security import get_password_hash

def reset_admin_password():
    db = SessionLocal()
    try:
        # Get admin user
        admin = user_crud.get_by_username(db, username="admin")
        if not admin:
            print("Admin user not found!")
            return False
        
        # Hash the new password
        hashed_password = get_password_hash("admin123")
        
        # Update password directly
        admin.password_hash = hashed_password
        db.commit()
        
        print(f"✓ Admin password reset successfully!")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        return True
    except Exception as e:
        print(f"✗ Failed to reset password: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
