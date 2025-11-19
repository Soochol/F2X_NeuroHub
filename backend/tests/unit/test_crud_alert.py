"""
Unit tests for Alert CRUD operations.

Tests for alert.py CRUD functions to improve coverage.
"""

import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError

from app.crud import alert as alert_crud
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus


class TestAlertGet:
    """Tests for get function."""

    def test_get_existing_alert(self):
        """Test getting an existing alert by ID."""
        mock_db = MagicMock()
        mock_alert = MagicMock(spec=Alert)
        mock_alert.id = 1
        mock_db.query().options().filter().first.return_value = mock_alert

        result = alert_crud.get(mock_db, alert_id=1)

        assert result is not None
        assert result.id == 1

    def test_get_nonexistent_alert(self):
        """Test getting an alert that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().options().filter().first.return_value = None

        result = alert_crud.get(mock_db, alert_id=999)

        assert result is None


class TestAlertGetMulti:
    """Tests for get_multi function."""

    def test_get_multi_no_filters(self):
        """Test getting multiple alerts without filters."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(5)]
        mock_db.query().options().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_multi(mock_db, skip=0, limit=10)

        assert len(result) == 5

    def test_get_multi_with_status_filter(self):
        """Test getting alerts filtered by status."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(3)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_multi(
            mock_db, status=AlertStatus.UNREAD, skip=0, limit=10
        )

        assert len(result) == 3

    def test_get_multi_with_severity_filter(self):
        """Test getting alerts filtered by severity."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(2)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_multi(
            mock_db, severity=AlertSeverity.HIGH, skip=0, limit=10
        )

        assert len(result) == 2

    def test_get_multi_with_date_range(self):
        """Test getting alerts filtered by date range."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(4)]
        mock_db.query().options().filter().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_multi(
            mock_db,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip=0,
            limit=10
        )

        assert len(result) == 4


class TestAlertCreate:
    """Tests for create function."""

    def test_create_alert_success(self):
        """Test creating an alert successfully."""
        mock_db = MagicMock()
        mock_alert_in = MagicMock()
        mock_alert_in.alert_type = AlertType.DEFECT_DETECTED
        mock_alert_in.severity = AlertSeverity.HIGH
        mock_alert_in.title = "Test Alert"
        mock_alert_in.message = "Test message"
        mock_alert_in.lot_id = 1
        mock_alert_in.serial_id = None
        mock_alert_in.process_id = 1
        mock_alert_in.equipment_id = "EQ-001"
        mock_alert_in.created_by_id = 1

        result = alert_crud.create(mock_db, mock_alert_in)

        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_alert_db_error(self):
        """Test creating alert with database error."""
        mock_db = MagicMock()
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        mock_alert_in = MagicMock()
        mock_alert_in.alert_type = AlertType.DEFECT_DETECTED
        mock_alert_in.severity = AlertSeverity.HIGH
        mock_alert_in.title = "Test Alert"
        mock_alert_in.message = "Test message"
        mock_alert_in.lot_id = 1
        mock_alert_in.serial_id = None
        mock_alert_in.process_id = 1
        mock_alert_in.equipment_id = None
        mock_alert_in.created_by_id = 1

        with pytest.raises(SQLAlchemyError):
            alert_crud.create(mock_db, mock_alert_in)

        mock_db.rollback.assert_called_once()


class TestAlertUpdate:
    """Tests for update function."""

    def test_update_alert_not_found(self):
        """Test updating alert that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().options().filter().first.return_value = None

        mock_alert_in = MagicMock()
        mock_alert_in.model_dump.return_value = {"status": AlertStatus.READ}

        result = alert_crud.update(mock_db, alert_id=999, alert_in=mock_alert_in)

        assert result is None

    def test_update_alert_to_read_status(self):
        """Test updating alert status to READ."""
        mock_db = MagicMock()
        mock_alert = MagicMock(spec=Alert)
        mock_alert.read_at = None
        mock_db.query().options().filter().first.return_value = mock_alert

        mock_alert_in = MagicMock()
        mock_alert_in.model_dump.return_value = {"status": AlertStatus.READ}

        result = alert_crud.update(mock_db, alert_id=1, alert_in=mock_alert_in)

        assert result is not None
        mock_db.commit.assert_called_once()

    def test_update_alert_to_archived_status(self):
        """Test updating alert status to ARCHIVED."""
        mock_db = MagicMock()
        mock_alert = MagicMock(spec=Alert)
        mock_alert.archived_at = None
        mock_db.query().options().filter().first.return_value = mock_alert

        mock_alert_in = MagicMock()
        mock_alert_in.model_dump.return_value = {"status": AlertStatus.ARCHIVED}

        result = alert_crud.update(mock_db, alert_id=1, alert_in=mock_alert_in)

        assert result is not None


class TestAlertDelete:
    """Tests for delete function."""

    def test_delete_alert_found(self):
        """Test deleting alert that exists."""
        mock_db = MagicMock()
        mock_alert = MagicMock(spec=Alert)
        mock_db.query().options().filter().first.return_value = mock_alert

        result = alert_crud.delete(mock_db, alert_id=1)

        assert result is True
        mock_db.delete.assert_called_once()

    def test_delete_alert_not_found(self):
        """Test deleting alert that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().options().filter().first.return_value = None

        result = alert_crud.delete(mock_db, alert_id=999)

        assert result is False


class TestAlertMarkAsRead:
    """Tests for mark_as_read function."""

    def test_mark_as_read_unread_alert(self):
        """Test marking an unread alert as read."""
        mock_db = MagicMock()
        mock_alert = MagicMock(spec=Alert)
        mock_alert.status = AlertStatus.UNREAD
        mock_db.query().options().filter().first.return_value = mock_alert

        result = alert_crud.mark_as_read(mock_db, alert_id=1, read_by_id=1)

        assert result is not None
        mock_db.commit.assert_called_once()

    def test_mark_as_read_already_read_alert(self):
        """Test marking an already read alert (should not update)."""
        mock_db = MagicMock()
        mock_alert = MagicMock(spec=Alert)
        mock_alert.status = AlertStatus.READ
        mock_db.query().options().filter().first.return_value = mock_alert

        result = alert_crud.mark_as_read(mock_db, alert_id=1, read_by_id=1)

        assert result is not None
        mock_db.commit.assert_not_called()

    def test_mark_as_read_not_found(self):
        """Test marking as read for nonexistent alert."""
        mock_db = MagicMock()
        mock_db.query().options().filter().first.return_value = None

        result = alert_crud.mark_as_read(mock_db, alert_id=999, read_by_id=1)

        assert result is None


class TestAlertBulkMarkAsRead:
    """Tests for bulk_mark_as_read function."""

    def test_bulk_mark_as_read_success(self):
        """Test bulk marking alerts as read."""
        mock_db = MagicMock()
        mock_db.query().filter().update.return_value = 5

        result = alert_crud.bulk_mark_as_read(
            mock_db, alert_ids=[1, 2, 3, 4, 5], read_by_id=1
        )

        assert result == 5
        mock_db.commit.assert_called_once()

    def test_bulk_mark_as_read_db_error(self):
        """Test bulk mark as read with database error."""
        mock_db = MagicMock()
        mock_db.query().filter().update.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            alert_crud.bulk_mark_as_read(
                mock_db, alert_ids=[1, 2, 3], read_by_id=1
            )

        mock_db.rollback.assert_called_once()


class TestAlertGetUnreadCount:
    """Tests for get_unread_count function."""

    def test_get_unread_count(self):
        """Test getting unread alert count."""
        mock_db = MagicMock()
        mock_db.query().filter().scalar.return_value = 10

        result = alert_crud.get_unread_count(mock_db)

        assert result == 10

    def test_get_unread_count_none(self):
        """Test getting unread count when result is None."""
        mock_db = MagicMock()
        mock_db.query().filter().scalar.return_value = None

        result = alert_crud.get_unread_count(mock_db)

        assert result == 0


class TestAlertGetByStatus:
    """Tests for get_by_status function."""

    def test_get_by_status(self):
        """Test getting alerts by status."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(3)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_by_status(mock_db, status=AlertStatus.UNREAD)

        assert len(result) == 3


class TestAlertGetBySeverity:
    """Tests for get_by_severity function."""

    def test_get_by_severity(self):
        """Test getting alerts by severity."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(2)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_by_severity(mock_db, severity=AlertSeverity.HIGH)

        assert len(result) == 2


class TestAlertGetByType:
    """Tests for get_by_type function."""

    def test_get_by_type(self):
        """Test getting alerts by type."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(4)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_by_type(mock_db, alert_type=AlertType.DEFECT_DETECTED)

        assert len(result) == 4


class TestAlertGetByLot:
    """Tests for get_by_lot function."""

    def test_get_by_lot(self):
        """Test getting alerts by lot ID."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(3)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_by_lot(mock_db, lot_id=1)

        assert len(result) == 3


class TestAlertGetBySerial:
    """Tests for get_by_serial function."""

    def test_get_by_serial(self):
        """Test getting alerts by serial ID."""
        mock_db = MagicMock()
        mock_alerts = [MagicMock(spec=Alert) for _ in range(2)]
        mock_db.query().options().filter().order_by().offset().limit().all.return_value = mock_alerts

        result = alert_crud.get_by_serial(mock_db, serial_id=1)

        assert len(result) == 2
