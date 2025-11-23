import logging
from datetime import datetime, timezone
from app.database import SessionLocal
from app.crud import user as user_crud
from app.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_persistence():
    db = SessionLocal()
    user_id = None
    try:
        logger.info("Step 1: Authenticate and Update")
        user = user_crud.authenticate(db, username="admin", password="admin123")
        if not user:
            logger.error("❌ Authentication failed")
            return
        
        user_id = user.id
        logger.info(f"User ID: {user_id}")
        
        # This uses datetime.now(timezone.utc) inside
        user_crud.update_last_login(db, user.id)
        db.commit() # Force write to DB
        logger.info("✅ Committed update to DB")
        
    except Exception as e:
        logger.error(f"❌ Error during update: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    if user_id:
        logger.info("Step 2: Read back")
        db2 = SessionLocal()
        try:
            user = db2.query(User).filter(User.id == user_id).first()
            logger.info(f"Read user: {user.username}")
            logger.info(f"Last login: {user.last_login_at}")
            logger.info(f"Type of last_login: {type(user.last_login_at)}")
            logger.info("✅ Read back successful")
        except Exception as e:
            logger.error(f"❌ Error during read back: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db2.close()

if __name__ == "__main__":
    test_persistence()
