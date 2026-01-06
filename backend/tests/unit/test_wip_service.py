"""
Unit tests for WIP Service business rules (BR-001 through BR-006).

Tests cover:
    - BR-001: LOT status validation for WIP generation
    - BR-002: Auto-transition LOT to IN_PROGRESS (tested via CRUD)
    - BR-003: Process sequence validation
    - BR-004: Duplicate PASS result prevention
    - BR-005: Serial conversion requirements
    - BR-006: WIP ID format validation (tested via utils)
"""

import pytest
from sqlalchemy.orm import Session

from app.services.wip_service import (
    WIPValidationError,
    validate_lot_for_wip_generation,
    validate_process_start,
    validate_process_completion,
    validate_serial_conversion,
    can_start_process,
    get_completed_processes,
    get_next_process,
    calculate_wip_completion_rate,
)
from app.models.lot import Lot, LotStatus, Shift
from app.models.wip_item import WIPItem, WIPStatus
from app.models.wip_process_history import WIPProcessHistory, ProcessResult
from app.models.process import Process
from app.models.product_model import ProductModel
from app.models.production_line import ProductionLine
from app.models.user import User, UserRole
from app.models.serial import Serial, SerialStatus


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_user(db: Session) -> User:
    """Create test user for FK references."""
    user = User(
        username="test_operator",
        email="testop@test.com",
        password_hash="$2b$12$dummy",
        full_name="Test Operator",
        role=UserRole.OPERATOR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def product_model(db: Session) -> ProductModel:
    """Create test product model."""
    pm = ProductModel(
        model_code="TST",
        model_name="Test Model / 테스트 모델",
        category="Standard",
        production_cycle_days=5,
        specifications={},
        status="ACTIVE"
    )
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@pytest.fixture
def production_line(db: Session) -> ProductionLine:
    """Create test production line."""
    line = ProductionLine(
        line_code="L01",
        line_name="Line 1 / 라인 1",
        cycle_time_sec=3600,  # 1 hour
        location="Factory A",
        is_active=True
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@pytest.fixture
def processes(db: Session) -> list[Process]:
    """Create test processes 1-6."""
    process_list = []
    for i in range(1, 7):
        process = Process(
            process_number=i,
            process_code=f"P{i:02d}",
            process_name_en=f"Process {i}",
            process_name_ko=f"공정 {i}",
            estimated_duration_seconds=60,
            sort_order=i,
            is_active=True
        )
        db.add(process)
        process_list.append(process)

    db.commit()
    for p in process_list:
        db.refresh(p)
    return process_list


@pytest.fixture
def lot_created(db: Session, product_model: ProductModel, production_line: ProductionLine) -> Lot:
    """Create LOT in CREATED status."""
    from datetime import date
    lot = Lot(
        lot_number="KR01TST2511",
        product_model_id=product_model.id,
        production_line_id=production_line.id,
        production_date=date.today(),
        target_quantity=10,
        status=LotStatus.CREATED.value,
        shift=Shift.DAY.value
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@pytest.fixture
def lot_in_progress(db: Session, product_model: ProductModel, production_line: ProductionLine) -> Lot:
    """Create LOT in IN_PROGRESS status."""
    from datetime import date
    lot = Lot(
        lot_number="KR01TST2512",
        product_model_id=product_model.id,
        production_line_id=production_line.id,
        production_date=date.today(),
        target_quantity=10,
        status=LotStatus.IN_PROGRESS.value,
        shift=Shift.DAY.value
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@pytest.fixture
def wip_item(db: Session, lot_in_progress: Lot, processes: list[Process]) -> WIPItem:
    """Create WIP item for testing."""
    wip = WIPItem(
        wip_id="WIP-KR01TST2512-001",
        lot_id=lot_in_progress.id,
        sequence_in_lot=1,
        status=WIPStatus.CREATED.value,
        current_process_id=None
    )
    db.add(wip)
    db.commit()
    db.refresh(wip)
    return wip


# ============================================================================
# BR-001: LOT Status Validation for WIP Generation
# ============================================================================

def test_validate_lot_for_wip_generation_success(db: Session, lot_created: Lot):
    """BR-001: Valid LOT in CREATED status should pass validation."""
    # Should not raise exception
    validate_lot_for_wip_generation(db, lot_created, 5)


def test_validate_lot_for_wip_generation_wrong_status(db: Session, lot_in_progress: Lot):
    """BR-001: LOT not in CREATED status should fail validation."""
    with pytest.raises(WIPValidationError) as exc_info:
        validate_lot_for_wip_generation(db, lot_in_progress, 5)

    assert "CREATED status" in str(exc_info.value)
    assert "IN_PROGRESS" in str(exc_info.value)


def test_validate_lot_for_wip_generation_invalid_quantity(db: Session, lot_created: Lot):
    """BR-001: Invalid quantity should fail validation."""
    # Too small
    with pytest.raises(WIPValidationError) as exc_info:
        validate_lot_for_wip_generation(db, lot_created, 0)
    assert "between 1 and 100" in str(exc_info.value)

    # Too large
    with pytest.raises(WIPValidationError) as exc_info:
        validate_lot_for_wip_generation(db, lot_created, 101)
    assert "between 1 and 100" in str(exc_info.value)


def test_validate_lot_for_wip_generation_exceeds_target(db: Session, lot_created: Lot):
    """BR-001: Quantity exceeding target should fail validation."""
    with pytest.raises(WIPValidationError) as exc_info:
        validate_lot_for_wip_generation(db, lot_created, 20)  # target is 10

    assert "exceeds LOT target_quantity" in str(exc_info.value)


def test_validate_lot_for_wip_generation_already_has_wips(db: Session, lot_created: Lot):
    """BR-001: LOT with existing WIPs should fail validation."""
    # Create existing WIP
    wip = WIPItem(
        wip_id="WIP-KR01TST2511-001",
        lot_id=lot_created.id,
        sequence_in_lot=1,
        status=WIPStatus.CREATED.value
    )
    db.add(wip)
    db.commit()

    with pytest.raises(WIPValidationError) as exc_info:
        validate_lot_for_wip_generation(db, lot_created, 5)

    assert "already has" in str(exc_info.value)
    assert "WIP IDs" in str(exc_info.value)


# ============================================================================
# BR-003: Process Sequence Validation
# ============================================================================

def test_validate_process_start_process1_success(db: Session, wip_item: WIPItem, processes: list[Process]):
    """BR-003: Process 1 should always be startable for CREATED WIP."""
    # Should not raise exception
    validate_process_start(db, wip_item, processes[0].id, 1)


def test_validate_process_start_process2_without_process1(db: Session, wip_item: WIPItem, processes: list[Process]):
    """BR-003: Process 2 should fail without Process 1 PASS."""
    with pytest.raises(WIPValidationError) as exc_info:
        validate_process_start(db, wip_item, processes[1].id, 2)

    assert "cannot start process 2" in str(exc_info.value)
    assert "Previous process 1 must be completed" in str(exc_info.value)


def test_validate_process_start_process2_with_process1_pass(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """BR-003: Process 2 should succeed with Process 1 PASS."""
    # Add Process 1 PASS result
    history = WIPProcessHistory(
        wip_item_id=wip_item.id,
        process_id=processes[0].id,
        operator_id=test_user.id,
        result=ProcessResult.PASS.value,
        started_at="2025-01-01 10:00:00",
        completed_at="2025-01-01 10:05:00"
    )
    db.add(history)
    db.commit()

    # Update WIP status
    wip_item.status = WIPStatus.IN_PROGRESS.value
    db.commit()

    # Should not raise exception
    validate_process_start(db, wip_item, processes[1].id, 2)


def test_validate_process_start_failed_wip_allowed(db: Session, wip_item: WIPItem, processes: list[Process]):
    """BR-003: FAILED WIP can start process (re-work/착공 재시도)."""
    wip_item.status = WIPStatus.FAILED.value
    db.commit()

    # Should NOT raise - FAILED WIP can re-start process 1
    validate_process_start(db, wip_item, processes[0].id, 1)


def test_validate_process_start_converted_wip(db: Session, wip_item: WIPItem, processes: list[Process]):
    """BR-003: CONVERTED WIP should not start any process."""
    wip_item.status = WIPStatus.CONVERTED.value
    db.commit()

    with pytest.raises(WIPValidationError) as exc_info:
        validate_process_start(db, wip_item, processes[0].id, 1)

    assert "already converted" in str(exc_info.value)


# ============================================================================
# BR-004: Duplicate PASS Result Prevention
# ============================================================================

def test_validate_process_completion_pass_success(db: Session, wip_item: WIPItem, processes: list[Process]):
    """BR-004: First PASS result should succeed."""
    # Should not raise exception
    validate_process_completion(db, wip_item, processes[0].id, ProcessResult.PASS.value)


def test_validate_process_completion_duplicate_pass(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """BR-004: Duplicate PASS result should fail."""
    # Add first PASS result
    history = WIPProcessHistory(
        wip_item_id=wip_item.id,
        process_id=processes[0].id,
        operator_id=test_user.id,
        result=ProcessResult.PASS.value,
        started_at="2025-01-01 10:00:00",
        completed_at="2025-01-01 10:05:00"
    )
    db.add(history)
    db.commit()

    # Try to add second PASS result
    with pytest.raises(WIPValidationError) as exc_info:
        validate_process_completion(db, wip_item, processes[0].id, ProcessResult.PASS.value)

    assert "already has PASS result" in str(exc_info.value)
    assert "Duplicate PASS results are not allowed" in str(exc_info.value)


def test_validate_process_completion_multiple_fails_allowed(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """BR-004: Multiple FAIL results should be allowed."""
    # Add first FAIL result
    history1 = WIPProcessHistory(
        wip_item_id=wip_item.id,
        process_id=processes[0].id,
        operator_id=test_user.id,
        result=ProcessResult.FAIL.value,
        started_at="2025-01-01 10:00:00",
        completed_at="2025-01-01 10:05:00"
    )
    db.add(history1)
    db.commit()

    # Add second FAIL result - should not raise exception
    validate_process_completion(db, wip_item, processes[0].id, ProcessResult.FAIL.value)


# ============================================================================
# BR-005: Serial Conversion Requirements
# ============================================================================

def test_validate_serial_conversion_success(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """BR-005: WIP with all processes 1-6 PASS should pass validation."""
    # Mark WIP as COMPLETED
    wip_item.status = WIPStatus.COMPLETED.value
    db.commit()

    # Add PASS results for all processes 1-6
    for process in processes:
        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=test_user.id,
            result=ProcessResult.PASS.value,
            started_at="2025-01-01 10:00:00",
            completed_at="2025-01-01 10:05:00"
        )
        db.add(history)
    db.commit()

    # Should not raise exception
    validate_serial_conversion(db, wip_item)


def test_validate_serial_conversion_not_completed(db: Session, wip_item: WIPItem):
    """BR-005: Non-COMPLETED WIP should fail validation."""
    with pytest.raises(WIPValidationError) as exc_info:
        validate_serial_conversion(db, wip_item)

    assert "must be in COMPLETED status" in str(exc_info.value)


def test_validate_serial_conversion_missing_processes(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """BR-005: WIP missing some process PASS results should fail."""
    # Mark WIP as COMPLETED
    wip_item.status = WIPStatus.COMPLETED.value
    db.commit()

    # Add PASS results for only processes 1-4 (missing 5-6)
    for process in processes[:4]:
        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=test_user.id,
            result=ProcessResult.PASS.value,
            started_at="2025-01-01 10:00:00",
            completed_at="2025-01-01 10:05:00"
        )
        db.add(history)
    db.commit()

    with pytest.raises(WIPValidationError) as exc_info:
        validate_serial_conversion(db, wip_item)

    assert "Missing PASS results for processes" in str(exc_info.value)
    assert "[5, 6]" in str(exc_info.value)


def test_validate_serial_conversion_already_converted(db: Session, wip_item: WIPItem, processes: list[Process], lot_created: Lot):
    """BR-005: Already converted WIP should fail validation."""
    # Create a dummy serial for FK constraint
    dummy_serial = Serial(
        serial_number="KR01TST2511TEST",
        lot_id=lot_created.id,
        sequence_in_lot=1,
        status=SerialStatus.CREATED.value
    )
    db.add(dummy_serial)
    db.commit()
    db.refresh(dummy_serial)

    # Mark WIP as COMPLETED and set serial_id
    wip_item.status = WIPStatus.COMPLETED.value
    wip_item.serial_id = dummy_serial.id
    db.commit()

    with pytest.raises(WIPValidationError) as exc_info:
        validate_serial_conversion(db, wip_item)

    assert "already converted" in str(exc_info.value)


# ============================================================================
# Helper Functions Tests
# ============================================================================

def test_can_start_process(db: Session, wip_item: WIPItem, processes: list[Process]):
    """Test can_start_process helper function."""
    # Process 1 should be startable
    can_start, error = can_start_process(db, wip_item, 1)
    assert can_start is True
    assert error is None

    # Process 2 should not be startable (no Process 1 PASS)
    can_start, error = can_start_process(db, wip_item, 2)
    assert can_start is False
    assert "Previous process 1 must be completed" in error


def test_get_completed_processes(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """Test get_completed_processes helper function."""
    # Initially no completed processes
    completed = get_completed_processes(db, wip_item)
    assert completed == []

    # Add PASS results for processes 1 and 2
    for process in processes[:2]:
        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=test_user.id,
            result=ProcessResult.PASS.value,
            started_at="2025-01-01 10:00:00",
            completed_at="2025-01-01 10:05:00"
        )
        db.add(history)
    db.commit()

    completed = get_completed_processes(db, wip_item)
    assert completed == [1, 2]


def test_get_next_process(db: Session, wip_item: WIPItem, processes: list[Process], test_user: User):
    """Test get_next_process helper function."""
    # Initially next process should be 1
    next_proc = get_next_process(db, wip_item)
    assert next_proc == 1

    # Add PASS results for processes 1, 2, 3
    for process in processes[:3]:
        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=test_user.id,
            result=ProcessResult.PASS.value,
            started_at="2025-01-01 10:00:00",
            completed_at="2025-01-01 10:05:00"
        )
        db.add(history)
    db.commit()

    # Next process should be 4
    next_proc = get_next_process(db, wip_item)
    assert next_proc == 4

    # Complete all processes
    for process in processes[3:]:
        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=test_user.id,
            result=ProcessResult.PASS.value,
            started_at="2025-01-01 10:00:00",
            completed_at="2025-01-01 10:05:00"
        )
        db.add(history)
    db.commit()

    # All completed, next process should be None
    next_proc = get_next_process(db, wip_item)
    assert next_proc is None


def test_calculate_wip_completion_rate(db: Session, lot_in_progress: Lot):
    """Test calculate_wip_completion_rate helper function."""
    # Create 3 WIPs with different statuses
    wip1 = WIPItem(
        wip_id="WIP-KR01TST2512-001",
        lot_id=lot_in_progress.id,
        sequence_in_lot=1,
        status=WIPStatus.COMPLETED.value
    )
    wip2 = WIPItem(
        wip_id="WIP-KR01TST2512-002",
        lot_id=lot_in_progress.id,
        sequence_in_lot=2,
        status=WIPStatus.IN_PROGRESS.value
    )
    wip3 = WIPItem(
        wip_id="WIP-KR01TST2512-003",
        lot_id=lot_in_progress.id,
        sequence_in_lot=3,
        status=WIPStatus.CONVERTED.value
    )
    db.add_all([wip1, wip2, wip3])
    db.commit()

    stats = calculate_wip_completion_rate(db, lot_in_progress.id)

    assert stats["total"] == 3
    assert stats["completed"] == 1
    assert stats["in_progress"] == 1
    assert stats["converted"] == 1
    assert stats["failed"] == 0
    assert stats["completion_rate"] == 66.67  # (1 + 1) / 3 * 100
