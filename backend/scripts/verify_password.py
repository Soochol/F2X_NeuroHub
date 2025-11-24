from app.database import SessionLocal
from app.models import User
from app.core.security import verify_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@f2x.com").first()
        if user:
            logger.info(f"User found: {user.email}")
            logger.info(f"Hashed password: {user.password_hash[:20]}...")
            
            is_valid = verify_password("admin123", user.password_hash)
            logger.info(f"Password 'admin123' valid? {is_valid}")
            
            if is_valid:
                print("✅ Password verification SUCCESS")
            else:
                print("❌ Password verification FAILED")
        else:
            logger.error("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_password()
