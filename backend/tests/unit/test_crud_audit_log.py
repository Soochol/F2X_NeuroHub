"""
Unit tests for Audit Log CRUD operations.

Tests the read-only CRUD functions for the audit log system which provides
an immutable audit trail for all database changes.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.crud import audit_log as audit_log_crud
from app.models.audit_log import AuditLog, AuditAction


class TestAuditLogGet:
    """Tests for get() function - retrieve single audit log by ID."""

    def test_get_existing_audit_log(self):
        """Test retrieving an existing audit log by ID."""
        # Arrange
        mock_db = MagicMock()
        mock_log = MagicMock(spec=AuditLog)
        mock_log.id = 1
        mock_log.action = "CREATE"
        mock_db.query().filter().first.return_value = mock_log

        # Act
        result = audit_log_crud.get(mock_db, id=1)

        # Assert
        assert result is not None
        assert result.id == 1

    def test_get_nonexistent_audit_log(self):
        """Test retrieving non-existent audit log returns None."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        # Act
        result = audit_log_crud.get(mock_db, id=999)

        # Assert
        assert result is None


class TestAuditLogGetMulti:
    """Tests for get_multi() function - retrieve multiple audit logs with pagination."""

    def test_get_multi_default_pagination(self):
        """Test get_multi with default pagination values."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(10)]
        mock_db.query().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_multi(mock_db)

        # Assert
        assert len(result) == 10

    def test_get_multi_custom_pagination(self):
        """Test get_multi with custom skip and limit values."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(5)]
        mock_db.query().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_multi(mock_db, skip=10, limit=5)

        # Assert
        assert len(result) == 5

    def test_get_multi_empty_result(self):
        """Test get_multi returns empty list when no logs exist."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().order_by().offset().limit().all.return_value = []

        # Act
        result = audit_log_crud.get_multi(mock_db, skip=1000, limit=10)

        # Assert
        assert result == []


class TestAuditLogGetByEntity:
    """Tests for get_by_entity() function - filter by entity type and ID."""

    def test_get_by_entity_with_results(self):
        """Test filtering audit logs by entity type and ID."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_entity(
            mock_db, entity_type="lots", entity_id=123
        )

        # Assert
        assert len(result) == 3

    def test_get_by_entity_no_results(self):
        """Test get_by_entity returns empty list when no matching logs."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        # Act
        result = audit_log_crud.get_by_entity(
            mock_db, entity_type="nonexistent", entity_id=999
        )

        # Assert
        assert result == []

    def test_get_by_entity_with_pagination(self):
        """Test get_by_entity with custom pagination."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(2)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_entity(
            mock_db, entity_type="serials", entity_id=456, skip=5, limit=2
        )

        # Assert
        assert len(result) == 2


class TestAuditLogGetByUser:
    """Tests for get_by_user() function - filter by user ID."""

    def test_get_by_user_with_results(self):
        """Test filtering audit logs by user ID."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(5)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_user(mock_db, user_id=1)

        # Assert
        assert len(result) == 5

    def test_get_by_user_no_results(self):
        """Test get_by_user returns empty list for user with no activity."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        # Act
        result = audit_log_crud.get_by_user(mock_db, user_id=999)

        # Assert
        assert result == []

    def test_get_by_user_with_pagination(self):
        """Test get_by_user with custom pagination."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(10)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_user(mock_db, user_id=5, skip=20, limit=10)

        # Assert
        assert len(result) == 10


class TestAuditLogGetByAction:
    """Tests for get_by_action() function - filter by action type."""

    def test_get_by_action_create(self):
        """Test filtering audit logs by CREATE action."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(4)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_action(mock_db, action="CREATE")

        # Assert
        assert len(result) == 4

    def test_get_by_action_update(self):
        """Test filtering audit logs by UPDATE action."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(6)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_action(mock_db, action="UPDATE")

        # Assert
        assert len(result) == 6

    def test_get_by_action_delete(self):
        """Test filtering audit logs by DELETE action."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(2)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_action(mock_db, action="DELETE")

        # Assert
        assert len(result) == 2

    def test_get_by_action_invalid_raises_error(self):
        """Test get_by_action raises ValueError for invalid action."""
        # Arrange
        mock_db = MagicMock()

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            audit_log_crud.get_by_action(mock_db, action="INVALID")

        assert "Invalid action" in str(exc_info.value)

    def test_get_by_action_with_pagination(self):
        """Test get_by_action with custom pagination."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_by_action(
            mock_db, action="CREATE", skip=10, limit=3
        )

        # Assert
        assert len(result) == 3


class TestAuditLogGetByDateRange:
    """Tests for get_by_date_range() function - filter by date range."""

    def test_get_by_date_range_with_results(self):
        """Test filtering audit logs by date range."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(7)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        start_date = datetime(2025, 11, 1, tzinfo=timezone.utc)
        end_date = datetime(2025, 11, 30, tzinfo=timezone.utc)

        # Act
        result = audit_log_crud.get_by_date_range(
            mock_db, start_date=start_date, end_date=end_date
        )

        # Assert
        assert len(result) == 7

    def test_get_by_date_range_no_results(self):
        """Test get_by_date_range returns empty list when no logs in range."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2020, 1, 2, tzinfo=timezone.utc)

        # Act
        result = audit_log_crud.get_by_date_range(
            mock_db, start_date=start_date, end_date=end_date
        )

        # Assert
        assert result == []

    def test_get_by_date_range_single_day(self):
        """Test filtering audit logs for a single day."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(3)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        target_date = datetime(2025, 11, 19, tzinfo=timezone.utc)
        next_day = target_date + timedelta(days=1)

        # Act
        result = audit_log_crud.get_by_date_range(
            mock_db, start_date=target_date, end_date=next_day
        )

        # Assert
        assert len(result) == 3

    def test_get_by_date_range_with_pagination(self):
        """Test get_by_date_range with custom pagination."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(5)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        start_date = datetime(2025, 11, 1, tzinfo=timezone.utc)
        end_date = datetime(2025, 11, 30, tzinfo=timezone.utc)

        # Act
        result = audit_log_crud.get_by_date_range(
            mock_db, start_date=start_date, end_date=end_date, skip=10, limit=5
        )

        # Assert
        assert len(result) == 5


class TestAuditLogGetEntityHistory:
    """Tests for get_entity_history() function - complete change history for entity."""

    def test_get_entity_history_with_results(self):
        """Test retrieving complete history for an entity."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(8)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_entity_history(
            mock_db, entity_type="lots", entity_id=123
        )

        # Assert
        assert len(result) == 8

    def test_get_entity_history_no_results(self):
        """Test get_entity_history returns empty list for entity with no history."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        # Act
        result = audit_log_crud.get_entity_history(
            mock_db, entity_type="serials", entity_id=999
        )

        # Assert
        assert result == []

    def test_get_entity_history_with_pagination(self):
        """Test get_entity_history with custom pagination."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(10)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_entity_history(
            mock_db, entity_type="product_models", entity_id=5, skip=0, limit=10
        )

        # Assert
        assert len(result) == 10


class TestAuditLogGetUserActivity:
    """Tests for get_user_activity() function - activity log for user."""

    def test_get_user_activity_with_results(self):
        """Test retrieving activity log for a user."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(15)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_user_activity(mock_db, user_id=5)

        # Assert
        assert len(result) == 15

    def test_get_user_activity_no_results(self):
        """Test get_user_activity returns empty list for user with no activity."""
        # Arrange
        mock_db = MagicMock()
        mock_db.query().filter().order_by().offset().limit().all.return_value = []

        # Act
        result = audit_log_crud.get_user_activity(mock_db, user_id=999)

        # Assert
        assert result == []

    def test_get_user_activity_with_pagination(self):
        """Test get_user_activity with custom pagination."""
        # Arrange
        mock_db = MagicMock()
        mock_logs = [MagicMock(spec=AuditLog) for _ in range(25)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_logs

        # Act
        result = audit_log_crud.get_user_activity(
            mock_db, user_id=3, skip=50, limit=25
        )

        # Assert
        assert len(result) == 25
