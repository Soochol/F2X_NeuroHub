"""
Extended unit tests for Serial CRUD operations.

Tests additional scenarios to improve coverage for serial.py CRUD functions.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.crud import serial as serial_crud
from app.models.serial import Serial, SerialStatus


class TestSerialGet:
    """Tests for get function."""

    def test_get_existing_serial(self):
        """Test getting an existing serial by ID."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.id = 1
        mock_serial.serial_number = "LOT-001-0001"
        mock_db.query().filter().first.return_value = mock_serial

        result = serial_crud.get(mock_db, 1)

        assert result is not None
        assert result.id == 1

    def test_get_nonexistent_serial(self):
        """Test getting a serial that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = serial_crud.get(mock_db, 999)

        assert result is None


class TestSerialGetMulti:
    """Tests for get_multi function."""

    def test_get_multi_with_valid_status(self):
        """Test getting multiple serials with valid status filter."""
        mock_db = MagicMock()
        mock_serials = [MagicMock(spec=Serial) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_serials

        result = serial_crud.get_multi(mock_db, skip=0, limit=10, status="PASSED")

        assert len(result) == 3

    def test_get_multi_with_invalid_status(self):
        """Test getting multiple serials with invalid status raises ValueError."""
        mock_db = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            serial_crud.get_multi(mock_db, status="INVALID_STATUS")

        assert "status must be one of" in str(exc_info.value)

    def test_get_multi_without_status(self):
        """Test getting multiple serials without status filter."""
        mock_db = MagicMock()
        mock_serials = [MagicMock(spec=Serial) for _ in range(5)]
        mock_db.query().order_by().offset().limit().all.return_value = mock_serials

        result = serial_crud.get_multi(mock_db, skip=0, limit=10)

        assert len(result) == 5


class TestSerialGetByNumber:
    """Tests for get_by_number function."""

    def test_get_by_number_found(self):
        """Test getting serial by serial number when found."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.serial_number = "WF-KR-251110D-001-0001"
        mock_db.query().filter().first.return_value = mock_serial

        result = serial_crud.get_by_number(mock_db, "WF-KR-251110D-001-0001")

        assert result is not None
        assert result.serial_number == "WF-KR-251110D-001-0001"

    def test_get_by_number_not_found(self):
        """Test getting serial by serial number when not found."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = serial_crud.get_by_number(mock_db, "NONEXISTENT")

        assert result is None


class TestSerialGetByLot:
    """Tests for get_by_lot function."""

    def test_get_by_lot_found(self):
        """Test getting serials by lot ID."""
        mock_db = MagicMock()
        mock_serials = [MagicMock(spec=Serial) for _ in range(5)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_serials

        result = serial_crud.get_by_lot(mock_db, lot_id=1, skip=0, limit=10)

        assert len(result) == 5

    def test_get_by_lot_empty(self):
        """Test getting serials by lot ID when lot has no serials."""
        mock_db = MagicMock()
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        result = serial_crud.get_by_lot(mock_db, lot_id=999)

        assert len(result) == 0


class TestSerialGetByStatus:
    """Tests for get_by_status function."""

    def test_get_by_status_valid(self):
        """Test getting serials by valid status."""
        mock_db = MagicMock()
        mock_serials = [MagicMock(spec=Serial) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_serials

        result = serial_crud.get_by_status(mock_db, status="PASSED", skip=0, limit=10)

        assert len(result) == 3

    def test_get_by_status_invalid(self):
        """Test getting serials by invalid status raises ValueError."""
        mock_db = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            serial_crud.get_by_status(mock_db, status="INVALID")

        assert "status must be one of" in str(exc_info.value)


class TestSerialGetFailed:
    """Tests for get_failed function."""

    def test_get_failed_serials(self):
        """Test getting failed serials available for rework."""
        mock_db = MagicMock()
        mock_serials = [MagicMock(spec=Serial) for _ in range(2)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_serials

        result = serial_crud.get_failed(mock_db, skip=0, limit=10)

        assert len(result) == 2


class TestSerialCreate:
    """Tests for create function."""

    def test_create_serial_lot_not_found(self):
        """Test creating serial when lot doesn't exist raises ValueError."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        mock_serial_in = MagicMock()
        mock_serial_in.lot_id = 999

        with pytest.raises(ValueError) as exc_info:
            serial_crud.create(mock_db, mock_serial_in)

        assert "Lot with ID 999 not found" in str(exc_info.value)

    def test_create_serial_integrity_error(self):
        """Test creating serial with integrity error."""
        mock_db = MagicMock()
        mock_lot = MagicMock()
        mock_lot.lot_number = "LOT-001"
        mock_db.query().filter().first.return_value = mock_lot
        mock_db.add.side_effect = None
        mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        mock_serial_in = MagicMock()
        mock_serial_in.lot_id = 1
        mock_serial_in.sequence_in_lot = 1
        mock_serial_in.status = "CREATED"
        mock_serial_in.rework_count = 0
        mock_serial_in.failure_reason = None

        with pytest.raises(IntegrityError):
            serial_crud.create(mock_db, mock_serial_in)

        mock_db.rollback.assert_called_once()


class TestSerialUpdate:
    """Tests for update function."""

    def test_update_serial_not_found(self):
        """Test updating serial that doesn't exist returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        mock_serial_in = MagicMock()
        mock_serial_in.model_dump.return_value = {"status": "IN_PROGRESS"}

        result = serial_crud.update(mock_db, serial_id=999, serial_in=mock_serial_in)

        assert result is None

    def test_update_serial_integrity_error(self):
        """Test updating serial with integrity error."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_db.query().filter().first.return_value = mock_serial
        mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        mock_serial_in = MagicMock()
        mock_serial_in.model_dump.return_value = {"status": "IN_PROGRESS"}

        with pytest.raises(IntegrityError):
            serial_crud.update(mock_db, serial_id=1, serial_in=mock_serial_in)

        mock_db.rollback.assert_called_once()


class TestSerialDelete:
    """Tests for delete function."""

    def test_delete_serial_not_found(self):
        """Test deleting serial that doesn't exist returns False."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = serial_crud.delete(mock_db, serial_id=999)

        assert result is False

    def test_delete_serial_integrity_error(self):
        """Test deleting serial with integrity error."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_db.query().filter().first.return_value = mock_serial
        mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        with pytest.raises(IntegrityError):
            serial_crud.delete(mock_db, serial_id=1)

        mock_db.rollback.assert_called_once()


class TestSerialIncrementRework:
    """Tests for increment_rework function."""

    def test_increment_rework_serial_not_found(self):
        """Test incrementing rework for nonexistent serial raises ValueError."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        with pytest.raises(ValueError) as exc_info:
            serial_crud.increment_rework(mock_db, serial_id=999)

        assert "not found" in str(exc_info.value)

    def test_increment_rework_not_failed_status(self):
        """Test incrementing rework for non-failed serial raises ValueError."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.status = SerialStatus.IN_PROGRESS
        mock_serial.serial_number = "LOT-001-0001"
        mock_db.query().filter().first.return_value = mock_serial

        with pytest.raises(ValueError) as exc_info:
            serial_crud.increment_rework(mock_db, serial_id=1)

        assert "not in FAILED status" in str(exc_info.value)

    def test_increment_rework_max_exceeded(self):
        """Test incrementing rework when max count exceeded raises ValueError."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.status = SerialStatus.FAILED
        mock_serial.rework_count = 3
        mock_serial.serial_number = "LOT-001-0001"
        mock_db.query().filter().first.return_value = mock_serial

        with pytest.raises(ValueError) as exc_info:
            serial_crud.increment_rework(mock_db, serial_id=1)

        assert "exceeded maximum rework count" in str(exc_info.value)


class TestSerialUpdateStatus:
    """Tests for update_status function."""

    def test_update_status_serial_not_found(self):
        """Test updating status for nonexistent serial returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = serial_crud.update_status(mock_db, serial_id=999, status="IN_PROGRESS")

        assert result is None

    def test_update_status_invalid_status(self):
        """Test updating to invalid status raises ValueError."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_db.query().filter().first.return_value = mock_serial

        with pytest.raises(ValueError) as exc_info:
            serial_crud.update_status(mock_db, serial_id=1, status="INVALID")

        assert "status must be one of" in str(exc_info.value)

    def test_update_status_failed_without_reason(self):
        """Test updating to FAILED without failure_reason raises ValueError."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.status = SerialStatus.IN_PROGRESS
        mock_serial.can_transition_to = MagicMock(return_value=True)
        mock_db.query().filter().first.return_value = mock_serial

        with pytest.raises(ValueError) as exc_info:
            serial_crud.update_status(mock_db, serial_id=1, status="FAILED")

        assert "failure_reason is required" in str(exc_info.value)


class TestSerialCanRework:
    """Tests for can_rework function."""

    def test_can_rework_serial_not_found(self):
        """Test can_rework returns False for nonexistent serial."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = serial_crud.can_rework(mock_db, serial_id=999)

        assert result is False

    def test_can_rework_eligible(self):
        """Test can_rework returns True for eligible serial."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.can_rework.return_value = True
        mock_db.query().filter().first.return_value = mock_serial

        result = serial_crud.can_rework(mock_db, serial_id=1)

        assert result is True

    def test_can_rework_not_eligible(self):
        """Test can_rework returns False for ineligible serial."""
        mock_db = MagicMock()
        mock_serial = MagicMock(spec=Serial)
        mock_serial.can_rework.return_value = False
        mock_db.query().filter().first.return_value = mock_serial

        result = serial_crud.can_rework(mock_db, serial_id=1)

        assert result is False
