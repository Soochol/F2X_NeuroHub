"""
Performance tests for CRUD query optimizations.

This module tests that CRUD operations maintain efficient query counts
and don't introduce N+1 query problems.
"""

import pytest
from contextlib import contextmanager
from typing import Generator, Dict, Any
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from app.database import SessionLocal
from app.crud import lot as crud_lot
from app.crud import serial as crud_serial
from app.crud import process_data as crud_process_data
from app.models.lot import Lot, LotStatus
from app.models.serial import Serial
from app.models.process_data import ProcessData
from app.schemas.lot import LotCreate
from app.schemas.serial import SerialCreate
from app.schemas.process_data import ProcessDataCreate


@contextmanager
def assert_query_count(
    session: Session,
    max_expected: int,
    print_queries: bool = False
) -> Generator[Dict[str, Any], None, None]:
    """
    Context manager to count and assert database queries.

    Args:
        session: SQLAlchemy session to monitor
        max_expected: Maximum expected number of queries
        print_queries: Whether to print queries for debugging

    Yields:
        Dictionary with query statistics

    Raises:
        AssertionError: If query count exceeds max_expected
    """
    stats = {"count": 0, "queries": []}

    def receive_after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        stats["count"] += 1
        if print_queries:
            print(f"Query {stats['count']}: {statement[:100]}...")
        stats["queries"].append(statement)

    # Attach listener
    engine: Engine = session.bind
    event.listen(engine, "after_cursor_execute", receive_after_cursor_execute)

    try:
        yield stats
    finally:
        # Remove listener
        event.remove(engine, "after_cursor_execute", receive_after_cursor_execute)

        # Assert query count
        if stats["count"] > max_expected:
            raise AssertionError(
                f"Expected at most {max_expected} queries, got {stats['count']}\n"
                f"Queries:\n" + "\n".join(f"{i+1}. {q[:100]}..."
                                         for i, q in enumerate(stats["queries"]))
            )


class TestLotQueryPerformance:
    """Test query performance for LOT CRUD operations."""

    def test_get_single_lot_optimized(self, db: Session, test_lot: Lot):
        """Test that getting a single lot with relationships is optimized."""
        with assert_query_count(db, max_expected=4):  # 1 main + 3 relationships
            lot = crud_lot.get(db, lot_id=test_lot.id, eager_loading="standard")

            # Access relationships - should not cause additional queries
            assert lot is not None
            _ = lot.product_model.model_code
            _ = lot.production_line.line_code if lot.production_line else None
            _ = len(lot.serials)
            _ = len(lot.wip_items)

    def test_get_single_lot_minimal(self, db: Session, test_lot: Lot):
        """Test that minimal loading uses only 1 query."""
        with assert_query_count(db, max_expected=1):
            lot = crud_lot.get(db, lot_id=test_lot.id, eager_loading="minimal")
            assert lot is not None
            # Don't access relationships in minimal mode

    def test_get_multi_lots_optimized(self, db: Session, test_lots: list):
        """Test that getting multiple lots with relationships is optimized."""
        with assert_query_count(db, max_expected=5):  # 1 main + 4 relationships
            lots = crud_lot.get_multi(db, limit=100, eager_loading="standard")

            # Access relationships for all lots - should not cause N+1
            for lot in lots:
                _ = lot.product_model.model_code
                _ = len(lot.serials)
                _ = len(lot.wip_items)

    def test_get_active_lots_optimized(self, db: Session, test_lots: list):
        """Test that getting active lots is optimized."""
        with assert_query_count(db, max_expected=5):
            lots = crud_lot.get_active(db, limit=50, eager_loading="standard")

            for lot in lots:
                if lot.status in [LotStatus.CREATED, LotStatus.IN_PROGRESS]:
                    _ = lot.product_model.model_code
                    _ = len(lot.serials)

    def test_get_by_status_optimized(self, db: Session, test_lots: list):
        """Test that filtering by status maintains optimization."""
        with assert_query_count(db, max_expected=5):
            lots = crud_lot.get_by_status(
                db,
                status=LotStatus.CREATED,
                limit=50,
                eager_loading="standard"
            )

            for lot in lots:
                _ = lot.lot_number
                _ = lot.product_model.model_code
                _ = len(lot.serials)


class TestSerialQueryPerformance:
    """Test query performance for Serial CRUD operations."""

    def test_get_single_serial_optimized(self, db: Session, test_serial: Serial):
        """Test that getting a single serial with lot is optimized."""
        with assert_query_count(db, max_expected=1):  # 1 query with JOIN
            serial = crud_serial.get(
                db,
                serial_id=test_serial.id,
                eager_loading="standard"
            )

            # Access lot relationship - should not cause additional query
            assert serial is not None
            _ = serial.lot.lot_number
            _ = serial.lot.product_model_id

    def test_get_multi_serials_optimized(self, db: Session, test_serials: list):
        """Test that getting multiple serials is optimized."""
        with assert_query_count(db, max_expected=1):  # 1 query with JOIN
            serials = crud_serial.get_multi(
                db,
                limit=100,
                eager_loading="standard"
            )

            # Access lot for all serials - should not cause N+1
            for serial in serials:
                _ = serial.lot.lot_number

    def test_get_by_lot_optimized(self, db: Session, test_lot: Lot):
        """Test that getting serials by lot is optimized."""
        with assert_query_count(db, max_expected=1):
            serials = crud_serial.get_by_lot(
                db,
                lot_id=test_lot.id,
                limit=100,
                eager_loading="standard"
            )

            for serial in serials:
                _ = serial.lot.lot_number
                _ = serial.status.value


class TestProcessDataQueryPerformance:
    """Test query performance for ProcessData CRUD operations."""

    def test_get_single_process_data_optimized(
        self,
        db: Session,
        test_process_data: ProcessData
    ):
        """Test that getting process data with all relationships is optimized."""
        with assert_query_count(db, max_expected=1):  # 1 query with multiple JOINs
            pd = crud_process_data.get(
                db,
                process_data_id=test_process_data.id,
                eager_loading="standard"
            )

            # Access all relationships - should not cause additional queries
            assert pd is not None
            _ = pd.lot.lot_number
            _ = pd.serial.serial_number if pd.serial else None
            _ = pd.process.name
            _ = pd.operator.username
            if pd.wip_item:
                _ = pd.wip_item.wip_number

    def test_get_multi_process_data_optimized(
        self,
        db: Session,
        test_process_data_list: list
    ):
        """Test that getting multiple process data records is optimized."""
        with assert_query_count(db, max_expected=1):
            process_data = crud_process_data.get_multi(
                db,
                limit=100,
                eager_loading="standard"
            )

            # Access relationships for all records - should not cause N+1
            for pd in process_data:
                _ = pd.lot.lot_number
                _ = pd.serial.serial_number if pd.serial else None
                _ = pd.process.name
                _ = pd.operator.username

    def test_get_by_serial_optimized(
        self,
        db: Session,
        test_serial: Serial
    ):
        """Test that getting process data by serial is optimized."""
        with assert_query_count(db, max_expected=1):
            process_data = crud_process_data.get_by_serial(
                db,
                serial_id=test_serial.id,
                eager_loading="standard"
            )

            for pd in process_data:
                _ = pd.process.name
                _ = pd.operator.username
                _ = pd.lot.lot_number


class TestQueryPerformanceComparison:
    """Compare query performance with and without optimization."""

    def test_n_plus_one_demonstration(self, db: Session, test_lots: list):
        """Demonstrate N+1 problem vs optimized solution."""
        # Without optimization (minimal loading)
        stats_without = {"queries": 0}
        with assert_query_count(db, max_expected=300, print_queries=False) as stats:
            lots = crud_lot.get_multi(db, limit=100, eager_loading="minimal")
            for lot in lots[:10]:  # Only check first 10 to limit queries
                # Each access causes a new query
                _ = lot.product_model.model_code  # +1 query
                _ = len(lot.serials)  # +1 query
            stats_without["queries"] = stats["count"]

        # With optimization (standard loading)
        stats_with = {"queries": 0}
        with assert_query_count(db, max_expected=5) as stats:
            lots = crud_lot.get_multi(db, limit=100, eager_loading="standard")
            for lot in lots[:10]:
                # No additional queries
                _ = lot.product_model.model_code
                _ = len(lot.serials)
            stats_with["queries"] = stats["count"]

        # Assert significant improvement
        improvement = (1 - stats_with["queries"] / stats_without["queries"]) * 100
        print(f"\nQuery reduction: {stats_without['queries']} -> {stats_with['queries']} "
              f"({improvement:.1f}% improvement)")
        assert improvement > 70, f"Expected >70% improvement, got {improvement:.1f}%"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_results_query_count(self, db: Session):
        """Test that empty results don't cause unnecessary queries."""
        with assert_query_count(db, max_expected=1):
            lots = crud_lot.get_multi(
                db,
                skip=99999,  # Skip beyond existing data
                eager_loading="standard"
            )
            assert len(lots) == 0

    def test_null_relationships_handling(self, db: Session):
        """Test that null relationships don't cause issues."""
        # Create a lot without production_line
        lot_data = LotCreate(
            product_model_id=1,
            production_line_id=None,
            production_date="2024-01-01",
            target_quantity=100,
            status=LotStatus.CREATED
        )

        with assert_query_count(db, max_expected=10):  # Allow for creation queries
            lot = crud_lot.create(db, lot_in=lot_data)
            db.commit()

            # Get with eager loading
            fetched = crud_lot.get(db, lot_id=lot.id, eager_loading="standard")

            # Access potentially null relationship
            assert fetched is not None
            assert fetched.production_line is None  # Should not cause error
            _ = fetched.product_model.model_code  # Should work normally


@pytest.fixture
def db():
    """Provide a database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_lot(db: Session) -> Lot:
    """Create a test lot with serials."""
    lot_data = LotCreate(
        product_model_id=1,
        production_line_id=1,
        production_date="2024-01-01",
        target_quantity=10,
        status=LotStatus.CREATED
    )
    lot = crud_lot.create(db, lot_in=lot_data)

    # Add some serials
    for i in range(5):
        serial_data = SerialCreate(
            lot_id=lot.id,
            sequence_in_lot=i + 1,
            status="CREATED",
            rework_count=0
        )
        crud_serial.create(db, serial_in=serial_data)

    db.commit()
    return lot


@pytest.fixture
def test_lots(db: Session) -> list:
    """Create multiple test lots."""
    lots = []
    for i in range(20):
        lot_data = LotCreate(
            product_model_id=1,
            production_line_id=1,
            production_date=f"2024-01-{i+1:02d}",
            target_quantity=50,
            status=LotStatus.CREATED if i % 2 == 0 else LotStatus.IN_PROGRESS
        )
        lot = crud_lot.create(db, lot_in=lot_data)
        lots.append(lot)

    db.commit()
    return lots


@pytest.fixture
def test_serial(db: Session, test_lot: Lot) -> Serial:
    """Create a test serial."""
    return db.query(Serial).filter(Serial.lot_id == test_lot.id).first()


@pytest.fixture
def test_serials(db: Session, test_lots: list) -> list:
    """Create multiple test serials."""
    serials = []
    for lot in test_lots[:10]:
        for i in range(5):
            serial_data = SerialCreate(
                lot_id=lot.id,
                sequence_in_lot=i + 1,
                status="CREATED",
                rework_count=0
            )
            serial = crud_serial.create(db, serial_in=serial_data)
            serials.append(serial)

    db.commit()
    return serials


@pytest.fixture
def test_process_data(
    db: Session,
    test_lot: Lot,
    test_serial: Serial
) -> ProcessData:
    """Create test process data."""
    from datetime import datetime

    pd_data = ProcessDataCreate(
        lot_id=test_lot.id,
        serial_id=test_serial.id,
        process_id=1,
        operator_id=1,
        data_level="SERIAL",
        result="PASS",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )

    pd = crud_process_data.create(db, obj_in=pd_data)
    db.commit()
    return pd


@pytest.fixture
def test_process_data_list(
    db: Session,
    test_serials: list
) -> list:
    """Create multiple test process data records."""
    from datetime import datetime

    process_data = []
    for serial in test_serials[:20]:
        pd_data = ProcessDataCreate(
            lot_id=serial.lot_id,
            serial_id=serial.id,
            process_id=1,
            operator_id=1,
            data_level="SERIAL",
            result="PASS" if serial.id % 2 == 0 else "FAIL",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        pd = crud_process_data.create(db, obj_in=pd_data)
        process_data.append(pd)

    db.commit()
    return process_data


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])