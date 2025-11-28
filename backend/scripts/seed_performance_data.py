"""
Performance Test Data Generator for F2X NeuroHub MES.

This script generates large-scale test data for performance testing.

Usage:
    # In Docker container (Demo server)
    docker exec -it f2x-demo-backend python scripts/seed_performance_data.py

    # Local execution with DB URL
    DATABASE_URL=postgresql://postgres:DemoPassword2024!@localhost:5432/f2x_neurohub_demo \
    python backend/scripts/seed_performance_data.py

    # With options
    python backend/scripts/seed_performance_data.py --lots 60 --serials-per-lot 10
    python backend/scripts/seed_performance_data.py --reset  # Clear existing data first
"""

import sys
import os
import argparse
import random
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import (
    ProductModel, Process, User, UserRole,
    ProductionLine, Equipment, Lot, LotStatus,
    Serial, SerialStatus, ProcessData, DataLevel, ProcessResult,
    WIPItem, WIPStatus, WIPProcessHistory
)
from app.core.security import get_password_hash


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
    # Keep ProductModel, ProductionLine, Process, User (master data)

    db.commit()
    print("   Existing transaction data cleared.")


def ensure_users(db: Session) -> list[User]:
    """Ensure test users exist."""
    print("Checking users...")

    existing_users = db.query(User).all()
    if existing_users:
        print(f"   Found {len(existing_users)} existing users.")
        return existing_users

    print("   Creating test users...")
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
            password_hash=get_password_hash("password123"),
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


def ensure_processes(db: Session) -> list[Process]:
    """Ensure manufacturing processes exist."""
    print("Checking processes...")

    existing = db.query(Process).order_by(Process.process_number).all()
    if existing:
        print(f"   Found {len(existing)} existing processes.")
        return existing

    print("   Creating processes...")
    processes_data = [
        {"process_number": 1, "process_code": "LASER", "process_name_en": "Laser Marking", "process_name_ko": "레이저 마킹", "sort_order": 1, "estimated_duration_seconds": 60},
        {"process_number": 2, "process_code": "ASSEMBLY", "process_name_en": "LMA Assembly", "process_name_ko": "LMA 조립", "sort_order": 2, "estimated_duration_seconds": 180},
        {"process_number": 3, "process_code": "SENSOR", "process_name_en": "Sensor Inspection", "process_name_ko": "센서 검사", "sort_order": 3, "estimated_duration_seconds": 45},
        {"process_number": 4, "process_code": "FIRMWARE", "process_name_en": "Firmware Upload", "process_name_ko": "펌웨어 업로드", "sort_order": 4, "estimated_duration_seconds": 240},
        {"process_number": 5, "process_code": "ROBOT", "process_name_en": "Robot Assembly", "process_name_ko": "로봇 조립", "sort_order": 5, "estimated_duration_seconds": 300},
        {"process_number": 6, "process_code": "TEST", "process_name_en": "Performance Test", "process_name_ko": "성능 테스트", "sort_order": 6, "estimated_duration_seconds": 180},
        {"process_number": 7, "process_code": "LABEL", "process_name_en": "Label Printing", "process_name_ko": "라벨 출력", "sort_order": 7, "estimated_duration_seconds": 30, "process_type": "SERIAL_CONVERSION"},
        {"process_number": 8, "process_code": "PACKAGING", "process_name_en": "Packaging", "process_name_ko": "포장", "sort_order": 8, "estimated_duration_seconds": 60},
    ]

    processes = []
    for p_data in processes_data:
        process = Process(
            process_number=p_data["process_number"],
            process_code=p_data["process_code"],
            process_name_en=p_data["process_name_en"],
            process_name_ko=p_data["process_name_ko"],
            sort_order=p_data["sort_order"],
            estimated_duration_seconds=p_data.get("estimated_duration_seconds"),
            process_type=p_data.get("process_type", "MANUFACTURING"),
            quality_criteria={}
        )
        db.add(process)
        processes.append(process)

    db.commit()
    print(f"   Created {len(processes)} processes.")
    return processes


def ensure_product_models(db: Session) -> list[ProductModel]:
    """Ensure product models exist."""
    print("Checking product models...")

    existing = db.query(ProductModel).all()
    if existing:
        print(f"   Found {len(existing)} existing product models.")
        return existing

    print("   Creating product models...")
    models_data = [
        {"model_code": "PSA", "model_name": "NeuroHub PSA Standard", "status": "ACTIVE", "specifications": {}},
        {"model_code": "PSB", "model_name": "NeuroHub PSB Pro", "status": "ACTIVE", "specifications": {}},
    ]

    models = []
    for model_data in models_data:
        model = ProductModel(**model_data)
        db.add(model)
        models.append(model)

    db.commit()
    print(f"   Created {len(models)} product models.")
    return models


def ensure_production_lines(db: Session) -> list[ProductionLine]:
    """Ensure production lines exist."""
    print("Checking production lines...")

    existing = db.query(ProductionLine).all()
    if existing:
        print(f"   Found {len(existing)} existing production lines.")
        return existing

    print("   Creating production lines...")
    lines_data = [
        {"line_code": "KR01", "line_name": "Production Line A", "is_active": True},
        {"line_code": "KR02", "line_name": "Production Line B", "is_active": True},
    ]

    lines = []
    for line_data in lines_data:
        line = ProductionLine(**line_data)
        db.add(line)
        lines.append(line)

    db.commit()
    print(f"   Created {len(lines)} production lines.")
    return lines


def ensure_equipment(db: Session, processes: list[Process], production_lines: list[ProductionLine]) -> list[Equipment]:
    """Ensure equipment exists."""
    print("Checking equipment...")

    existing = db.query(Equipment).all()
    if existing:
        print(f"   Found {len(existing)} existing equipment.")
        return existing

    print("   Creating equipment...")
    equipment_types = {
        1: ("Laser Marker", "LASER_MARKER"),
        2: ("Assembly Station", "ASSEMBLY"),
        3: ("Sensor Tester", "SENSOR"),
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
                status="AVAILABLE"
            )
            db.add(equipment)
            equipment_list.append(equipment)

    db.commit()
    print(f"   Created {len(equipment_list)} equipment items.")
    return equipment_list


def generate_lot_number(line_code: str, model_code: str, production_date: date, sequence: int) -> str:
    """Generate LOT number in format: KR01PSA251101"""
    # Country(2) + Line(2) + Model(3) + YYMM(4) + Seq(2)
    country = "KR"
    line = line_code[-2:] if len(line_code) >= 2 else line_code.zfill(2)
    model = model_code[:3].upper()
    yymm = production_date.strftime("%y%m")
    seq = f"{sequence:02d}"
    return f"{country}{line}{model}{yymm}{seq}"


def generate_serial_number(lot_number: str, sequence: int) -> str:
    """Generate serial number in format: KR01PSA2511001"""
    return f"{lot_number}{sequence:03d}"


def generate_wip_id(lot_number: str, sequence: int) -> str:
    """Generate WIP ID in format: WIP-KR01PSA2511-001"""
    return f"WIP-{lot_number}-{sequence:03d}"


def create_lots(db: Session, product_models: list[ProductModel],
                production_lines: list[ProductionLine], num_lots: int) -> list[Lot]:
    """Create LOTs with various statuses."""
    print(f"Creating {num_lots} LOTs...")

    # Status distribution
    # CREATED: 10, IN_PROGRESS: 30, COMPLETED: 15, CLOSED: 5
    status_counts = {
        LotStatus.CREATED: int(num_lots * 0.17),
        LotStatus.IN_PROGRESS: int(num_lots * 0.5),
        LotStatus.COMPLETED: int(num_lots * 0.25),
        LotStatus.CLOSED: int(num_lots * 0.08),
    }

    # Adjust to match exact count
    total = sum(status_counts.values())
    if total < num_lots:
        status_counts[LotStatus.IN_PROGRESS] += (num_lots - total)

    lots = []
    today = date.today()
    lot_sequence = 1

    for status, count in status_counts.items():
        for i in range(count):
            # Vary production date
            days_offset = random.randint(0, 30)
            production_date = today - timedelta(days=days_offset)

            product_model = random.choice(product_models)
            production_line = random.choice(production_lines)
            target_quantity = random.randint(10, 20)

            lot_number = generate_lot_number(
                production_line.line_code,
                product_model.model_code,
                production_date,
                lot_sequence
            )
            lot_sequence += 1

            # Determine quantities based on status
            if status == LotStatus.CREATED:
                actual_qty = 0
                passed_qty = 0
                failed_qty = 0
            elif status == LotStatus.IN_PROGRESS:
                actual_qty = random.randint(1, target_quantity - 1)
                passed_qty = int(actual_qty * random.uniform(0.3, 0.7))
                failed_qty = random.randint(0, min(2, actual_qty - passed_qty))
            else:  # COMPLETED or CLOSED
                actual_qty = target_quantity
                passed_qty = int(actual_qty * random.uniform(0.85, 0.95))
                failed_qty = actual_qty - passed_qty

            lot = Lot(
                lot_number=lot_number,
                product_model_id=product_model.id,
                production_line_id=production_line.id,
                production_date=production_date,
                target_quantity=target_quantity,
                actual_quantity=actual_qty,
                passed_quantity=passed_qty,
                failed_quantity=failed_qty,
                status=status.value,
                closed_at=datetime.now(timezone.utc) if status == LotStatus.CLOSED else None
            )
            db.add(lot)
            lots.append(lot)

    db.commit()
    print(f"   Created {len(lots)} LOTs.")
    return lots


def create_serials_and_wips(db: Session, lots: list[Lot], serials_per_lot: int) -> tuple[list[Serial], list[WIPItem]]:
    """Create Serials and WIP Items for each LOT."""
    print(f"Creating Serials and WIP Items ({serials_per_lot} per LOT)...")

    all_serials = []
    all_wips = []

    for lot in lots:
        if lot.status == LotStatus.CREATED.value:
            # CREATED LOTs have no serials yet
            continue

        num_items = min(serials_per_lot, lot.actual_quantity) if lot.actual_quantity > 0 else serials_per_lot

        for seq in range(1, num_items + 1):
            # Generate identifiers
            serial_number = generate_serial_number(lot.lot_number, seq)
            wip_id = generate_wip_id(lot.lot_number, seq)

            # Determine status based on LOT status
            if lot.status in [LotStatus.COMPLETED.value, LotStatus.CLOSED.value]:
                # Completed LOTs: mostly PASSED
                rand = random.random()
                if rand < 0.85:
                    serial_status = SerialStatus.PASSED
                    wip_status = WIPStatus.CONVERTED
                elif rand < 0.95:
                    serial_status = SerialStatus.FAILED
                    wip_status = WIPStatus.FAILED
                else:
                    serial_status = SerialStatus.PASSED
                    wip_status = WIPStatus.CONVERTED
            else:  # IN_PROGRESS
                rand = random.random()
                if rand < 0.2:
                    serial_status = SerialStatus.CREATED
                    wip_status = WIPStatus.CREATED
                elif rand < 0.5:
                    serial_status = SerialStatus.IN_PROGRESS
                    wip_status = WIPStatus.IN_PROGRESS
                elif rand < 0.8:
                    serial_status = SerialStatus.PASSED
                    wip_status = WIPStatus.CONVERTED
                else:
                    serial_status = SerialStatus.FAILED
                    wip_status = WIPStatus.FAILED

            # Failure reason for failed status
            failure_reason = None
            if serial_status == SerialStatus.FAILED:
                failure_reason = random.choice([
                    "Sensor test failed",
                    "Voltage out of range",
                    "Assembly defect",
                    "Firmware upload error",
                    "Visual inspection failed"
                ])

            # Create Serial
            serial = Serial(
                serial_number=serial_number,
                lot_id=lot.id,
                sequence_in_lot=seq,
                status=serial_status,
                rework_count=random.randint(0, 1) if serial_status == SerialStatus.FAILED else 0,
                failure_reason=failure_reason,
                completed_at=datetime.now(timezone.utc) if serial_status in [SerialStatus.PASSED, SerialStatus.FAILED] else None
            )
            db.add(serial)
            all_serials.append(serial)

            # Create WIP Item
            wip = WIPItem(
                wip_id=wip_id,
                lot_id=lot.id,
                sequence_in_lot=seq,
                status=wip_status.value,
                completed_at=datetime.now(timezone.utc) if wip_status == WIPStatus.COMPLETED else None,
                converted_at=datetime.now(timezone.utc) if wip_status == WIPStatus.CONVERTED else None
            )
            db.add(wip)
            all_wips.append(wip)

    db.commit()

    # Link WIP to Serial for converted items
    for i, wip in enumerate(all_wips):
        if wip.status == WIPStatus.CONVERTED.value and i < len(all_serials):
            wip.serial_id = all_serials[i].id

    db.commit()

    print(f"   Created {len(all_serials)} Serials and {len(all_wips)} WIP Items.")
    return all_serials, all_wips


def create_process_data(db: Session, serials: list[Serial], wips: list[WIPItem],
                        processes: list[Process], users: list[User],
                        equipment_list: list[Equipment], lots: list[Lot]):
    """Create ProcessData and WIPProcessHistory records."""
    print("Creating ProcessData and WIPProcessHistory...")

    operators = [u for u in users if u.role == UserRole.OPERATOR]
    if not operators:
        operators = users

    # Build equipment map
    equipment_map = {}
    for eq in equipment_list:
        key = (eq.process_id, eq.production_line_id)
        equipment_map[key] = eq

    # Build lot map
    lot_map = {lot.id: lot for lot in lots}

    process_data_count = 0
    wip_history_count = 0

    # Process Data for Serials (process 7, 8)
    for serial in serials:
        if serial.status == SerialStatus.CREATED:
            continue

        lot = lot_map.get(serial.lot_id)
        if not lot:
            continue

        # Completed serials go through process 7, 8
        if serial.status in [SerialStatus.PASSED, SerialStatus.FAILED]:
            completed_processes = [p for p in processes if p.process_number >= 7]
        else:
            # IN_PROGRESS might be at process 7
            completed_processes = [p for p in processes if p.process_number == 7]

        base_time = datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))

        for i, process in enumerate(completed_processes):
            duration = process.estimated_duration_seconds or 60
            started_at = base_time + timedelta(minutes=i * 10)
            completed_at = started_at + timedelta(seconds=duration)

            # Result
            is_last = (i == len(completed_processes) - 1)
            if serial.status == SerialStatus.FAILED and is_last:
                result = ProcessResult.FAIL
            else:
                result = ProcessResult.PASS

            equipment = equipment_map.get((process.id, lot.production_line_id))

            process_data = ProcessData(
                lot_id=lot.id,
                serial_id=serial.id,
                process_id=process.id,
                operator_id=random.choice(operators).id,
                equipment_id=equipment.id if equipment else None,
                data_level=DataLevel.SERIAL,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                result=result,
                measurements={"test": "value"},
                defects=None
            )
            db.add(process_data)
            process_data_count += 1

    # WIP Process History (process 1-6)
    for wip in wips:
        if wip.status == WIPStatus.CREATED.value:
            continue

        lot = lot_map.get(wip.lot_id)
        if not lot:
            continue

        # Determine how many processes completed
        if wip.status in [WIPStatus.COMPLETED.value, WIPStatus.CONVERTED.value]:
            num_processes = 6  # All WIP processes
        elif wip.status == WIPStatus.FAILED.value:
            num_processes = random.randint(1, 5)
        else:  # IN_PROGRESS
            num_processes = random.randint(1, 5)

        base_time = datetime.now(timezone.utc) - timedelta(hours=random.randint(2, 72))
        wip_processes = [p for p in processes if p.process_number <= 6][:num_processes]

        for i, process in enumerate(wip_processes):
            duration = process.estimated_duration_seconds or 60
            started_at = base_time + timedelta(minutes=i * 15)
            completed_at = started_at + timedelta(seconds=duration)

            is_last = (i == len(wip_processes) - 1)
            if wip.status == WIPStatus.FAILED.value and is_last:
                result = "FAIL"
            else:
                result = "PASS"

            equipment = equipment_map.get((process.id, lot.production_line_id))

            wip_history = WIPProcessHistory(
                wip_item_id=wip.id,
                process_id=process.id,
                operator_id=random.choice(operators).id,
                equipment_id=equipment.id if equipment else None,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                result=result,
                measurements={"test": "value"},
                defects=None
            )
            db.add(wip_history)
            wip_history_count += 1

        # Update WIP current_process_id
        if wip_processes:
            wip.current_process_id = wip_processes[-1].id

    db.commit()
    print(f"   Created {process_data_count} ProcessData records.")
    print(f"   Created {wip_history_count} WIPProcessHistory records.")


def print_summary(db: Session):
    """Print summary of generated data."""
    print("\n" + "=" * 60)
    print("Performance Test Data Generation Summary")
    print("=" * 60)

    users_count = db.query(User).count()
    processes_count = db.query(Process).count()
    models_count = db.query(ProductModel).count()
    lines_count = db.query(ProductionLine).count()
    equipment_count = db.query(Equipment).count()
    lots_count = db.query(Lot).count()
    serials_count = db.query(Serial).count()
    wips_count = db.query(WIPItem).count()
    process_data_count = db.query(ProcessData).count()
    wip_history_count = db.query(WIPProcessHistory).count()

    print(f"\nMaster Data:")
    print(f"  Users:            {users_count}")
    print(f"  Processes:        {processes_count}")
    print(f"  Product Models:   {models_count}")
    print(f"  Production Lines: {lines_count}")
    print(f"  Equipment:        {equipment_count}")

    print(f"\nTransaction Data:")
    print(f"  LOTs:             {lots_count}")
    print(f"  Serials:          {serials_count}")
    print(f"  WIP Items:        {wips_count}")
    print(f"  ProcessData:      {process_data_count}")
    print(f"  WIPProcessHistory:{wip_history_count}")

    print("\nLOT Status Distribution:")
    for status in [LotStatus.CREATED, LotStatus.IN_PROGRESS, LotStatus.COMPLETED, LotStatus.CLOSED]:
        count = db.query(Lot).filter(Lot.status == status.value).count()
        print(f"  - {status.value}: {count}")

    print("\nSerial Status Distribution:")
    for status in SerialStatus:
        count = db.query(Serial).filter(Serial.status == status).count()
        print(f"  - {status.value}: {count}")

    print("\n" + "=" * 60)
    print("Performance test data is ready!")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Generate performance test data")
    parser.add_argument("--reset", action="store_true", help="Clear existing transaction data first")
    parser.add_argument("--lots", type=int, default=60, help="Number of LOTs to create (default: 60)")
    parser.add_argument("--serials-per-lot", type=int, default=10, help="Serials per LOT (default: 10)")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("F2X NeuroHub MES - Performance Test Data Generator")
    print("=" * 60)
    print(f"LOTs: {args.lots}")
    print(f"Serials per LOT: {args.serials_per_lot}")
    print(f"Expected total Serials: ~{args.lots * args.serials_per_lot}")
    print(f"Reset: {args.reset}")
    print("=" * 60 + "\n")

    db = SessionLocal()

    try:
        if args.reset:
            clear_data(db)

        # Ensure master data exists
        users = ensure_users(db)
        processes = ensure_processes(db)
        product_models = ensure_product_models(db)
        production_lines = ensure_production_lines(db)
        equipment = ensure_equipment(db, processes, production_lines)

        # Create transaction data
        lots = create_lots(db, product_models, production_lines, args.lots)
        serials, wips = create_serials_and_wips(db, lots, args.serials_per_lot)
        create_process_data(db, serials, wips, processes, users, equipment, lots)

        print_summary(db)

    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
