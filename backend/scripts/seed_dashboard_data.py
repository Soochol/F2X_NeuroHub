"""
Dashboard Simulation Data Generator for F2X NeuroHub MES.

This script generates realistic test data for dashboard simulation and testing.

Usage:
    python backend/scripts/seed_dashboard_data.py
    python backend/scripts/seed_dashboard_data.py --reset  # Clear existing data first
    python backend/scripts/seed_dashboard_data.py --scale medium  # small/medium/large

Requirements:
    pip install faker
"""

import sys
import os
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from faker import Faker
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    ProductModel, Process, User, UserRole,
    ProductionLine, Equipment, Lot, LotStatus,
    Serial, SerialStatus, ProcessData, DataLevel, ProcessResult,
    WIPItem, WIPProcessHistory
)
from app.crud import lot as lot_crud, serial as serial_crud
from app.schemas import LotCreate, SerialCreate

# Initialize Faker with Korean locale
fake = Faker(['ko_KR', 'en_US'])

# Scale configurations
SCALE_CONFIG = {
    'small': {
        'lots': 5,
        'serials_per_lot': (10, 30),
        'equipment_per_line': 8,
    },
    'medium': {
        'lots': 10,
        'serials_per_lot': (30, 60),
        'equipment_per_line': 8,
    },
    'large': {
        'lots': 20,
        'serials_per_lot': (50, 100),
        'equipment_per_line': 8,
    }
}


def clear_data(db: Session):
    """Clear existing data in reverse dependency order."""
    print("Clearing existing data...")

    # Delete in order of dependencies (reverse of creation)
    db.query(WIPProcessHistory).delete()
    db.query(ProcessData).delete()
    db.query(WIPItem).delete()
    db.query(Serial).delete()
    db.query(Lot).delete()
    db.query(Equipment).delete()
    db.query(ProductionLine).delete()
    db.query(ProductModel).delete()
    # Keep processes and users if they exist from DDL

    db.commit()
    print("   Existing data cleared.")


def seed_users(db: Session) -> list[User]:
    """Create test users if they don't exist."""
    print("Seeding users...")

    existing_users = db.query(User).all()
    if existing_users:
        print(f"   Found {len(existing_users)} existing users.")
        return existing_users

    users_data = [
        {"username": "admin", "email": "admin@f2x.com", "full_name": "System Admin",
         "role": UserRole.ADMIN, "department": "IT"},
        {"username": "manager1", "email": "manager1@f2x.com", "full_name": "Kim Manager",
         "role": UserRole.MANAGER, "department": "Production"},
        {"username": "operator1", "email": "operator1@f2x.com", "full_name": "Park Operator",
         "role": UserRole.OPERATOR, "department": "Line-A"},
        {"username": "operator2", "email": "operator2@f2x.com", "full_name": "Lee Operator",
         "role": UserRole.OPERATOR, "department": "Line-B"},
        {"username": "operator3", "email": "operator3@f2x.com", "full_name": "Choi Operator",
         "role": UserRole.OPERATOR, "department": "Line-A"},
    ]

    users = []
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password_hash="$2b$12$06V3LW8lqL93TwDD69SXq.g9SUU5y/L4.gcX35xqO5fkLlEW21T3K",  # password123
            full_name=user_data["full_name"],
            role=user_data["role"],
            department=user_data["department"],
            is_active=True
        )
        db.add(user)
        users.append(user)

    db.commit()
    print(f"   Created {len(users)} users.")
    return users


def seed_processes(db: Session) -> list[Process]:
    """Create standard manufacturing processes."""
    print("Seeding processes...")

    existing = db.query(Process).all()
    if existing:
        print(f"   Found {len(existing)} existing processes.")
        return existing

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

    processes = []
    for p_data in processes_data:
        process = Process(**p_data)
        db.add(process)
        processes.append(process)

    db.commit()
    print(f"   Created {len(processes)} processes.")
    return processes


def seed_product_models(db: Session) -> list[ProductModel]:
    """Create test product models."""
    print("Seeding product models...")

    existing = db.query(ProductModel).all()
    if existing:
        print(f"   Found {len(existing)} existing product models.")
        return existing

    models_data = [
        {
            "model_code": "PSA-1000",
            "model_name": "NeuroHub PSA 1000",
            "specifications": {
                "voltage": "12V",
                "current": "5A",
                "power": "60W",
                "dimensions": {"width": 100, "height": 50, "depth": 150},
                "weight": 500,
                "certifications": ["CE", "FCC", "RoHS"]
            },
            "status": "ACTIVE"
        },
        {
            "model_code": "PSA-2000",
            "model_name": "NeuroHub PSA 2000",
            "specifications": {
                "voltage": "24V",
                "current": "10A",
                "power": "240W",
                "dimensions": {"width": 150, "height": 75, "depth": 200},
                "weight": 800,
                "certifications": ["CE", "FCC", "RoHS", "UL"]
            },
            "status": "ACTIVE"
        },
        {
            "model_code": "PSA-3000",
            "model_name": "NeuroHub PSA 3000 Pro",
            "specifications": {
                "voltage": "48V",
                "current": "20A",
                "power": "960W",
                "dimensions": {"width": 200, "height": 100, "depth": 250},
                "weight": 1200,
                "certifications": ["CE", "FCC", "RoHS", "UL"]
            },
            "status": "ACTIVE"
        }
    ]

    models = []
    for model_data in models_data:
        model = ProductModel(**model_data)
        db.add(model)
        models.append(model)

    db.commit()
    print(f"   Created {len(models)} product models.")
    return models


def seed_production_lines(db: Session) -> list[ProductionLine]:
    """Create test production lines."""
    print("Seeding production lines...")

    existing = db.query(ProductionLine).all()
    if existing:
        print(f"   Found {len(existing)} existing production lines.")
        return existing

    lines_data = [
        {
            "line_code": "KR001",
            "line_name": "Production Line A",
            "description": "Main assembly line for PSA-1000 and PSA-2000",
            "cycle_time_sec": 1260,  # 21 minutes total
            "location": "Building A, Floor 1",
            "is_active": True
        },
        {
            "line_code": "KR002",
            "line_name": "Production Line B",
            "description": "Secondary assembly line for PSA-3000 Pro",
            "cycle_time_sec": 1500,  # 25 minutes total
            "location": "Building A, Floor 2",
            "is_active": True
        }
    ]

    lines = []
    for line_data in lines_data:
        line = ProductionLine(**line_data)
        db.add(line)
        lines.append(line)

    db.commit()
    print(f"   Created {len(lines)} production lines.")
    return lines


def seed_equipment(db: Session, production_lines: list[ProductionLine]) -> list[Equipment]:
    """Create test equipment for each production line."""
    print("Seeding equipment...")

    existing = db.query(Equipment).all()
    if existing:
        print(f"   Found {len(existing)} existing equipment.")
        return existing

    # Get all processes
    processes = db.query(Process).order_by(Process.process_number).all()
    if not processes:
        print("   Warning: No processes found. Skipping equipment seeding.")
        return []

    equipment_types = {
        1: ("Laser Marker", "LASER"),
        2: ("Assembly Station", "ASSEMBLY"),
        3: ("Sensor Tester", "TESTER"),
        4: ("Firmware Programmer", "PROGRAMMER"),
        5: ("Robot Arm", "ROBOT"),
        6: ("Performance Tester", "TESTER"),
        7: ("Label Printer", "PRINTER"),
        8: ("Packaging Station", "PACKAGING")
    }

    equipment_list = []
    for line in production_lines:
        for process in processes:
            eq_name, eq_type = equipment_types.get(process.process_number, ("Unknown", "OTHER"))

            equipment = Equipment(
                equipment_code=f"EQ-{line.line_code}-{process.process_number:02d}",
                equipment_name=f"{eq_name} ({line.line_code})",
                equipment_type=eq_type,
                process_id=process.id,
                production_line_id=line.id,
                manufacturer=fake.company(),
                model_number=f"MODEL-{fake.random_number(digits=4)}",
                status="AVAILABLE"
            )
            db.add(equipment)
            equipment_list.append(equipment)

    db.commit()
    print(f"   Created {len(equipment_list)} equipment items.")
    return equipment_list


def seed_lots(db: Session, product_models: list[ProductModel],
              production_lines: list[ProductionLine], scale: str) -> list[Lot]:
    """Create test LOTs with various statuses."""
    print("Seeding LOTs...")

    config = SCALE_CONFIG[scale]
    num_lots = config['lots']

    # Status distribution for realistic dashboard
    status_distribution = [
        (LotStatus.COMPLETED, 0.3),
        (LotStatus.IN_PROGRESS, 0.5),
        (LotStatus.CREATED, 0.2),
    ]

    lots = []
    today = datetime.now().date()

    for i in range(num_lots):
        # Pick random status based on distribution
        rand = random.random()
        cumulative = 0
        status = LotStatus.IN_PROGRESS
        for s, prob in status_distribution:
            cumulative += prob
            if rand <= cumulative:
                status = s
                break

        # Production date - vary by a few days to create different months/days
        days_offset = i % 30  # Spread across 30 days
        production_date = today - timedelta(days=days_offset)

        # Random product model and production line
        product_model = random.choice(product_models)
        production_line = random.choice(production_lines)

        # Target quantity (max 100 per business rule)
        target_quantity = random.randint(30, 100)

        # CRUD function handles LOT number generation with auto-increment sequence
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_line_id=production_line.id,
            production_date=production_date,
            target_quantity=target_quantity,
            status=status
        )

        try:
            lot = lot_crud.create(db, lot_data)
            lots.append(lot)
        except Exception as e:
            print(f"  Warning: Could not create LOT: {e}")
            continue

    print(f"   Created {len(lots)} LOTs.")
    return lots


def seed_serials(db: Session, lots: list[Lot], scale: str) -> list[Serial]:
    """Create serials for each LOT based on its status."""
    print("Seeding serials...")

    config = SCALE_CONFIG[scale]
    min_serials, max_serials = config['serials_per_lot']

    all_serials = []

    for lot in lots:
        # Determine number of serials based on LOT status
        if lot.status == LotStatus.CREATED:
            num_serials = 0
        elif lot.status == LotStatus.IN_PROGRESS:
            num_serials = random.randint(min_serials, min(max_serials, lot.target_quantity))
        else:  # COMPLETED
            num_serials = lot.target_quantity

        for i in range(1, num_serials + 1):  # Start from 1 for sequence_in_lot
            # Determine serial status based on lot status
            if lot.status == LotStatus.COMPLETED:
                # 90% passed, 8% failed, 2% passed with rework
                rand = random.random()
                if rand < 0.90:
                    status = SerialStatus.PASSED
                    rework_count = 0
                elif rand < 0.98:
                    status = SerialStatus.FAILED
                    rework_count = random.randint(0, 3)
                else:
                    status = SerialStatus.PASSED
                    rework_count = random.randint(1, 2)
            else:  # IN_PROGRESS
                # Mix of statuses to show WIP
                rand = random.random()
                if rand < 0.3:
                    status = SerialStatus.CREATED
                    rework_count = 0
                elif rand < 0.7:
                    status = SerialStatus.IN_PROGRESS
                    rework_count = 0
                elif rand < 0.9:
                    status = SerialStatus.PASSED
                    rework_count = 0
                else:
                    status = SerialStatus.FAILED
                    rework_count = random.randint(0, 2)

            # Add failure_reason for FAILED status
            failure_reason = None
            if status == SerialStatus.FAILED:
                failure_reason = random.choice([
                    "Sensor test failed",
                    "Voltage out of range",
                    "Assembly defect",
                    "Firmware upload error",
                    "Visual inspection failed"
                ])

            # Use CRUD function to create serial (handles serial_number generation)
            serial_data = SerialCreate(
                lot_id=lot.id,
                sequence_in_lot=i,
                status=status.value,
                rework_count=rework_count,
                failure_reason=failure_reason
            )

            try:
                serial = serial_crud.create(db, serial_data)
                all_serials.append(serial)
            except Exception as e:
                print(f"  Warning: Could not create serial: {e}")
                continue

    print(f"   Created {len(all_serials)} serials.")
    return all_serials


def seed_process_data(db: Session, serials: list[Serial], users: list[User],
                      production_lines: list[ProductionLine], skip_equipment: bool = False):
    """Create process data records for serials."""
    print("Seeding process data...")

    # Get all processes
    processes = db.query(Process).order_by(Process.process_number).all()
    if not processes:
        print("   Warning: No processes found. Skipping process data seeding.")
        return

    # Get operators only
    operators = [u for u in users if u.role == UserRole.OPERATOR]
    if not operators:
        operators = users  # Fallback to any user

    # Get equipment by process and line (skip if flag set)
    equipment_map = {}
    if not skip_equipment:
        equipment_list = db.query(Equipment).all()
        for eq in equipment_list:
            key = (eq.process_id, eq.production_line_id)
            equipment_map[key] = eq

    process_data_count = 0

    for serial in serials:
        if serial.status == SerialStatus.CREATED:
            continue

        # Get lot for production_line_id
        lot = db.query(Lot).filter(Lot.id == serial.lot_id).first()

        # Determine how many processes to complete
        if serial.status == SerialStatus.PASSED:
            completed_processes = 8
        elif serial.status == SerialStatus.FAILED:
            # Failed at some random process
            completed_processes = random.randint(1, 7)
        else:  # IN_PROGRESS
            # Currently at some process
            completed_processes = random.randint(1, 7)

        base_time = datetime.now() - timedelta(hours=random.randint(1, 24))

        for i, process in enumerate(processes[:completed_processes]):
            # Calculate times
            duration = process.estimated_duration_seconds or 60
            started_at = base_time + timedelta(minutes=i * 30)
            completed_at = started_at + timedelta(seconds=duration)

            # Determine result
            is_last = (i == completed_processes - 1)
            if serial.status == SerialStatus.FAILED and is_last:
                result = ProcessResult.FAIL
            elif serial.rework_count > 0 and random.random() < 0.3 and not is_last:
                result = ProcessResult.REWORK
            else:
                result = ProcessResult.PASS

            # Get equipment
            equipment = equipment_map.get((process.id, lot.production_line_id))

            # Generate measurements based on process
            measurements = generate_measurements(process.process_number)

            # Generate defects if FAIL
            defects = None
            if result == ProcessResult.FAIL:
                defects = generate_defects(process.process_number)

            process_data = ProcessData(
                lot_id=lot.id,
                serial_id=serial.id,
                process_id=process.id,
                operator_id=random.choice(operators).id,
                equipment_id=equipment.id if equipment else None,
                data_level=DataLevel.SERIAL,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=int((completed_at - started_at).total_seconds()),
                result=result,
                measurements=measurements,
                defects=defects
            )
            db.add(process_data)
            process_data_count += 1

    db.commit()
    print(f"   Created {process_data_count} process data records.")


def generate_measurements(process_number: int) -> dict:
    """Generate realistic measurements for each process."""

    if process_number == 1:  # Laser Marking
        return {
            "marking_result": "SUCCESS",
            "laser_power": round(random.uniform(80, 100), 1),
            "marking_depth": round(random.uniform(0.1, 0.3), 3)
        }

    elif process_number == 2:  # LMA Assembly
        return {
            "assembly_time": round(random.uniform(150, 210), 1),
            "visual_inspection": "PASS",
            "torque_value": round(random.uniform(4.5, 5.5), 2)
        }

    elif process_number == 3:  # Sensor Inspection
        return {
            "temp_sensor": {
                "measured_temp": round(random.uniform(58, 62), 1),
                "target_temp": 60.0,
                "tolerance": 1.0,
                "result": "PASS"
            },
            "tof_sensor": {
                "i2c_communication": True,
                "result": "PASS"
            }
        }

    elif process_number == 4:  # Firmware Upload
        return {
            "firmware_version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
            "upload_result": "SUCCESS",
            "upload_time_seconds": random.randint(180, 300)
        }

    elif process_number == 5:  # Robot Assembly
        return {
            "assembly_time": round(random.uniform(280, 320), 1),
            "cable_connection": "OK",
            "final_visual_check": "PASS"
        }

    elif process_number == 6:  # Performance Test
        return {
            "test_results": [
                {"test_name": "Voltage Test", "result": "PASS", "value": round(random.uniform(11.8, 12.2), 2)},
                {"test_name": "Current Test", "result": "PASS", "value": round(random.uniform(4.8, 5.2), 2)},
                {"test_name": "Efficiency Test", "result": "PASS", "value": round(random.uniform(90, 98), 1)}
            ],
            "overall_result": "PASS",
            "test_duration_seconds": random.randint(160, 200)
        }

    elif process_number == 7:  # Label Printing
        return {
            "label_printed": True,
            "print_quality": round(random.uniform(95, 100), 1),
            "barcode_verified": True
        }

    elif process_number == 8:  # Packaging
        return {
            "visual_defects": [],
            "packaging_complete": True,
            "final_result": "PASS",
            "weight_check": round(random.uniform(495, 505), 1)
        }

    return {}


def generate_defects(process_number: int) -> list:
    """Generate defect data for failed processes."""

    defect_types = {
        1: [
            {"defect_code": "LASER_001", "defect_name": "Marking unclear", "severity": "MEDIUM"},
            {"defect_code": "LASER_002", "defect_name": "Wrong position", "severity": "HIGH"}
        ],
        2: [
            {"defect_code": "LMA_001", "defect_name": "Assembly gap", "severity": "HIGH"},
            {"defect_code": "LMA_002", "defect_name": "Component misalignment", "severity": "MEDIUM"}
        ],
        3: [
            {"defect_code": "SENSOR_001", "defect_name": "Temperature out of range", "severity": "HIGH"},
            {"defect_code": "SENSOR_002", "defect_name": "ToF sensor failure", "severity": "CRITICAL"}
        ],
        4: [
            {"defect_code": "FW_001", "defect_name": "Upload failed", "severity": "HIGH"},
            {"defect_code": "FW_002", "defect_name": "Version mismatch", "severity": "MEDIUM"}
        ],
        5: [
            {"defect_code": "ROBOT_001", "defect_name": "Cable connection failure", "severity": "HIGH"},
            {"defect_code": "ROBOT_002", "defect_name": "Motor alignment issue", "severity": "CRITICAL"}
        ],
        6: [
            {"defect_code": "PERF_001", "defect_name": "Voltage test failed", "severity": "HIGH"},
            {"defect_code": "PERF_002", "defect_name": "Efficiency below threshold", "severity": "MEDIUM"}
        ],
        7: [
            {"defect_code": "LABEL_001", "defect_name": "Print quality poor", "severity": "LOW"},
            {"defect_code": "LABEL_002", "defect_name": "Barcode unreadable", "severity": "MEDIUM"}
        ],
        8: [
            {"defect_code": "PKG_001", "defect_name": "Scratch on surface", "severity": "LOW"},
            {"defect_code": "PKG_002", "defect_name": "Packaging damaged", "severity": "MEDIUM"}
        ]
    }

    defects = defect_types.get(process_number, [])
    if defects:
        selected = random.choice(defects)
        selected["description"] = fake.sentence()
        return [selected]

    return []


def update_lot_statistics(db: Session, lots: list[Lot]):
    """Update LOT statistics based on serials."""
    print("Updating LOT statistics...")

    for lot in lots:
        serials = db.query(Serial).filter(Serial.lot_id == lot.id).all()

        lot.actual_quantity = len(serials)
        lot.passed_quantity = len([s for s in serials if s.status == SerialStatus.PASSED])
        lot.failed_quantity = len([s for s in serials if s.status == SerialStatus.FAILED])

        if lot.status == LotStatus.COMPLETED and lot.actual_quantity >= lot.target_quantity:
            lot.completed_at = datetime.now() - timedelta(hours=random.randint(1, 24))

    db.commit()
    print("   LOT statistics updated.")


def print_summary(db: Session):
    """Print summary of generated data."""
    print("\n" + "=" * 60)
    print("Data Generation Summary")
    print("=" * 60)

    # Count records
    users_count = db.query(User).count()
    models_count = db.query(ProductModel).count()
    lines_count = db.query(ProductionLine).count()
    lots_count = db.query(Lot).count()
    serials_count = db.query(Serial).count()
    process_data_count = db.query(ProcessData).count()

    print(f"\nUsers:           {users_count}")
    print(f"Product Models:  {models_count}")
    print(f"Production Lines: {lines_count}")
    print(f"LOTs:            {lots_count}")
    print(f"Serials:         {serials_count}")
    print(f"Process Data:    {process_data_count}")

    # LOT status breakdown
    print("\nLOT Status Distribution:")
    for status in LotStatus:
        count = db.query(Lot).filter(Lot.status == status).count()
        print(f"  - {status.value}: {count}")

    # Serial status breakdown
    print("\nSerial Status Distribution:")
    for status in SerialStatus:
        count = db.query(Serial).filter(Serial.status == status).count()
        print(f"  - {status.value}: {count}")

    print("\n" + "=" * 60)
    print("Dashboard simulation data is ready!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start backend: cd backend && uvicorn app.main:app --reload")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open dashboard: http://localhost:5173")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Generate dashboard simulation data")
    parser.add_argument("--reset", action="store_true", help="Clear existing data first")
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="medium",
                       help="Data scale (default: medium)")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("F2X NeuroHub MES - Dashboard Data Generator")
    print("=" * 60)
    print(f"Scale: {args.scale}")
    print(f"Reset: {args.reset}")
    print("=" * 60 + "\n")

    db = SessionLocal()

    try:
        if args.reset:
            clear_data(db)

        # Seed data in dependency order
        users = seed_users(db)
        processes = seed_processes(db)
        product_models = seed_product_models(db)
        production_lines = seed_production_lines(db)
        equipment = seed_equipment(db, production_lines)
        lots = seed_lots(db, product_models, production_lines, args.scale)
        serials = seed_serials(db, lots, args.scale)
        seed_process_data(db, serials, users, production_lines, skip_equipment=False)
        update_lot_statistics(db, lots)

        print_summary(db)

    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
