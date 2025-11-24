import logging
from app.database import SessionLocal
from app.models import User
from app.schemas import UserRole
from app.core.security import get_password_hash
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_db():
    print(f"Connecting to: {settings.DATABASE_URL}")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@f2x.com").first()
        if not user:
            logger.info("Creating admin user...")
            user = User(
                email="admin@f2x.com",
                username="admin@f2x.com",
                full_name="Admin User",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(user)
            db.commit()
            logger.info("✅ Admin user created successfully!")
        else:
            logger.info("⚠️  Admin user already exists. Resetting password...")
            user.password_hash = get_password_hash("admin123")
            user.is_active = True
            db.commit()
            logger.info("✅ Admin password reset to 'admin123'")
            
    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
