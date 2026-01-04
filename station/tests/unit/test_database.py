"""
Unit tests for the Database class.

Tests database connection, schema initialization, and CRUD operations.
"""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from station_service.storage.database import (
    Database,
    DatabaseConnectionError,
    DatabaseError,
    DatabaseQueryError,
)


class TestDatabase:
    """Test suite for Database."""

    @pytest_asyncio.fixture
    async def db_path(self) -> Path:
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test.db"

    @pytest_asyncio.fixture
    async def db(self, db_path: Path) -> Database:
        """Create and initialize a test database."""
        database = await Database.create(db_path)
        await database.init_db()
        yield database
        await database.close()

    # ============================================================
    # Connection Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_create_connects_database(self, db_path: Path):
        """Test that create() establishes database connection."""
        db = await Database.create(db_path)

        assert db.is_connected is True

        await db.close()

    @pytest.mark.asyncio
    async def test_create_creates_parent_directories(self):
        """Test that create() creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            deep_path = Path(tmpdir) / "a" / "b" / "c" / "test.db"
            db = await Database.create(deep_path)

            assert deep_path.parent.exists()

            await db.close()

    @pytest.mark.asyncio
    async def test_close_disconnects_database(self, db_path: Path):
        """Test that close() disconnects the database."""
        db = await Database.create(db_path)
        await db.close()

        assert db.is_connected is False

    @pytest.mark.asyncio
    async def test_context_manager(self, db_path: Path):
        """Test database context manager."""
        async with Database(db_path) as db:
            assert db.is_connected is True

        assert db.is_connected is False

    # ============================================================
    # Schema Initialization Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, db_path: Path):
        """Test that init_db() creates all required tables."""
        db = await Database.create(db_path)
        await db.init_db()

        # Check tables exist
        tables = await db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = {t["name"] for t in tables}

        assert "execution_results" in table_names
        assert "step_results" in table_names
        assert "logs" in table_names
        assert "sync_queue" in table_names

        await db.close()

    @pytest.mark.asyncio
    async def test_init_db_sets_initialized_flag(self, db_path: Path):
        """Test that init_db() sets the initialized flag."""
        db = await Database.create(db_path)

        assert db.is_initialized is False

        await db.init_db()

        assert db.is_initialized is True

        await db.close()

    @pytest.mark.asyncio
    async def test_init_db_without_connection_raises(self, db_path: Path):
        """Test that init_db() raises when not connected."""
        db = Database(db_path)

        with pytest.raises(DatabaseConnectionError):
            await db.init_db()

    # ============================================================
    # Execute Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_execute_insert(self, db: Database):
        """Test executing INSERT statement."""
        row_id = await db.execute(
            """
            INSERT INTO logs (batch_id, level, message)
            VALUES (?, ?, ?)
            """,
            ("batch_001", "info", "Test message"),
        )

        assert row_id is not None
        assert row_id > 0

    @pytest.mark.asyncio
    async def test_execute_update(self, db: Database):
        """Test executing UPDATE statement."""
        # Insert first
        await db.execute(
            "INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
            ("batch_001", "info", "Original"),
        )

        # Update
        affected = await db.execute(
            "UPDATE logs SET message = ? WHERE batch_id = ?",
            ("Updated", "batch_001"),
        )

        assert affected >= 1

    @pytest.mark.asyncio
    async def test_execute_delete(self, db: Database):
        """Test executing DELETE statement."""
        # Insert first
        await db.execute(
            "INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
            ("batch_001", "info", "To delete"),
        )

        # Delete
        affected = await db.execute(
            "DELETE FROM logs WHERE batch_id = ?",
            ("batch_001",),
        )

        assert affected >= 1

    @pytest.mark.asyncio
    async def test_execute_without_connection_raises(self, db_path: Path):
        """Test that execute() raises when not connected."""
        db = Database(db_path)

        with pytest.raises(DatabaseConnectionError):
            await db.execute("SELECT 1")

    @pytest.mark.asyncio
    async def test_execute_many(self, db: Database):
        """Test executing batch inserts."""
        data = [
            ("batch_001", "info", "Message 1"),
            ("batch_001", "warning", "Message 2"),
            ("batch_002", "error", "Message 3"),
        ]

        affected = await db.execute_many(
            "INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
            data,
        )

        assert affected == 3

    # ============================================================
    # Fetch Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_fetch_one(self, db: Database):
        """Test fetching single row."""
        await db.execute(
            "INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
            ("batch_001", "info", "Test"),
        )

        row = await db.fetch_one(
            "SELECT * FROM logs WHERE batch_id = ?",
            ("batch_001",),
        )

        assert row is not None
        assert row["batch_id"] == "batch_001"
        assert row["level"] == "info"
        assert row["message"] == "Test"

    @pytest.mark.asyncio
    async def test_fetch_one_returns_none_for_no_match(self, db: Database):
        """Test that fetch_one() returns None when no match."""
        row = await db.fetch_one(
            "SELECT * FROM logs WHERE batch_id = ?",
            ("nonexistent",),
        )

        assert row is None

    @pytest.mark.asyncio
    async def test_fetch_all(self, db: Database):
        """Test fetching multiple rows."""
        # Insert multiple
        await db.execute_many(
            "INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
            [
                ("batch_001", "info", "Msg 1"),
                ("batch_001", "warning", "Msg 2"),
            ],
        )

        rows = await db.fetch_all(
            "SELECT * FROM logs WHERE batch_id = ?",
            ("batch_001",),
        )

        assert len(rows) == 2

    @pytest.mark.asyncio
    async def test_fetch_all_returns_empty_list(self, db: Database):
        """Test that fetch_all() returns empty list for no matches."""
        rows = await db.fetch_all(
            "SELECT * FROM logs WHERE batch_id = ?",
            ("nonexistent",),
        )

        assert rows == []

    @pytest.mark.asyncio
    async def test_fetch_value(self, db: Database):
        """Test fetching single value."""
        await db.execute(
            "INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
            ("batch_001", "info", "Test"),
        )

        count = await db.fetch_value("SELECT COUNT(*) FROM logs")

        assert count == 1

    @pytest.mark.asyncio
    async def test_fetch_value_returns_none_for_no_match(self, db: Database):
        """Test that fetch_value() returns None when no match."""
        value = await db.fetch_value(
            "SELECT message FROM logs WHERE batch_id = ?",
            ("nonexistent",),
        )

        assert value is None

    # ============================================================
    # Error Handling Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_invalid_sql_raises_query_error(self, db: Database):
        """Test that invalid SQL raises DatabaseQueryError."""
        with pytest.raises(DatabaseQueryError):
            await db.execute("INVALID SQL SYNTAX")

    @pytest.mark.asyncio
    async def test_foreign_key_violation_raises(self, db: Database):
        """Test that foreign key violations raise errors."""
        # Try to insert step_result with non-existent execution_id
        with pytest.raises(DatabaseQueryError):
            await db.execute(
                """
                INSERT INTO step_results (execution_id, step_name, step_order, status, pass)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("nonexistent_exec", "step1", 1, "completed", True),
            )
