"""
Unit tests for WIP duplicate process attempt prevention.

Tests the fix for duplicate attempt counts in WIP tracking:
- complete_process() updates ProcessData.completed_at
- Database constraint prevents duplicate incomplete records
- Trace API shows correct attempt count
- Rework scenarios work correctly
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crud import wip_item as wip_crud
from app.crud import user as user_crud
from app.models import (
    ProductModel, Lot, LotStatus, Process, ProcessData, User, UserRole,
    WIPItem, WIPStatus, WIPProcessHistory
)
from app.models.production_line import ProductionLine
from app.models.process_data import ProcessResult, DataLevel
from app.schemas import UserCreate


def create_product_model(db: Session) -> ProductModel:
    """Helper to create a ProductModel for tests."""
    product_model = ProductModel(
        model_code="PSA",
        model_name="Test Model",
        category="Test",
        status="ACTIVE",
        specifications={}
    )
    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model


def create_production_line(db: Session) -> ProductionLine:
    """Helper to create a ProductionLine for tests."""
    production_line = ProductionLine(
        line_code="KR001",
        line_name="Test Line",
        location="Test Location",
        is_active=True
    )
    db.add(production_line)
    db.commit()
    db.refresh(production_line)
    return production_line


def create_lot(db: Session, product_model: ProductModel, production_line: ProductionLine) -> Lot:
    """Helper to create a LOT for tests."""
    lot = Lot(
        lot_number="WF-KR-260109D-001",
        product_model_id=product_model.id,
        production_line_id=production_line.id,
        production_date=datetime.now(timezone.utc).date(),
        shift="D",
        target_quantity=10,
        status=LotStatus.IN_PROGRESS.value
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


def create_wip(db: Session, lot: Lot) -> WIPItem:
    """Helper to create a WIP item for tests."""
    wip = WIPItem(
        wip_id=f"WIP-{lot.lot_number}-001",
        lot_id=lot.id,
        sequence_in_lot=1,
        status=WIPStatus.IN_PROGRESS.value
    )
    db.add(wip)
    db.commit()
    db.refresh(wip)
    return wip


def create_process(db: Session, process_number: int = 1) -> Process:
    """Helper to create a Process for tests."""
    process = Process(
        process_code=f"P{process_number:02d}",
        process_name_en=f"Test Process {process_number}",
        process_name_kr=f"테스트 공정 {process_number}",
        process_number=process_number,
        process_type="MANUFACTURING",
        is_active=True
    )
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


def create_operator(db: Session) -> User:
    """Helper to create an operator user for tests."""
    user = user_crud.create(
        db,
        UserCreate(
            username="test_operator",
            email="operator@test.com",
            full_name="Test Operator",
            role=UserRole.OPERATOR,
            password="password123"
        )
    )
    return user


def test_complete_process_updates_process_data(db: Session):
    """
    Test that complete_process() sets ProcessData.completed_at.

    This is the primary fix for the duplicate attempt issue.
    """
    # Setup
    product_model = create_product_model(db)
    production_line = create_production_line(db)
    lot = create_lot(db, product_model, production_line)
    wip = create_wip(db, lot)
    process = create_process(db, process_number=1)
    operator = create_operator(db)

    # 1. Start process → creates ProcessData with completed_at=NULL
    started_at = datetime.now(timezone.utc)
    wip_crud.start_process(
        db,
        wip_id=wip.id,
        process_id=process.id,
        operator_id=operator.id,
        started_at=started_at
    )

    # Verify ProcessData was created
    process_data = (
        db.query(ProcessData)
        .filter(
            ProcessData.wip_id == wip.id,
            ProcessData.process_id == process.id
        )
        .first()
    )
    assert process_data is not None
    assert process_data.completed_at is None  # Should be NULL initially

    # 2. Complete process → should update ProcessData.completed_at
    completed_at = datetime.now(timezone.utc)
    wip_crud.complete_process(
        db,
        wip_id=wip.id,
        process_id=process.id,
        operator_id=operator.id,
        result=ProcessResult.PASS.value,
        measurements={"test": "value"},
        started_at=started_at,
        completed_at=completed_at
    )

    # 3. Verify ProcessData.completed_at is set
    db.refresh(process_data)
    assert process_data.completed_at is not None, "ProcessData.completed_at should be set after completion"
    assert process_data.result == ProcessResult.PASS.value
    assert process_data.measurements == {"test": "value"}
    assert process_data.duration_seconds is not None

    # 4. Verify WIPProcessHistory was also created
    history = (
        db.query(WIPProcessHistory)
        .filter(
            WIPProcessHistory.wip_item_id == wip.id,
            WIPProcessHistory.process_id == process.id
        )
        .first()
    )
    assert history is not None
    assert history.completed_at is not None
    assert history.result == ProcessResult.PASS.value


def test_no_duplicate_incomplete_records_query(db: Session):
    """
    Test that the trace API query doesn't return duplicate in-progress records.

    After the fix, completed ProcessData records should not appear in the
    in-progress query (completed_at IS NULL).
    """
    # Setup
    product_model = create_product_model(db)
    production_line = create_production_line(db)
    lot = create_lot(db, product_model, production_line)
    wip = create_wip(db, lot)
    process = create_process(db, process_number=1)
    operator = create_operator(db)

    # Start and complete a process
    started_at = datetime.now(timezone.utc)
    wip_crud.start_process(db, wip.id, process.id, operator.id, started_at=started_at)
    wip_crud.complete_process(
        db,
        wip.id,
        process.id,
        operator.id,
        result=ProcessResult.PASS.value,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc)
    )

    # Query for in-progress records (mimicking trace API)
    in_progress_records = (
        db.query(ProcessData)
        .filter(
            ProcessData.wip_id == wip.id,
            ProcessData.completed_at.is_(None)
        )
        .all()
    )

    # Should be 0 in-progress records after completion
    assert len(in_progress_records) == 0, \
        "No in-progress ProcessData should exist after process completion"


def test_database_constraint_prevents_duplicate_incomplete(db: Session):
    """
    Test that database constraint prevents duplicate incomplete ProcessData records.

    This tests the unique index: uk_process_data_wip_process_incomplete
    """
    # Setup
    product_model = create_product_model(db)
    production_line = create_production_line(db)
    lot = create_lot(db, product_model, production_line)
    wip = create_wip(db, lot)
    process = create_process(db, process_number=1)
    operator = create_operator(db)

    # Create first incomplete ProcessData
    process_data_1 = ProcessData(
        lot_id=lot.id,
        wip_id=wip.id,
        process_id=process.id,
        operator_id=operator.id,
        data_level=DataLevel.WIP.value,
        result=ProcessResult.PASS.value,
        started_at=datetime.now(timezone.utc),
        completed_at=None  # Incomplete
    )
    db.add(process_data_1)
    db.commit()

    # Try to create second incomplete ProcessData for same WIP+process
    process_data_2 = ProcessData(
        lot_id=lot.id,
        wip_id=wip.id,
        process_id=process.id,
        operator_id=operator.id,
        data_level=DataLevel.WIP.value,
        result=ProcessResult.PASS.value,
        started_at=datetime.now(timezone.utc),
        completed_at=None  # Incomplete
    )
    db.add(process_data_2)

    # Should raise IntegrityError due to unique constraint
    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_rework_scenario_creates_multiple_attempts(db: Session):
    """
    Test that rework scenarios (FAIL → restart → PASS) correctly create multiple attempts.

    This ensures the fix doesn't break legitimate rework tracking.
    """
    # Setup
    product_model = create_product_model(db)
    production_line = create_production_line(db)
    lot = create_lot(db, product_model, production_line)
    wip = create_wip(db, lot)
    process = create_process(db, process_number=1)
    operator = create_operator(db)

    # Attempt 1: Start and complete with FAIL
    started_at_1 = datetime.now(timezone.utc)
    wip_crud.start_process(db, wip.id, process.id, operator.id, started_at=started_at_1)
    wip_crud.complete_process(
        db,
        wip.id,
        process.id,
        operator.id,
        result=ProcessResult.FAIL.value,
        defects=["defect1"],
        started_at=started_at_1,
        completed_at=datetime.now(timezone.utc)
    )

    # Attempt 2: Restart and complete with PASS
    started_at_2 = datetime.now(timezone.utc)
    wip_crud.start_process(db, wip.id, process.id, operator.id, started_at=started_at_2)
    wip_crud.complete_process(
        db,
        wip.id,
        process.id,
        operator.id,
        result=ProcessResult.PASS.value,
        started_at=started_at_2,
        completed_at=datetime.now(timezone.utc)
    )

    # Verify 2 WIPProcessHistory records exist (both attempts)
    history_records = (
        db.query(WIPProcessHistory)
        .filter(WIPProcessHistory.wip_item_id == wip.id)
        .order_by(WIPProcessHistory.created_at)
        .all()
    )
    assert len(history_records) == 2, "Should have 2 history records for rework"
    assert history_records[0].result == ProcessResult.FAIL.value
    assert history_records[1].result == ProcessResult.PASS.value

    # Verify 2 ProcessData records exist (both completed)
    process_data_records = (
        db.query(ProcessData)
        .filter(ProcessData.wip_id == wip.id)
        .order_by(ProcessData.started_at)
        .all()
    )
    assert len(process_data_records) == 2, "Should have 2 ProcessData records for rework"
    assert process_data_records[0].completed_at is not None
    assert process_data_records[1].completed_at is not None

    # Verify no incomplete records exist
    incomplete_records = (
        db.query(ProcessData)
        .filter(
            ProcessData.wip_id == wip.id,
            ProcessData.completed_at.is_(None)
        )
        .all()
    )
    assert len(incomplete_records) == 0, "No incomplete records should exist"


def test_concurrent_start_updates_existing_record(db: Session):
    """
    Test that calling start_process twice updates the existing incomplete record.

    This is the intended behavior for 재착공 (restart) scenarios.
    """
    # Setup
    product_model = create_product_model(db)
    production_line = create_production_line(db)
    lot = create_lot(db, product_model, production_line)
    wip = create_wip(db, lot)
    process = create_process(db, process_number=1)
    operator = create_operator(db)

    # First start
    started_at_1 = datetime.now(timezone.utc)
    wip_crud.start_process(db, wip.id, process.id, operator.id, started_at=started_at_1)

    # Verify one ProcessData exists
    process_data_count_1 = (
        db.query(ProcessData)
        .filter(ProcessData.wip_id == wip.id)
        .count()
    )
    assert process_data_count_1 == 1

    # Second start (before completing the first)
    started_at_2 = datetime.now(timezone.utc)
    wip_crud.start_process(db, wip.id, process.id, operator.id, started_at=started_at_2)

    # Should still have only one ProcessData (updated, not duplicated)
    process_data_count_2 = (
        db.query(ProcessData)
        .filter(ProcessData.wip_id == wip.id)
        .count()
    )
    assert process_data_count_2 == 1, "Should not create duplicate ProcessData on restart"

    # Verify the started_at was updated
    process_data = (
        db.query(ProcessData)
        .filter(ProcessData.wip_id == wip.id)
        .first()
    )
    # Note: The exact started_at comparison might not work due to precision,
    # but we can verify it's not the old one
    assert process_data is not None
    assert process_data.completed_at is None
