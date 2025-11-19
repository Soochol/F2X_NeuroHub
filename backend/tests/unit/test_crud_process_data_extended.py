"""
Extended unit tests for ProcessData CRUD operations.

Tests additional scenarios to improve coverage for process_data.py CRUD functions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.crud import process_data as process_data_crud
from app.models.process_data import ProcessData, ProcessResult, DataLevel


class TestProcessDataGet:
    """Tests for get function."""

    def test_get_existing_process_data(self):
        """Test getting an existing process data by ID."""
        mock_db = MagicMock()
        mock_pd = MagicMock(spec=ProcessData)
        mock_pd.id = 1
        mock_db.query().filter().first.return_value = mock_pd

        result = process_data_crud.get(mock_db, process_data_id=1)

        assert result is not None
        assert result.id == 1

    def test_get_nonexistent_process_data(self):
        """Test getting process data that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = process_data_crud.get(mock_db, process_data_id=999)

        assert result is None


class TestProcessDataGetMulti:
    """Tests for get_multi function."""

    def test_get_multi_with_pagination(self):
        """Test getting multiple process data with pagination."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(5)]
        mock_db.query().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_multi(mock_db, skip=0, limit=10)

        assert len(result) == 5


class TestProcessDataGetBySerial:
    """Tests for get_by_serial function."""

    def test_get_by_serial_found(self):
        """Test getting process data by serial ID."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(3)]
        mock_db.query().join().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_by_serial(mock_db, serial_id=1, skip=0, limit=10)

        assert len(result) == 3

    def test_get_by_serial_empty(self):
        """Test getting process data by serial ID when none exist."""
        mock_db = MagicMock()
        mock_db.query().join().filter().order_by().offset().limit().all.return_value = []

        result = process_data_crud.get_by_serial(mock_db, serial_id=999)

        assert len(result) == 0


class TestProcessDataGetByLot:
    """Tests for get_by_lot function."""

    def test_get_by_lot_found(self):
        """Test getting process data by lot ID."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(10)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_by_lot(mock_db, lot_id=1, skip=0, limit=20)

        assert len(result) == 10


class TestProcessDataGetByProcess:
    """Tests for get_by_process function."""

    def test_get_by_process_found(self):
        """Test getting process data by process ID."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(4)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_by_process(mock_db, process_id=1)

        assert len(result) == 4


class TestProcessDataGetByResult:
    """Tests for get_by_result function."""

    def test_get_by_result_pass(self):
        """Test getting process data by PASS result."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(5)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_by_result(mock_db, result="PASS")

        assert len(result) == 5

    def test_get_by_result_fail(self):
        """Test getting process data by FAIL result."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(2)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_by_result(mock_db, result="FAIL")

        assert len(result) == 2


class TestProcessDataGetFailures:
    """Tests for get_failures function."""

    def test_get_failures(self):
        """Test getting failed process records."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_failures(mock_db, skip=0, limit=10)

        assert len(result) == 3


class TestProcessDataGetByOperator:
    """Tests for get_by_operator function."""

    def test_get_by_operator_found(self):
        """Test getting process data by operator ID."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(7)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_by_operator(mock_db, operator_id=1)

        assert len(result) == 7


class TestProcessDataGetByDateRange:
    """Tests for get_by_date_range function."""

    def test_get_by_date_range(self):
        """Test getting process data by date range."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(5)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        start = datetime.utcnow() - timedelta(days=7)
        end = datetime.utcnow()

        result = process_data_crud.get_by_date_range(
            mock_db, start_date=start, end_date=end
        )

        assert len(result) == 5


class TestProcessDataGetBySerialAndProcess:
    """Tests for get_by_serial_and_process function."""

    def test_get_by_serial_and_process_found(self):
        """Test getting process data by serial and process combination."""
        mock_db = MagicMock()
        mock_pd = MagicMock(spec=ProcessData)
        mock_db.query().filter().first.return_value = mock_pd

        result = process_data_crud.get_by_serial_and_process(
            mock_db, serial_id=1, process_id=1
        )

        assert result is not None

    def test_get_by_serial_and_process_not_found(self):
        """Test getting process data by serial and process when not found."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = process_data_crud.get_by_serial_and_process(
            mock_db, serial_id=999, process_id=999
        )

        assert result is None


class TestProcessDataGetByLotAndProcess:
    """Tests for get_by_lot_and_process function."""

    def test_get_by_lot_and_process_found(self):
        """Test getting LOT-level process data."""
        mock_db = MagicMock()
        mock_pd = MagicMock(spec=ProcessData)
        mock_db.query().filter().first.return_value = mock_pd

        result = process_data_crud.get_by_lot_and_process(
            mock_db, lot_id=1, process_id=1
        )

        assert result is not None


class TestProcessDataGetFailuresByProcess:
    """Tests for get_failures_by_process function."""

    def test_get_failures_by_process(self):
        """Test getting failures for a specific process."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(2)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_failures_by_process(mock_db, process_id=1)

        assert len(result) == 2


class TestProcessDataGetIncomplete:
    """Tests for get_incomplete_processes function."""

    def test_get_incomplete_processes(self):
        """Test getting in-progress processes."""
        mock_db = MagicMock()
        mock_pds = [MagicMock(spec=ProcessData) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_pds

        result = process_data_crud.get_incomplete_processes(mock_db)

        assert len(result) == 3


class TestProcessDataCountByResult:
    """Tests for count_by_result function."""

    def test_count_by_result_pass(self):
        """Test counting process data by PASS result."""
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 100

        result = process_data_crud.count_by_result(mock_db, result="PASS")

        assert result == 100

    def test_count_by_result_fail(self):
        """Test counting process data by FAIL result."""
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 10

        result = process_data_crud.count_by_result(mock_db, result="FAIL")

        assert result == 10


class TestProcessDataCountByProcess:
    """Tests for count_by_process function."""

    def test_count_by_process(self):
        """Test counting process data by process ID."""
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 50

        result = process_data_crud.count_by_process(mock_db, process_id=1)

        assert result == 50


class TestProcessDataCountBySerial:
    """Tests for count_by_serial function."""

    def test_count_by_serial(self):
        """Test counting process data by serial ID."""
        mock_db = MagicMock()
        mock_db.query().filter().count.return_value = 8

        result = process_data_crud.count_by_serial(mock_db, serial_id=1)

        assert result == 8


class TestProcessDataDelete:
    """Tests for delete function."""

    def test_delete_found(self):
        """Test deleting process data that exists."""
        mock_db = MagicMock()
        mock_pd = MagicMock(spec=ProcessData)
        mock_db.query().filter().first.return_value = mock_pd

        result = process_data_crud.delete(mock_db, process_data_id=1)

        assert result is True
        mock_db.delete.assert_called_once()

    def test_delete_not_found(self):
        """Test deleting process data that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = process_data_crud.delete(mock_db, process_data_id=999)

        assert result is False
