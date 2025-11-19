"""
Extended unit tests for Process CRUD operations.

Tests additional scenarios to improve coverage for process.py CRUD functions.
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.crud import process as process_crud
from app.models.process import Process


class TestProcessGet:
    """Tests for get function."""

    def test_get_existing_process(self):
        """Test getting an existing process by ID."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_process.id = 1
        mock_process.process_name_en = "Laser Marking"
        mock_db.query().filter().first.return_value = mock_process

        result = process_crud.get(mock_db, process_id=1)

        assert result is not None
        assert result.id == 1

    def test_get_nonexistent_process(self):
        """Test getting a process that doesn't exist."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = process_crud.get(mock_db, process_id=999)

        assert result is None


class TestProcessGetMulti:
    """Tests for get_multi function."""

    def test_get_multi_no_filter(self):
        """Test getting multiple processes without filter."""
        mock_db = MagicMock()
        mock_processes = [MagicMock(spec=Process) for _ in range(8)]
        mock_db.query().order_by().offset().limit().all.return_value = mock_processes

        result = process_crud.get_multi(mock_db, skip=0, limit=10)

        assert len(result) == 8

    def test_get_multi_with_active_filter(self):
        """Test getting processes filtered by active status."""
        mock_db = MagicMock()
        mock_processes = [MagicMock(spec=Process) for _ in range(5)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_processes

        result = process_crud.get_multi(mock_db, skip=0, limit=10, is_active=True)

        assert len(result) == 5

    def test_get_multi_inactive(self):
        """Test getting inactive processes."""
        mock_db = MagicMock()
        mock_processes = [MagicMock(spec=Process) for _ in range(2)]
        mock_db.query().filter().order_by().offset().limit().all.return_value = mock_processes

        result = process_crud.get_multi(mock_db, is_active=False)

        assert len(result) == 2


class TestProcessCreate:
    """Tests for create function."""

    def test_create_process_success(self):
        """Test creating a process successfully."""
        mock_db = MagicMock()
        mock_process_in = MagicMock()
        mock_process_in.process_number = 1
        mock_process_in.process_code = "LASER_MARKING"
        mock_process_in.process_name_ko = "레이저 마킹"
        mock_process_in.process_name_en = "Laser Marking"
        mock_process_in.description = None
        mock_process_in.estimated_duration_seconds = 60
        mock_process_in.quality_criteria = {}
        mock_process_in.is_active = True
        mock_process_in.sort_order = 1

        result = process_crud.create(mock_db, mock_process_in)

        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_process_integrity_error(self):
        """Test creating process with duplicate data raises IntegrityError."""
        mock_db = MagicMock()
        mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        mock_process_in = MagicMock()
        mock_process_in.process_number = 1
        mock_process_in.process_code = "LASER_MARKING"
        mock_process_in.process_name_ko = "레이저 마킹"
        mock_process_in.process_name_en = "Laser Marking"
        mock_process_in.description = None
        mock_process_in.estimated_duration_seconds = 60
        mock_process_in.quality_criteria = {}
        mock_process_in.is_active = True
        mock_process_in.sort_order = 1

        with pytest.raises(IntegrityError):
            process_crud.create(mock_db, mock_process_in)

        mock_db.rollback.assert_called_once()

    def test_create_process_sqlalchemy_error(self):
        """Test creating process with SQLAlchemy error."""
        mock_db = MagicMock()
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        mock_process_in = MagicMock()
        mock_process_in.process_number = 2
        mock_process_in.process_code = "QUALITY_CHECK"
        mock_process_in.process_name_ko = "품질 검사"
        mock_process_in.process_name_en = "Quality Check"
        mock_process_in.description = None
        mock_process_in.estimated_duration_seconds = 30
        mock_process_in.quality_criteria = {}
        mock_process_in.is_active = True
        mock_process_in.sort_order = 2

        with pytest.raises(SQLAlchemyError):
            process_crud.create(mock_db, mock_process_in)

        mock_db.rollback.assert_called_once()


class TestProcessUpdate:
    """Tests for update function."""

    def test_update_process_not_found(self):
        """Test updating process that doesn't exist returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        mock_process_in = MagicMock()
        mock_process_in.model_dump.return_value = {"description": "Updated"}

        result = process_crud.update(mock_db, process_id=999, process_in=mock_process_in)

        assert result is None

    def test_update_process_success(self):
        """Test updating process successfully."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process

        mock_process_in = MagicMock()
        mock_process_in.model_dump.return_value = {"description": "Updated"}

        result = process_crud.update(mock_db, process_id=1, process_in=mock_process_in)

        assert result is not None
        mock_db.commit.assert_called_once()

    def test_update_process_integrity_error(self):
        """Test updating process with integrity error."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process
        mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        mock_process_in = MagicMock()
        mock_process_in.model_dump.return_value = {"process_code": "DUPLICATE"}

        with pytest.raises(IntegrityError):
            process_crud.update(mock_db, process_id=1, process_in=mock_process_in)

        mock_db.rollback.assert_called_once()

    def test_update_process_sqlalchemy_error(self):
        """Test updating process with SQLAlchemy error."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        mock_process_in = MagicMock()
        mock_process_in.model_dump.return_value = {"is_active": False}

        with pytest.raises(SQLAlchemyError):
            process_crud.update(mock_db, process_id=1, process_in=mock_process_in)

        mock_db.rollback.assert_called_once()


class TestProcessDelete:
    """Tests for delete function."""

    def test_delete_process_not_found(self):
        """Test deleting process that doesn't exist returns False."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = process_crud.delete(mock_db, process_id=999)

        assert result is False

    def test_delete_process_success(self):
        """Test deleting process successfully."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process

        result = process_crud.delete(mock_db, process_id=1)

        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_delete_process_integrity_error(self):
        """Test deleting process with FK constraint violation."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process
        mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        with pytest.raises(IntegrityError):
            process_crud.delete(mock_db, process_id=1)

        mock_db.rollback.assert_called_once()

    def test_delete_process_sqlalchemy_error(self):
        """Test deleting process with SQLAlchemy error."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process
        mock_db.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            process_crud.delete(mock_db, process_id=1)

        mock_db.rollback.assert_called_once()


class TestProcessGetByNumber:
    """Tests for get_by_number function."""

    def test_get_by_number_found(self):
        """Test getting process by number when found."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_process.process_number = 1
        mock_db.query().filter().first.return_value = mock_process

        result = process_crud.get_by_number(mock_db, process_number=1)

        assert result is not None
        assert result.process_number == 1

    def test_get_by_number_not_found(self):
        """Test getting process by number when not found."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = process_crud.get_by_number(mock_db, process_number=99)

        assert result is None


class TestProcessGetByCode:
    """Tests for get_by_code function."""

    def test_get_by_code_found(self):
        """Test getting process by code when found."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_process.process_code = "LASER_MARKING"
        mock_db.query().filter().first.return_value = mock_process

        result = process_crud.get_by_code(mock_db, process_code="LASER_MARKING")

        assert result is not None

    def test_get_by_code_lowercase(self):
        """Test getting process by lowercase code (should uppercase)."""
        mock_db = MagicMock()
        mock_process = MagicMock(spec=Process)
        mock_db.query().filter().first.return_value = mock_process

        result = process_crud.get_by_code(mock_db, process_code="laser_marking")

        assert result is not None


class TestProcessGetActive:
    """Tests for get_active function."""

    def test_get_active_processes(self):
        """Test getting all active processes."""
        mock_db = MagicMock()
        mock_processes = [MagicMock(spec=Process) for _ in range(8)]
        mock_db.query().filter().order_by().all.return_value = mock_processes

        result = process_crud.get_active(mock_db)

        assert len(result) == 8


class TestProcessGetSequence:
    """Tests for get_sequence function."""

    def test_get_sequence(self):
        """Test getting processes in sequential order."""
        mock_db = MagicMock()
        mock_processes = [MagicMock(spec=Process) for _ in range(8)]
        for i, p in enumerate(mock_processes):
            p.process_number = i + 1
        mock_db.query().filter().order_by().all.return_value = mock_processes

        result = process_crud.get_sequence(mock_db)

        assert len(result) == 8
