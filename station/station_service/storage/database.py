"""
Database module for Station Service.

This module provides async SQLite database access using aiosqlite.
Implements singleton pattern for database connection management.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Sequence

import aiosqlite

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path("data/station.db")

# Singleton instance
_database_instance: Optional[Database] = None


class DatabaseError(Exception):
    """Base exception for database errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""

    pass


class DatabaseQueryError(DatabaseError):
    """Exception raised when database query fails."""

    pass


class Database:
    """
    Async SQLite database wrapper using aiosqlite.

    Provides connection management and basic CRUD operations.
    Supports singleton pattern for shared database access.

    Usage:
        db = await Database.create("data/station.db")
        await db.init_db()

        # Execute queries
        await db.execute("INSERT INTO logs (batch_id, level, message) VALUES (?, ?, ?)",
                        ("batch_1", "info", "Test message"))

        # Fetch data
        row = await db.fetch_one("SELECT * FROM logs WHERE id = ?", (1,))
        rows = await db.fetch_all("SELECT * FROM logs WHERE batch_id = ?", ("batch_1",))

        # Close connection
        await db.close()
    """

    def __init__(self, db_path: Path | str) -> None:
        """
        Initialize database wrapper.

        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = Path(db_path)
        self._connection: Optional[aiosqlite.Connection] = None
        self._initialized = False

    @classmethod
    async def create(cls, db_path: Path | str = DEFAULT_DB_PATH) -> Database:
        """
        Factory method to create and connect database instance.

        Args:
            db_path: Path to SQLite database file.

        Returns:
            Connected Database instance.

        Raises:
            DatabaseConnectionError: If connection fails.
        """
        instance = cls(db_path)
        await instance._connect()
        return instance

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connection is not None

    @property
    def is_initialized(self) -> bool:
        """Check if database schema is initialized."""
        return self._initialized

    async def _connect(self) -> None:
        """
        Establish database connection.

        Raises:
            DatabaseConnectionError: If connection fails.
        """
        try:
            # Ensure parent directory exists
            self._db_path.parent.mkdir(parents=True, exist_ok=True)

            self._connection = await aiosqlite.connect(str(self._db_path))
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            # Use WAL mode for better concurrent access
            await self._connection.execute("PRAGMA journal_mode = WAL")
            # Enable row factory for dict-like access
            self._connection.row_factory = aiosqlite.Row

            logger.info(f"Database connected: {self._db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e

    async def init_db(self) -> None:
        """
        Initialize database schema from schema.sql file.

        Raises:
            DatabaseError: If initialization fails.
        """
        if not self._connection:
            raise DatabaseConnectionError("Database not connected")

        try:
            # Find schema.sql relative to this module
            schema_path = Path(__file__).parent / "schema.sql"

            if not schema_path.exists():
                raise DatabaseError(f"Schema file not found: {schema_path}")

            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            await self._connection.executescript(schema_sql)
            await self._connection.commit()

            self._initialized = True
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise DatabaseError(f"Failed to initialize database schema: {e}") from e

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                await self._connection.close()
                self._connection = None
                self._initialized = False
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
                raise DatabaseError(f"Error closing database connection: {e}") from e

    async def execute(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> int:
        """
        Execute a SQL query.

        Args:
            query: SQL query string.
            parameters: Query parameters.

        Returns:
            Last inserted row ID or number of affected rows.

        Raises:
            DatabaseQueryError: If query execution fails.
        """
        if not self._connection:
            raise DatabaseConnectionError("Database not connected")

        try:
            cursor = await self._connection.execute(query, parameters)
            await self._connection.commit()
            return cursor.lastrowid or cursor.rowcount
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseQueryError(f"Query execution failed: {e}") from e

    async def execute_many(
        self,
        query: str,
        parameters_list: Sequence[Sequence[Any]],
    ) -> int:
        """
        Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query string.
            parameters_list: List of parameter sequences.

        Returns:
            Number of affected rows.

        Raises:
            DatabaseQueryError: If query execution fails.
        """
        if not self._connection:
            raise DatabaseConnectionError("Database not connected")

        try:
            cursor = await self._connection.executemany(query, parameters_list)
            await self._connection.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Batch query execution failed: {e}")
            raise DatabaseQueryError(f"Batch query execution failed: {e}") from e

    async def fetch_one(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> Optional[dict[str, Any]]:
        """
        Fetch a single row from query result.

        Args:
            query: SQL query string.
            parameters: Query parameters.

        Returns:
            Row as dictionary or None if no result.

        Raises:
            DatabaseQueryError: If query execution fails.
        """
        if not self._connection:
            raise DatabaseConnectionError("Database not connected")

        try:
            cursor = await self._connection.execute(query, parameters)
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(row)
        except Exception as e:
            logger.error(f"Fetch one failed: {e}")
            raise DatabaseQueryError(f"Fetch one failed: {e}") from e

    async def fetch_all(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> list[dict[str, Any]]:
        """
        Fetch all rows from query result.

        Args:
            query: SQL query string.
            parameters: Query parameters.

        Returns:
            List of rows as dictionaries.

        Raises:
            DatabaseQueryError: If query execution fails.
        """
        if not self._connection:
            raise DatabaseConnectionError("Database not connected")

        try:
            cursor = await self._connection.execute(query, parameters)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Fetch all failed: {e}")
            raise DatabaseQueryError(f"Fetch all failed: {e}") from e

    async def fetch_value(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> Optional[Any]:
        """
        Fetch a single value from query result.

        Args:
            query: SQL query string.
            parameters: Query parameters.

        Returns:
            First column of first row or None.

        Raises:
            DatabaseQueryError: If query execution fails.
        """
        if not self._connection:
            raise DatabaseConnectionError("Database not connected")

        try:
            cursor = await self._connection.execute(query, parameters)
            row = await cursor.fetchone()
            if row is None:
                return None
            return row[0]
        except Exception as e:
            logger.error(f"Fetch value failed: {e}")
            raise DatabaseQueryError(f"Fetch value failed: {e}") from e

    async def __aenter__(self) -> Database:
        """Async context manager entry."""
        if not self._connection:
            await self._connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()


async def get_database(db_path: Path | str = DEFAULT_DB_PATH) -> Database:
    """
    Get or create singleton database instance.

    Args:
        db_path: Path to SQLite database file.

    Returns:
        Database instance.
    """
    global _database_instance

    if _database_instance is None or not _database_instance.is_connected:
        _database_instance = await Database.create(db_path)
        await _database_instance.init_db()

    return _database_instance


async def close_database() -> None:
    """Close singleton database instance."""
    global _database_instance

    if _database_instance is not None:
        await _database_instance.close()
        _database_instance = None
