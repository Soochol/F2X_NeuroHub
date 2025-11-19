"""
Unit tests for app/crud/process_data.py module.

Tests:
    - ProcessData CRUD operations (create, read, update, delete)
    - ProcessData-specific queries (get_by_serial, get_by_lot, get_by_process)
    - Result filtering (get_by_result, get_failures)
    - Operator and date range filtering
    - Count operations
"""

import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.crud import process_data as process_data_crud
from app.crud import serial as serial_crud
from app.crud import lot as lot_crud
from app.crud import user as user_crud
from app.models import (
    ProductModel, Lot, LotStatus, Process, ProcessData, User, UserRole
)
from app.models.process_data import ProcessResult, DataLevel
from app.schemas.process_data import ProcessDataCreate, ProcessDataUpdate, DataLevel as DataLevelSchema, ProcessResult as ProcessResultSchema
from app.schemas.lot import LotCreate
from app.schemas.serial import SerialCreate
from app.schemas import UserCreate


def create_product_model(db: Session) -> ProductModel:
    """Helper to create a ProductModel for tests."""
    product_model = ProductModel(
        model_code="NH-TEST-001",
        model_name="Test Model",
        category="Test",
        status="ACTIVE",
        specifications={}
    )
    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model


def create_lot(db: Session, product_model_id: int) -> Lot:
    """Helper to create a Lot for tests."""
    lot = Lot(
        lot_number="WF-KR-251118D-001",
        product_model_id=product_model_id,
        production_date=date(2025, 11, 18),
        shift="D",
        target_quantity=100,
        status=LotStatus.CREATED,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


def create_process(db: Session, process_number: int = 1) -> Process:
    """Helper to create a Process for tests."""
    process = Process(
        process_number=process_number,
        process_code=f"PROCESS_{process_number}",
        process_name_ko=f"프로세스 {process_number}",
        process_name_en=f"Process {process_number}",
        quality_criteria={},
        sort_order=process_number,
    )
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


def create_operator(db: Session, username: str = "operator1") -> User:
    """Helper to create an operator user for tests."""
    user_data = UserCreate(
        username=username,
        email=f"{username}@test.com",
        password="Password123!",
        full_name=f"Operator {username}",
        role=UserRole.OPERATOR,
    )
    user = user_crud.create(db, user_in=user_data)
    db.commit()
    db.refresh(user)
    return user


class TestProcessDataCreate:
    """Test ProcessData creation operations."""

    def test_create_process_data_serial_level(self, db: Session):
        """Test creating serial-level process data."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        serial = serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="IN_PROGRESS", rework_count=0
        ))

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=serial.id,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.SERIAL,
            result=ProcessResultSchema.PASS,
            measurements={"temperature": 25.5},
            started_at=now,
            completed_at=now + timedelta(seconds=60),
        )

        pd = process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        assert pd.id is not None
        assert pd.lot_id == lot.id
        assert pd.serial_id == serial.id
        assert pd.process_id == process.id
        assert pd.operator_id == operator.id
        assert pd.data_level == DataLevel.SERIAL.value
        assert pd.result == ProcessResult.PASS.value

    def test_create_process_data_lot_level(self, db: Session):
        """Test creating lot-level process data."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={"batch_temp": 30.0},
            started_at=now,
            completed_at=now + timedelta(seconds=120),
        )

        pd = process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        assert pd.id is not None
        assert pd.serial_id is None
        assert pd.data_level == DataLevel.LOT.value


class TestProcessDataRead:
    """Test ProcessData read operations."""

    def test_get_process_data_by_id(self, db: Session):
        """Test retrieving process data by ID."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
        )
        created = process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        retrieved = process_data_crud.get(db, process_data_id=created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_returns_none(self, db: Session):
        """Test getting nonexistent process data returns None."""
        pd = process_data_crud.get(db, process_data_id=99999)
        assert pd is None


class TestProcessDataGetBySerial:
    """Test get_by_serial functionality."""

    def test_get_by_serial(self, db: Session):
        """Test getting all process data for a serial."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process1 = create_process(db, process_number=1)
        process2 = create_process(db, process_number=2)
        operator = create_operator(db)

        serial = serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="IN_PROGRESS", rework_count=0
        ))

        now = datetime.utcnow()
        # Create 2 process data records for the serial
        for proc in [process1, process2]:
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=serial.id,
                process_id=proc.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.SERIAL,
                result=ProcessResultSchema.PASS,
                measurements={},
                started_at=now,
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        records = process_data_crud.get_by_serial(db, serial_id=serial.id)

        assert len(records) == 2
        assert all(r.serial_id == serial.id for r in records)


class TestProcessDataGetByLot:
    """Test get_by_lot functionality."""

    def test_get_by_lot(self, db: Session):
        """Test getting all process data for a lot."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create lot-level process data
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
        )
        process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        records = process_data_crud.get_by_lot(db, lot_id=lot.id)

        assert len(records) == 1
        assert records[0].lot_id == lot.id


class TestProcessDataGetByProcess:
    """Test get_by_process functionality."""

    def test_get_by_process(self, db: Session):
        """Test filtering process data by process type."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process1 = create_process(db, process_number=1)
        process2 = create_process(db, process_number=2)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create data for each process
        for proc in [process1, process2]:
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=None,
                process_id=proc.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.LOT,
                result=ProcessResultSchema.PASS,
                measurements={},
                started_at=now,
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        records = process_data_crud.get_by_process(db, process_id=process1.id)

        assert len(records) == 1
        assert records[0].process_id == process1.id


class TestProcessDataGetByResult:
    """Test get_by_result functionality."""

    def test_get_by_result_pass(self, db: Session):
        """Test filtering process data by PASS result."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create PASS and FAIL records
        for result in [ProcessResultSchema.PASS, ProcessResultSchema.FAIL]:
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=None,
                process_id=process.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.LOT,
                result=result,
                measurements={},
                defects={"code": "TEST"} if result == ProcessResultSchema.FAIL else None,
                started_at=now,
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        pass_records = process_data_crud.get_by_result(db, result=ProcessResult.PASS.value)

        assert len(pass_records) == 1
        assert pass_records[0].result == ProcessResult.PASS.value


class TestProcessDataGetFailures:
    """Test get_failures functionality."""

    def test_get_failures(self, db: Session):
        """Test getting failed process records."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create FAIL record
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.FAIL,
            measurements={},
            defects={"code": "DEFECT_001"},
            started_at=now,
        )
        process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        failures = process_data_crud.get_failures(db)

        assert len(failures) == 1
        assert failures[0].result == ProcessResult.FAIL.value


class TestProcessDataGetByOperator:
    """Test get_by_operator functionality."""

    def test_get_by_operator(self, db: Session):
        """Test filtering process data by operator."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator1 = create_operator(db, username="operator1")
        operator2 = create_operator(db, username="operator2")

        now = datetime.utcnow()
        # Create records for different operators
        for op in [operator1, operator2]:
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=None,
                process_id=process.id,
                operator_id=op.id,
                data_level=DataLevelSchema.LOT,
                result=ProcessResultSchema.PASS,
                measurements={},
                started_at=now,
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        records = process_data_crud.get_by_operator(db, operator_id=operator1.id)

        assert len(records) == 1
        assert records[0].operator_id == operator1.id


class TestProcessDataGetByDateRange:
    """Test get_by_date_range functionality."""

    def test_get_by_date_range(self, db: Session):
        """Test filtering process data by date range."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Create record for today
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
        )
        process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        records = process_data_crud.get_by_date_range(
            db,
            start_date=yesterday,
            end_date=tomorrow
        )

        assert len(records) == 1


class TestProcessDataCounts:
    """Test count operations."""

    def test_count_by_result(self, db: Session):
        """Test counting process data by result."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create 2 PASS and 1 FAIL records
        for i, result in enumerate([
            ProcessResultSchema.PASS, ProcessResultSchema.PASS, ProcessResultSchema.FAIL
        ]):
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=None,
                process_id=process.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.LOT,
                result=result,
                measurements={},
                defects={"code": "TEST"} if result == ProcessResultSchema.FAIL else None,
                started_at=now + timedelta(seconds=i),
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        pass_count = process_data_crud.count_by_result(db, result=ProcessResult.PASS.value)
        fail_count = process_data_crud.count_by_result(db, result=ProcessResult.FAIL.value)

        assert pass_count == 2
        assert fail_count == 1

    def test_count_by_process(self, db: Session):
        """Test counting process data by process."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create 3 records for the process
        for i in range(3):
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=None,
                process_id=process.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.LOT,
                result=ProcessResultSchema.PASS,
                measurements={},
                started_at=now + timedelta(seconds=i),
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        count = process_data_crud.count_by_process(db, process_id=process.id)

        assert count == 3

    def test_count_by_serial(self, db: Session):
        """Test counting process data by serial."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process1 = create_process(db, process_number=1)
        process2 = create_process(db, process_number=2)
        operator = create_operator(db)

        serial = serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="IN_PROGRESS", rework_count=0
        ))

        now = datetime.utcnow()
        # Create 2 records for the serial
        for proc in [process1, process2]:
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=serial.id,
                process_id=proc.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.SERIAL,
                result=ProcessResultSchema.PASS,
                measurements={},
                started_at=now,
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        count = process_data_crud.count_by_serial(db, serial_id=serial.id)

        assert count == 2


class TestProcessDataUpdate:
    """Test ProcessData update operations."""

    def test_update_process_data(self, db: Session):
        """Test updating process data."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
        )
        created = process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        update_data = ProcessDataUpdate(
            result=ProcessResultSchema.FAIL,
            defects={"code": "DEFECT_001"},
            completed_at=now + timedelta(seconds=30)
        )
        updated = process_data_crud.update(db, db_obj=created, obj_in=update_data)
        db.commit()

        assert updated.result == ProcessResult.FAIL.value
        assert updated.defects == {"code": "DEFECT_001"}
        assert updated.completed_at is not None


class TestProcessDataDelete:
    """Test ProcessData delete operations."""

    def test_delete_process_data(self, db: Session):
        """Test deleting process data."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
        )
        created = process_data_crud.create(db, obj_in=pd_data)
        db.commit()
        pd_id = created.id

        result = process_data_crud.delete(db, process_data_id=pd_id)
        db.commit()

        assert result is True
        assert process_data_crud.get(db, process_data_id=pd_id) is None

    def test_delete_nonexistent_returns_false(self, db: Session):
        """Test deleting nonexistent process data returns False."""
        result = process_data_crud.delete(db, process_data_id=99999)

        assert result is False


class TestProcessDataGetMulti:
    """Test get_multi functionality."""

    def test_get_multi_with_pagination(self, db: Session):
        """Test get_multi with pagination."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create 5 records
        for i in range(5):
            pd_data = ProcessDataCreate(
                lot_id=lot.id,
                serial_id=None,
                process_id=process.id,
                operator_id=operator.id,
                data_level=DataLevelSchema.LOT,
                result=ProcessResultSchema.PASS,
                measurements={},
                started_at=now + timedelta(seconds=i),
            )
            process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        page1 = process_data_crud.get_multi(db, skip=0, limit=2)
        page2 = process_data_crud.get_multi(db, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        # Verify no overlap
        page1_ids = {pd.id for pd in page1}
        page2_ids = {pd.id for pd in page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestProcessDataSpecializedQueries:
    """Test specialized query functions."""

    def test_get_by_serial_and_process(self, db: Session):
        """Test getting process data for specific serial and process."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        serial = serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="IN_PROGRESS", rework_count=0
        ))

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=serial.id,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.SERIAL,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
        )
        process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        record = process_data_crud.get_by_serial_and_process(
            db, serial_id=serial.id, process_id=process.id
        )

        assert record is not None
        assert record.serial_id == serial.id
        assert record.process_id == process.id

    def test_get_failures_by_process(self, db: Session):
        """Test getting failures for a specific process."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.FAIL,
            measurements={},
            defects={"code": "DEFECT_001"},
            started_at=now,
        )
        process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        failures = process_data_crud.get_failures_by_process(db, process_id=process.id)

        assert len(failures) == 1
        assert failures[0].process_id == process.id
        assert failures[0].result == ProcessResult.FAIL.value

    def test_get_incomplete_processes(self, db: Session):
        """Test getting in-progress process records."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        process = create_process(db)
        operator = create_operator(db)

        now = datetime.utcnow()
        # Create incomplete record (no completed_at)
        pd_data = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=None,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevelSchema.LOT,
            result=ProcessResultSchema.PASS,
            measurements={},
            started_at=now,
            completed_at=None,
        )
        process_data_crud.create(db, obj_in=pd_data)
        db.commit()

        incomplete = process_data_crud.get_incomplete_processes(db)

        assert len(incomplete) == 1
        assert incomplete[0].completed_at is None
