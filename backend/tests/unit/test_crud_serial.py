"""
Unit tests for app/crud/serial.py module.

Tests:
    - Serial CRUD operations (create, read, update, delete)
    - Serial-specific queries (get_by_number, get_by_lot, get_by_status)
    - Rework operations (get_failed, increment_rework, can_rework)
    - Status transitions and validations
    - Pagination and filtering
"""

import pytest
from datetime import date
from sqlalchemy.orm import Session

from app.crud import serial as serial_crud
from app.models import Serial, SerialStatus, ProductModel, Lot, LotStatus
from app.schemas import SerialCreate, SerialUpdate
from app.schemas.lot import LotCreate


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


class TestSerialCreate:
    """Test serial creation operations."""

    def test_create_serial_with_valid_data(self, db: Session):
        """Test creating a serial with valid data."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )

        serial = serial_crud.create(db, serial_data)

        assert serial.id is not None
        assert serial.lot_id == lot.id
        assert serial.sequence_in_lot == 1
        assert serial.status == SerialStatus.CREATED
        assert serial.rework_count == 0
        assert serial.serial_number == f"{lot.lot_number}-0001"

    def test_create_serial_generates_correct_serial_number(self, db: Session):
        """Test that serial numbers are correctly generated from lot number."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=42,
            status="CREATED",
            rework_count=0,
        )

        serial = serial_crud.create(db, serial_data)

        assert serial.serial_number == "WF-KR-251118D-001-0042"

    def test_create_serial_with_invalid_lot_raises_error(self, db: Session):
        """Test creating serial with invalid lot_id raises ValueError."""
        serial_data = SerialCreate(
            lot_id=99999,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )

        with pytest.raises(ValueError, match="Lot with ID 99999 not found"):
            serial_crud.create(db, serial_data)


class TestSerialRead:
    """Test serial read operations."""

    def test_get_serial_by_id(self, db: Session):
        """Test retrieving serial by ID."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        created = serial_crud.create(db, serial_data)

        retrieved = serial_crud.get(db, serial_id=created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_serial_returns_none(self, db: Session):
        """Test that getting nonexistent serial returns None."""
        serial = serial_crud.get(db, serial_id=99999)
        assert serial is None

    def test_get_by_number(self, db: Session):
        """Test retrieving serial by serial_number."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)
        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        created = serial_crud.create(db, serial_data)

        retrieved = serial_crud.get_by_number(db, serial_number=created.serial_number)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.serial_number == created.serial_number

    def test_get_by_number_not_found(self, db: Session):
        """Test get_by_number returns None for nonexistent serial."""
        serial = serial_crud.get_by_number(db, serial_number="NONEXISTENT-0001")
        assert serial is None


class TestSerialGetByLot:
    """Test get_by_lot functionality."""

    def test_get_by_lot_returns_all_serials(self, db: Session):
        """Test getting all serials in a lot."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create 3 serials
        for i in range(1, 4):
            serial_data = SerialCreate(
                lot_id=lot.id,
                sequence_in_lot=i,
                status="CREATED",
                rework_count=0,
            )
            serial_crud.create(db, serial_data)

        serials = serial_crud.get_by_lot(db, lot_id=lot.id)

        assert len(serials) == 3
        assert all(s.lot_id == lot.id for s in serials)

    def test_get_by_lot_with_pagination(self, db: Session):
        """Test pagination in get_by_lot."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create 5 serials
        for i in range(1, 6):
            serial_data = SerialCreate(
                lot_id=lot.id,
                sequence_in_lot=i,
                status="CREATED",
                rework_count=0,
            )
            serial_crud.create(db, serial_data)

        page1 = serial_crud.get_by_lot(db, lot_id=lot.id, skip=0, limit=2)
        page2 = serial_crud.get_by_lot(db, lot_id=lot.id, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].sequence_in_lot == 1
        assert page2[0].sequence_in_lot == 3

    def test_get_by_lot_empty_lot(self, db: Session):
        """Test get_by_lot for a lot with no serials."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serials = serial_crud.get_by_lot(db, lot_id=lot.id)

        assert len(serials) == 0


class TestSerialGetByStatus:
    """Test get_by_status functionality."""

    def test_get_by_status_returns_filtered_serials(self, db: Session):
        """Test filtering serials by status."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create serials with different statuses
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="CREATED", rework_count=0
        ))
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=2, status="IN_PROGRESS", rework_count=0
        ))

        created_serials = serial_crud.get_by_status(db, status="CREATED")
        in_progress_serials = serial_crud.get_by_status(db, status="IN_PROGRESS")

        assert all(s.status == SerialStatus.CREATED for s in created_serials)
        assert all(s.status == SerialStatus.IN_PROGRESS for s in in_progress_serials)

    def test_get_by_status_invalid_status_raises_error(self, db: Session):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="status must be one of"):
            serial_crud.get_by_status(db, status="INVALID")


class TestSerialGetMulti:
    """Test get_multi functionality."""

    def test_get_multi_with_status_filter(self, db: Session):
        """Test get_multi with status filtering."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create serials with different statuses
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="CREATED", rework_count=0
        ))
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=2, status="IN_PROGRESS", rework_count=0
        ))

        created_serials = serial_crud.get_multi(db, status="CREATED")

        assert len(created_serials) >= 1
        assert all(s.status == SerialStatus.CREATED for s in created_serials)

    def test_get_multi_invalid_status_raises_error(self, db: Session):
        """Test that invalid status in get_multi raises ValueError."""
        with pytest.raises(ValueError, match="status must be one of"):
            serial_crud.get_multi(db, status="INVALID")


class TestSerialGetFailed:
    """Test get_failed functionality for rework operations."""

    def test_get_failed_returns_rework_candidates(self, db: Session):
        """Test getting failed serials available for rework."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create failed serial with rework_count < 3
        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="FAILED",
            rework_count=1,
            failure_reason="Test failure"
        )
        serial_crud.create(db, serial_data)

        failed_serials = serial_crud.get_failed(db)

        assert len(failed_serials) == 1
        assert failed_serials[0].status == SerialStatus.FAILED
        assert failed_serials[0].rework_count < 3

    def test_get_failed_excludes_exhausted_reworks(self, db: Session):
        """Test that serials with 3 reworks are excluded."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create failed serial with rework_count = 3
        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="FAILED",
            rework_count=3,
            failure_reason="Test failure"
        )
        serial_crud.create(db, serial_data)

        failed_serials = serial_crud.get_failed(db)

        assert len(failed_serials) == 0


class TestSerialRework:
    """Test rework operations."""

    def test_increment_rework_success(self, db: Session):
        """Test incrementing rework count successfully."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        # Create failed serial
        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="FAILED",
            rework_count=0,
            failure_reason="Test failure"
        )
        serial = serial_crud.create(db, serial_data)

        reworked = serial_crud.increment_rework(db, serial_id=serial.id)

        assert reworked.rework_count == 1
        assert reworked.status == SerialStatus.IN_PROGRESS
        assert reworked.failure_reason is None

    def test_increment_rework_not_failed_raises_error(self, db: Session):
        """Test that rework on non-failed serial raises ValueError."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        with pytest.raises(ValueError, match="is not in FAILED status"):
            serial_crud.increment_rework(db, serial_id=serial.id)

    def test_increment_rework_max_exceeded_raises_error(self, db: Session):
        """Test that exceeding max rework raises ValueError."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="FAILED",
            rework_count=3,
            failure_reason="Test failure"
        )
        serial = serial_crud.create(db, serial_data)

        with pytest.raises(ValueError, match="exceeded maximum rework count"):
            serial_crud.increment_rework(db, serial_id=serial.id)

    def test_increment_rework_not_found_raises_error(self, db: Session):
        """Test that rework on nonexistent serial raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            serial_crud.increment_rework(db, serial_id=99999)

    def test_can_rework_true_for_eligible(self, db: Session):
        """Test can_rework returns True for eligible serial."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="FAILED",
            rework_count=1,
            failure_reason="Test failure"
        )
        serial = serial_crud.create(db, serial_data)

        assert serial_crud.can_rework(db, serial_id=serial.id) is True

    def test_can_rework_false_for_non_failed(self, db: Session):
        """Test can_rework returns False for non-failed serial."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        assert serial_crud.can_rework(db, serial_id=serial.id) is False

    def test_can_rework_false_for_exhausted(self, db: Session):
        """Test can_rework returns False when rework count is 3."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="FAILED",
            rework_count=3,
            failure_reason="Test failure"
        )
        serial = serial_crud.create(db, serial_data)

        assert serial_crud.can_rework(db, serial_id=serial.id) is False

    def test_can_rework_false_for_nonexistent(self, db: Session):
        """Test can_rework returns False for nonexistent serial."""
        assert serial_crud.can_rework(db, serial_id=99999) is False


class TestSerialUpdateStatus:
    """Test update_status functionality."""

    def test_update_status_valid_transition(self, db: Session):
        """Test valid status transition from CREATED to IN_PROGRESS."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        updated = serial_crud.update_status(db, serial_id=serial.id, status="IN_PROGRESS")

        assert updated.status == SerialStatus.IN_PROGRESS

    def test_update_status_to_failed_requires_reason(self, db: Session):
        """Test that transitioning to FAILED requires failure_reason."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="IN_PROGRESS",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        with pytest.raises(ValueError, match="failure_reason is required"):
            serial_crud.update_status(db, serial_id=serial.id, status="FAILED")

    def test_update_status_to_failed_with_reason(self, db: Session):
        """Test transitioning to FAILED with failure_reason."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="IN_PROGRESS",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        updated = serial_crud.update_status(
            db,
            serial_id=serial.id,
            status="FAILED",
            failure_reason="Dimension out of tolerance"
        )

        assert updated.status == SerialStatus.FAILED
        assert updated.failure_reason == "Dimension out of tolerance"
        assert updated.completed_at is not None

    def test_update_status_invalid_transition_raises_error(self, db: Session):
        """Test invalid status transition raises ValueError."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        with pytest.raises(ValueError, match="Invalid status transition"):
            serial_crud.update_status(db, serial_id=serial.id, status="PASSED")

    def test_update_status_invalid_status_value(self, db: Session):
        """Test that invalid status value raises ValueError."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        with pytest.raises(ValueError, match="status must be one of"):
            serial_crud.update_status(db, serial_id=serial.id, status="INVALID")

    def test_update_status_not_found(self, db: Session):
        """Test update_status returns None for nonexistent serial."""
        result = serial_crud.update_status(db, serial_id=99999, status="IN_PROGRESS")
        assert result is None


class TestSerialUpdate:
    """Test serial update operations."""

    def test_update_serial(self, db: Session):
        """Test updating serial fields."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)

        update_data = SerialUpdate(status="IN_PROGRESS")
        updated = serial_crud.update(db, serial_id=serial.id, serial_in=update_data)

        assert updated.status == SerialStatus.IN_PROGRESS

    def test_update_nonexistent_serial_returns_none(self, db: Session):
        """Test updating nonexistent serial returns None."""
        update_data = SerialUpdate(status="IN_PROGRESS")
        result = serial_crud.update(db, serial_id=99999, serial_in=update_data)

        assert result is None


class TestSerialDelete:
    """Test serial delete operations."""

    def test_delete_existing_serial(self, db: Session):
        """Test deleting an existing serial."""
        product_model = create_product_model(db)
        lot = create_lot(db, product_model.id)

        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0,
        )
        serial = serial_crud.create(db, serial_data)
        serial_id = serial.id

        result = serial_crud.delete(db, serial_id=serial_id)

        assert result is True
        assert serial_crud.get(db, serial_id=serial_id) is None

    def test_delete_nonexistent_serial_returns_false(self, db: Session):
        """Test deleting nonexistent serial returns False."""
        result = serial_crud.delete(db, serial_id=99999)

        assert result is False
