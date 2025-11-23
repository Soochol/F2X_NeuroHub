from app.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

def check_users():
    db = SessionLocal()
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        print("Database connection successful.")
        
        count = db.query(User).count()
        print(f"User count: {count}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
