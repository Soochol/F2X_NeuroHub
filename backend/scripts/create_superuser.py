import logging
import sys
import os

# Add parent directory to path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_superuser():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            logger.info("User 'admin' already exists.")
            # Optional: Update password if needed, but for now just notify
            # user.password_hash = get_password_hash("admin123")
            # db.commit()
            # logger.info("Password updated for 'admin'.")
        else:
            logger.info("Creating superuser 'admin'...")
            user = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                full_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(user)
            db.commit()
            logger.info("Superuser 'admin' created successfully with password 'admin123'.")
    except Exception as e:
        logger.error(f"Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()
