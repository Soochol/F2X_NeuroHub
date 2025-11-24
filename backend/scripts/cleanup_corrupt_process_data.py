from app.database import SessionLocal
from app.models.process_data import ProcessData
from app.schemas.process_data import ProcessResult
from sqlalchemy import and_
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_corrupt_data():
    db = SessionLocal()
    try:
        # Find corrupt records: result is set (PASS/FAIL) but completed_at is None
        corrupt_records = db.query(ProcessData).filter(
            and_(
                ProcessData.result.in_([ProcessResult.PASS, ProcessResult.FAIL, ProcessResult.REWORK]),
                ProcessData.completed_at.is_(None)
            )
        ).all()

        if not corrupt_records:
            logger.info("No corrupt ProcessData records found. Database is clean.")
            return

        logger.info(f"Found {len(corrupt_records)} corrupt ProcessData records.")
        
        for pd in corrupt_records:
            logger.info(f"Deleting corrupt record ID {pd.id}: result={pd.result}, completed_at=None, started_at={pd.started_at}")
            db.delete(pd)

        db.commit()
        logger.info("Cleanup completed successfully.")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting cleanup of corrupt ProcessData records...")
    cleanup_corrupt_data()
