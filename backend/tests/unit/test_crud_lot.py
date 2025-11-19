"""
Unit tests for app/crud/lot.py module.

Tests:
    - LOT CRUD operations (create, read, update, delete)
    - LOT-specific queries (get_by_number, get_active, get_by_date_range)
    - Product model filtering
    - Status transitions
    - Quantity updates and calculations
    - LOT closure operations
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.crud import lot as lot_crud
from app.crud import serial as serial_crud
from app.models import Lot, LotStatus, ProductModel, SerialStatus
from app.schemas.lot import LotCreate, LotUpdate
from app.schemas.serial import SerialCreate


def create_product_model(db: Session, model_code: str = "NH-TEST-001") -> ProductModel:
    """Helper to create a ProductModel for tests."""
    product_model = ProductModel(
        model_code=model_code,
        model_name="Test Model",
        category="Test",
        status="ACTIVE",
        specifications={}
    )
    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model


class TestLotCreate:
    """Test LOT creation operations."""

    def test_create_lot_with_valid_data(self, db: Session):
        """Test creating a LOT with valid data."""
        product_model = create_product_model(db)

        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=50,
            status=LotStatus.CREATED
        )

        lot = lot_crud.create(db, lot_data)

        assert lot.id is not None
        assert lot.product_model_id == product_model.id
        assert lot.production_date == date(2025, 11, 18)
        assert lot.shift == "D"
        assert lot.target_quantity == 50
        assert lot.status == LotStatus.CREATED
        assert lot.lot_number.startswith("WF-KR-251118D-")

    def test_create_lot_generates_sequential_numbers(self, db: Session):
        """Test that LOT numbers are sequential for same date/shift."""
        product_model = create_product_model(db)

        lot_data1 = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        lot_data2 = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )

        lot1 = lot_crud.create(db, lot_data1)
        lot2 = lot_crud.create(db, lot_data2)

        assert lot1.lot_number == "WF-KR-251118D-001"
        assert lot2.lot_number == "WF-KR-251118D-002"

    def test_create_lot_night_shift(self, db: Session):
        """Test creating a LOT for night shift."""
        product_model = create_product_model(db)

        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="N",
            target_quantity=100,
            status=LotStatus.CREATED
        )

        lot = lot_crud.create(db, lot_data)

        assert "N" in lot.lot_number
        assert lot.lot_number == "WF-KR-251118N-001"


class TestLotRead:
    """Test LOT read operations."""

    def test_get_lot_by_id(self, db: Session):
        """Test retrieving LOT by ID."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        created = lot_crud.create(db, lot_data)

        retrieved = lot_crud.get(db, lot_id=created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_lot_returns_none(self, db: Session):
        """Test that getting nonexistent LOT returns None."""
        lot = lot_crud.get(db, lot_id=99999)
        assert lot is None

    def test_get_by_number(self, db: Session):
        """Test retrieving LOT by lot_number."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        created = lot_crud.create(db, lot_data)

        retrieved = lot_crud.get_by_number(db, lot_number=created.lot_number)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.lot_number == created.lot_number

    def test_get_by_number_not_found(self, db: Session):
        """Test get_by_number returns None for nonexistent LOT."""
        lot = lot_crud.get_by_number(db, lot_number="WF-KR-NONEXISTENT-001")
        assert lot is None


class TestLotGetActive:
    """Test get_active functionality."""

    def test_get_active_returns_created_and_in_progress(self, db: Session):
        """Test getting active LOTs (CREATED and IN_PROGRESS)."""
        product_model = create_product_model(db)

        # Create LOTs with different statuses
        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))
        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="N",
            target_quantity=100,
            status=LotStatus.IN_PROGRESS
        ))
        completed_lot = lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 19),
            shift="D",
            target_quantity=100,
            status=LotStatus.COMPLETED
        ))

        active_lots = lot_crud.get_active(db)

        assert len(active_lots) == 2
        active_ids = [lot.id for lot in active_lots]
        assert completed_lot.id not in active_ids

    def test_get_active_with_pagination(self, db: Session):
        """Test pagination in get_active."""
        product_model = create_product_model(db)

        # Create 5 active LOTs
        for i in range(5):
            lot_crud.create(db, LotCreate(
                product_model_id=product_model.id,
                production_date=date(2025, 11, 18),
                shift="D" if i % 2 == 0 else "N",
                target_quantity=100,
                status=LotStatus.CREATED
            ))

        page1 = lot_crud.get_active(db, skip=0, limit=2)
        page2 = lot_crud.get_active(db, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2


class TestLotGetByDateRange:
    """Test get_by_date_range functionality."""

    def test_get_by_date_range(self, db: Session):
        """Test filtering LOTs by date range."""
        product_model = create_product_model(db)

        # Create LOTs on different dates
        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 15),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))
        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))
        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 25),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))

        lots = lot_crud.get_by_date_range(
            db,
            start_date=date(2025, 11, 16),
            end_date=date(2025, 11, 20)
        )

        assert len(lots) == 1
        assert lots[0].production_date == date(2025, 11, 18)

    def test_get_by_date_range_inclusive(self, db: Session):
        """Test that date range is inclusive."""
        product_model = create_product_model(db)

        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))

        lots = lot_crud.get_by_date_range(
            db,
            start_date=date(2025, 11, 18),
            end_date=date(2025, 11, 18)
        )

        assert len(lots) == 1


class TestLotGetByProductModel:
    """Test get_by_product_model functionality."""

    def test_get_by_product_model(self, db: Session):
        """Test filtering LOTs by product model."""
        product_model1 = create_product_model(db, model_code="NH-TEST-001")
        product_model2 = create_product_model(db, model_code="NH-TEST-002")

        lot_crud.create(db, LotCreate(
            product_model_id=product_model1.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))
        lot_crud.create(db, LotCreate(
            product_model_id=product_model2.id,
            production_date=date(2025, 11, 18),
            shift="N",
            target_quantity=100,
            status=LotStatus.CREATED
        ))

        lots = lot_crud.get_by_product_model(db, product_model_id=product_model1.id)

        assert len(lots) == 1
        assert lots[0].product_model_id == product_model1.id


class TestLotGetByStatus:
    """Test get_by_status functionality."""

    def test_get_by_status(self, db: Session):
        """Test filtering LOTs by status."""
        product_model = create_product_model(db)

        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        ))
        lot_crud.create(db, LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="N",
            target_quantity=100,
            status=LotStatus.COMPLETED
        ))

        created_lots = lot_crud.get_by_status(db, status=LotStatus.CREATED)
        completed_lots = lot_crud.get_by_status(db, status=LotStatus.COMPLETED)

        assert len(created_lots) == 1
        assert len(completed_lots) == 1
        assert all(lot.status == LotStatus.CREATED for lot in created_lots)


class TestLotUpdateQuantities:
    """Test update_quantities functionality."""

    def test_update_quantities_calculates_from_serials(self, db: Session):
        """Test that quantities are correctly calculated from serials."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        lot = lot_crud.create(db, lot_data)

        # Create serials with different statuses
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=1, status="PASSED", rework_count=0
        ))
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=2, status="PASSED", rework_count=0
        ))
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=3, status="FAILED",
            rework_count=0, failure_reason="Test"
        ))
        serial_crud.create(db, SerialCreate(
            lot_id=lot.id, sequence_in_lot=4, status="IN_PROGRESS", rework_count=0
        ))

        updated_lot = lot_crud.update_quantities(db, lot_id=lot.id)

        assert updated_lot.actual_quantity == 4
        assert updated_lot.passed_quantity == 2
        assert updated_lot.failed_quantity == 1

    def test_update_quantities_not_found(self, db: Session):
        """Test update_quantities returns None for nonexistent LOT."""
        result = lot_crud.update_quantities(db, lot_id=99999)
        assert result is None


class TestLotCloseLot:
    """Test close_lot functionality."""

    def test_close_lot_sets_status_and_timestamp(self, db: Session):
        """Test closing a LOT sets status and closed_at."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.COMPLETED
        )
        lot = lot_crud.create(db, lot_data)

        closed_lot = lot_crud.close_lot(db, lot_id=lot.id)

        assert closed_lot.status == LotStatus.CLOSED
        assert closed_lot.closed_at is not None

    def test_close_lot_not_found(self, db: Session):
        """Test close_lot returns None for nonexistent LOT."""
        result = lot_crud.close_lot(db, lot_id=99999)
        assert result is None


class TestLotUpdate:
    """Test LOT update operations."""

    def test_update_lot_status(self, db: Session):
        """Test updating LOT status."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        lot = lot_crud.create(db, lot_data)

        update_data = LotUpdate(status=LotStatus.IN_PROGRESS)
        updated = lot_crud.update(db, lot_id=lot.id, lot_in=update_data)

        assert updated.status == LotStatus.IN_PROGRESS

    def test_update_lot_quantities(self, db: Session):
        """Test updating LOT quantities."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        lot = lot_crud.create(db, lot_data)

        update_data = LotUpdate(
            actual_quantity=50,
            passed_quantity=45,
            failed_quantity=5
        )
        updated = lot_crud.update(db, lot_id=lot.id, lot_in=update_data)

        assert updated.actual_quantity == 50
        assert updated.passed_quantity == 45
        assert updated.failed_quantity == 5

    def test_update_nonexistent_lot_returns_none(self, db: Session):
        """Test updating nonexistent LOT returns None."""
        update_data = LotUpdate(status=LotStatus.IN_PROGRESS)
        result = lot_crud.update(db, lot_id=99999, lot_in=update_data)

        assert result is None


class TestLotDelete:
    """Test LOT delete operations."""

    def test_delete_existing_lot(self, db: Session):
        """Test deleting an existing LOT without serials."""
        product_model = create_product_model(db)
        lot_data = LotCreate(
            product_model_id=product_model.id,
            production_date=date(2025, 11, 18),
            shift="D",
            target_quantity=100,
            status=LotStatus.CREATED
        )
        lot = lot_crud.create(db, lot_data)
        lot_id = lot.id

        result = lot_crud.delete(db, lot_id=lot_id)

        assert result is True
        assert lot_crud.get(db, lot_id=lot_id) is None

    def test_delete_nonexistent_lot_returns_false(self, db: Session):
        """Test deleting nonexistent LOT returns False."""
        result = lot_crud.delete(db, lot_id=99999)

        assert result is False


class TestLotGetMulti:
    """Test get_multi functionality."""

    def test_get_multi_with_pagination(self, db: Session):
        """Test get_multi with pagination."""
        product_model = create_product_model(db)

        # Create 5 LOTs
        for i in range(5):
            lot_crud.create(db, LotCreate(
                product_model_id=product_model.id,
                production_date=date(2025, 11, 18 - i),
                shift="D",
                target_quantity=100,
                status=LotStatus.CREATED
            ))

        page1 = lot_crud.get_multi(db, skip=0, limit=2)
        page2 = lot_crud.get_multi(db, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        # Verify no overlap
        page1_ids = {lot.id for lot in page1}
        page2_ids = {lot.id for lot in page2}
        assert page1_ids.isdisjoint(page2_ids)
