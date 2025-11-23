import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_users():
    db = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).first():
            logger.info("Users already exist. Skipping seed.")
            return

        logger.info("Seeding initial users...")

        users = [
            User(
                username="admin",
                email="admin@neurohub.com",
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                department="IT"
            ),
            User(
                username="manager1",
                email="manager1@neurohub.com",
                password_hash=get_password_hash("manager123"),
                full_name="Manager One",
                role=UserRole.MANAGER,
                department="Production"
            ),
            User(
                username="operator1",
                email="operator1@neurohub.com",
                password_hash=get_password_hash("operator123"),
                full_name="Operator One",
                role=UserRole.OPERATOR,
                department="Assembly"
            )
        ]

        db.add_all(users)
        db.commit()
        logger.info("✅ Initial users seeded successfully!")

    except Exception as e:
        logger.error(f"❌ Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
