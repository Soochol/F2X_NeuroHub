import logging
from app.database import engine, Base
from app.models import *  # Import all models to ensure they are registered with Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_db()
