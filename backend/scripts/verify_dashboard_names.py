import sys
import os
from datetime import date

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.services.analytics_service import analytics_service

def verify_process_names():
    db = SessionLocal()
    try:
        summary = analytics_service.get_dashboard_summary(db, date.today())
        print("Process Names in Dashboard Summary:")
        for process in summary["process_wip"]:
            print(f"- {process['process_name']}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_process_names()
