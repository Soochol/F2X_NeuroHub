import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Process, User, UserRole
from app.core.security import get_password_hash
from app.models.process import ProcessType

def seed():
    db = SessionLocal()
    try:
        # 1. Admin User
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@f2x.com",
                full_name="Admin",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
        
        # 2. Standard Processes 1-8
        processes_data = [
            {"process_number": 1, "process_code": "LASER", "process_name_en": "Laser Marking", "process_name_ko": "레이저 마킹", "description": "Laser marking of serial number on PCB", "estimated_duration_seconds": 60, "sort_order": 1},
            {"process_number": 2, "process_code": "ASSEMBLY", "process_name_en": "LMA Assembly", "process_name_ko": "LMA 조립", "description": "Assembly of LMA components", "estimated_duration_seconds": 180, "sort_order": 2},
            {"process_number": 3, "process_code": "SENSOR", "process_name_en": "Sensor Inspection", "process_name_ko": "센서 검사", "description": "Inspection of temperature and ToF sensors", "estimated_duration_seconds": 45, "sort_order": 3},
            {"process_number": 4, "process_code": "FIRMWARE", "process_name_en": "Firmware Upload", "process_name_ko": "펌웨어 업로드", "description": "Flashing of main firmware", "estimated_duration_seconds": 240, "sort_order": 4},
            {"process_number": 5, "process_code": "ROBOT", "process_name_en": "Robot Assembly", "process_name_ko": "로봇 조립", "description": "Automated assembly by robot arm", "estimated_duration_seconds": 300, "sort_order": 5},
            {"process_number": 6, "process_code": "TEST", "process_name_en": "Performance Test", "process_name_ko": "성능 테스트", "description": "Comprehensive performance testing", "estimated_duration_seconds": 180, "sort_order": 6},
            {"process_number": 7, "process_code": "LABEL", "process_name_en": "Label Printing", "process_name_ko": "라벨 출력", "description": "Printing and attaching product label", "estimated_duration_seconds": 30, "sort_order": 7},
            {"process_number": 8, "process_code": "PACKAGING", "process_name_en": "Packaging", "process_name_ko": "포장", "description": "Final packaging and visual check", "estimated_duration_seconds": 60, "sort_order": 8},
        ]
        
        for p_data in processes_data:
            exists = db.query(Process).filter(Process.process_number == p_data["process_number"]).first()
            if not exists:
                db.add(Process(**p_data))
        
        db.commit()
        print("Done seeding admin and 8 processes.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
