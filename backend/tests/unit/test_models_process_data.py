"""
Unit tests for ProcessData and WIPProcessHistory models.

Tests process_session_id column and session relationship functionality.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import (
    ProcessData,
    WIPProcessHistory,
    ProcessHeader,
    Lot,
    Process,
    User,
    WIPItem,
    UserRole,
    ProductModel,
    LotStatus,
)
from app.models.production_line import ProductionLine
from app.models.process_data import ProcessResult, DataLevel


def create_test_product_model(db: Session) -> ProductModel:
    """Helper to create a ProductModel for tests."""
    product_model = ProductModel(
        model_code="TST",
        model_name="Test Model",
        category="Test",
        status="ACTIVE",
        specifications={}
    )
    db.add(product_model)
    db.commit()
    db.refresh(product_model)
    return product_model


def create_test_production_line(db: Session) -> ProductionLine:
    """Helper to create a ProductionLine for tests."""
    production_line = ProductionLine(
        line_code="KR001",
        line_name="Test Line 1",
        location="Test Factory",
        status="ACTIVE"
    )
    db.add(production_line)
    db.commit()
    db.refresh(production_line)
    return production_line


def create_test_lot(db: Session, product_model_id: int, production_line_id: int) -> Lot:
    """Helper to create a Lot for tests."""
    lot = Lot(
        lot_number="TEST-LOT-001",
        product_model_id=product_model_id,
        production_line_id=production_line_id,
        production_date=datetime.now(timezone.utc).date(),
        shift="D",
        target_quantity=100,
        status=LotStatus.CREATED,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


def create_test_process(db: Session, process_number: int = 1) -> Process:
    """Helper to create a Process for tests."""
    process = Process(
        process_number=process_number,
        process_code=f"PROC{process_number}",
        process_name_ko=f"테스트 프로세스 {process_number}",
        process_name_en=f"Test Process {process_number}",
        quality_criteria={},
        sort_order=process_number,
    )
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


def create_test_operator(db: Session, username: str = "operator1") -> User:
    """Helper to create an operator user for tests."""
    operator = User(
        username=username,
        email=f"{username}@test.com",
        full_name="Test Operator",
        hashed_password="fakehash123",
        role=UserRole.OPERATOR,
        is_active=True,
    )
    db.add(operator)
    db.commit()
    db.refresh(operator)
    return operator


class TestProcessDataSessionID:
    """Tests for ProcessData.process_session_id column and relationship."""

    def test_process_data_session_id_column_exists(self, db: Session):
        """Test that process_session_id column exists and is nullable."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        process_data = ProcessData(
            lot_id=lot.id,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevel.LOT.value,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            process_session_id=42,
        )
        db.add(process_data)
        db.commit()
        db.refresh(process_data)

        assert process_data.process_session_id == 42

    def test_process_data_session_id_nullable(self, db: Session):
        """Test that process_session_id can be NULL."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        process_data = ProcessData(
            lot_id=lot.id,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevel.LOT.value,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            # process_session_id is NOT set - should default to None
        )
        db.add(process_data)
        db.commit()
        db.refresh(process_data)

        assert process_data.process_session_id is None

    def test_process_data_session_relationship(self, db: Session):
        """Test that session relationship is properly configured."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        # Create a ProcessHeader (session)
        session = ProcessHeader(
            process_id=process.id,
            slot_id=1,
            station_id=1,
            status="ACTIVE",
        )
        db.add(session)
        db.flush()

        process_data = ProcessData(
            lot_id=lot.id,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevel.LOT.value,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            process_session_id=session.id,
        )
        db.add(process_data)
        db.commit()
        db.refresh(process_data)

        # Test relationship
        assert hasattr(process_data, 'session')
        assert process_data.session is not None
        assert isinstance(process_data.session, ProcessHeader)
        assert process_data.session.id == session.id

    def test_process_data_session_fk_set_null_on_delete(self, db: Session):
        """Test that deleting ProcessHeader sets process_session_id to NULL (ON DELETE SET NULL)."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        # Create session
        session = ProcessHeader(
            process_id=process.id,
            slot_id=1,
            station_id=1,
            status="ACTIVE",
        )
        db.add(session)
        db.flush()

        # Create process_data referencing session
        process_data = ProcessData(
            lot_id=lot.id,
            process_id=process.id,
            operator_id=operator.id,
            data_level=DataLevel.LOT.value,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            process_session_id=session.id,
        )
        db.add(process_data)
        db.commit()
        db.refresh(process_data)

        # Verify session is linked
        assert process_data.process_session_id == session.id

        # Delete session
        db.delete(session)
        db.commit()
        db.refresh(process_data)

        # Verify process_data.process_session_id is now NULL
        assert process_data.process_session_id is None


class TestWIPProcessHistorySessionID:
    """Tests for WIPProcessHistory.process_session_id column and relationship."""

    def test_wip_process_history_session_id_column(self, db: Session):
        """Test WIPProcessHistory.process_session_id column."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        # Create WIP item
        wip_item = WIPItem(
            lot_id=lot.id,
            wip_number=1,
            status="IN_PROGRESS",
        )
        db.add(wip_item)
        db.flush()

        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=operator.id,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            process_session_id=42,
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        assert history.process_session_id == 42
        assert hasattr(history, 'session')

    def test_wip_history_session_relationship(self, db: Session):
        """Test WIPProcessHistory session relationship."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        # Create session
        session = ProcessHeader(
            process_id=process.id,
            slot_id=2,
            station_id=1,
            status="ACTIVE",
        )
        db.add(session)
        db.flush()

        # Create WIP item
        wip_item = WIPItem(
            lot_id=lot.id,
            wip_number=1,
            status="IN_PROGRESS",
        )
        db.add(wip_item)
        db.flush()

        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=operator.id,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            process_session_id=session.id,
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        # Test relationship
        assert history.session is not None
        assert isinstance(history.session, ProcessHeader)
        assert history.session.id == session.id
        assert history.session.slot_id == 2

    def test_wip_history_session_fk_set_null_on_delete(self, db: Session):
        """Test WIPProcessHistory foreign key behavior (ON DELETE SET NULL)."""
        product_model = create_test_product_model(db)
        production_line = create_test_production_line(db)
        lot = create_test_lot(db, product_model.id, production_line.id)
        process = create_test_process(db, 1)
        operator = create_test_operator(db)

        # Create session
        session = ProcessHeader(
            process_id=process.id,
            slot_id=1,
            station_id=1,
            status="ACTIVE",
        )
        db.add(session)
        db.flush()

        # Create WIP history
        wip_item = WIPItem(
            lot_id=lot.id,
            wip_number=1,
            status="IN_PROGRESS",
        )
        db.add(wip_item)
        db.flush()

        history = WIPProcessHistory(
            wip_item_id=wip_item.id,
            process_id=process.id,
            operator_id=operator.id,
            result=ProcessResult.PASS.value,
            started_at=datetime.now(timezone.utc),
            process_session_id=session.id,
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        # Verify session linked
        assert history.process_session_id == session.id

        # Delete session
        db.delete(session)
        db.commit()
        db.refresh(history)

        # Verify history.process_session_id is now NULL
        assert history.process_session_id is None
