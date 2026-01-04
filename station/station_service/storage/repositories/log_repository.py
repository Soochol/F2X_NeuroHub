"""
Log Repository for Station Service.

Provides CRUD operations for LogEntry entities.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from station_service.storage.database import Database

logger = logging.getLogger(__name__)


class LogRepository:
    """
    Repository for LogEntry CRUD operations.

    Handles persistence of log entries to SQLite database.

    Usage:
        db = await get_database()
        repo = LogRepository(db)

        # Create log entry
        await repo.create_log(
            batch_id="batch_1",
            level="info",
            message="Sequence started",
            execution_id="exec_123"
        )

        # Get logs for batch
        logs = await repo.get_logs_by_batch("batch_1", limit=100)

        # Delete old logs
        await repo.delete_logs_before(datetime(2025, 1, 1))
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize repository with database instance.

        Args:
            db: Database instance for queries.
        """
        self._db = db

    async def create_log(
        self,
        batch_id: str,
        level: str,
        message: str,
        execution_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> int:
        """
        Create a new log entry.

        Args:
            batch_id: Batch ID for the log.
            level: Log level (debug, info, warning, error).
            message: Log message.
            execution_id: Optional associated execution ID.
            timestamp: Log timestamp (defaults to now).

        Returns:
            Created log entry ID.
        """
        if timestamp is None:
            timestamp = datetime.now()

        row_id = await self._db.execute(
            """
            INSERT INTO logs (batch_id, execution_id, level, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                batch_id,
                execution_id,
                level,
                message,
                timestamp.isoformat(),
            ),
        )

        logger.debug(f"Created log entry: {level} - {message[:50]}")
        return row_id

    async def create_logs_batch(
        self,
        logs: list[dict[str, Any]],
    ) -> int:
        """
        Create multiple log entries in batch.

        Args:
            logs: List of log entries with keys:
                  batch_id, level, message, execution_id (optional),
                  timestamp (optional).

        Returns:
            Number of created entries.
        """
        parameters = []
        for log in logs:
            timestamp = log.get("timestamp") or datetime.now()
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()

            parameters.append((
                log["batch_id"],
                log.get("execution_id"),
                log["level"],
                log["message"],
                timestamp,
            ))

        return await self._db.execute_many(
            """
            INSERT INTO logs (batch_id, execution_id, level, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            parameters,
        )

    async def get_log(self, id: int) -> Optional[dict[str, Any]]:
        """
        Get log entry by ID.

        Args:
            id: Log entry ID.

        Returns:
            Log entry as dict or None if not found.
        """
        return await self._db.fetch_one(
            "SELECT * FROM logs WHERE id = ?",
            (id,),
        )

    async def get_logs_by_batch(
        self,
        batch_id: str,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_desc: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Get log entries for a batch.

        Args:
            batch_id: Batch ID.
            level: Filter by log level.
            execution_id: Filter by execution ID.
            limit: Maximum number of results.
            offset: Result offset for pagination.
            order_desc: Order by timestamp descending (newest first).

        Returns:
            List of log entries.
        """
        query = "SELECT * FROM logs WHERE batch_id = ?"
        params: list[Any] = [batch_id]

        if level:
            query += " AND level = ?"
            params.append(level)

        if execution_id:
            query += " AND execution_id = ?"
            params.append(execution_id)

        order = "DESC" if order_desc else "ASC"
        query += f" ORDER BY timestamp {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return await self._db.fetch_all(query, params)

    async def get_logs_by_execution(
        self,
        execution_id: str,
        level: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Get log entries for an execution.

        Args:
            execution_id: Execution ID.
            level: Filter by log level.
            limit: Maximum number of results.
            offset: Result offset for pagination.

        Returns:
            List of log entries.
        """
        query = "SELECT * FROM logs WHERE execution_id = ?"
        params: list[Any] = [execution_id]

        if level:
            query += " AND level = ?"
            params.append(level)

        query += " ORDER BY timestamp ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return await self._db.fetch_all(query, params)

    async def get_recent_logs(
        self,
        limit: int = 100,
        level: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent log entries across all batches.

        Args:
            limit: Maximum number of results.
            level: Filter by log level.
            since: Filter entries after this timestamp.

        Returns:
            List of log entries ordered by timestamp descending.
        """
        query = "SELECT * FROM logs WHERE 1=1"
        params: list[Any] = []

        if level:
            query += " AND level = ?"
            params.append(level)

        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        return await self._db.fetch_all(query, params)

    async def get_error_logs(
        self,
        batch_id: Optional[str] = None,
        limit: int = 100,
        since: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Get error and warning log entries.

        Args:
            batch_id: Filter by batch ID.
            limit: Maximum number of results.
            since: Filter entries after this timestamp.

        Returns:
            List of error/warning log entries.
        """
        query = "SELECT * FROM logs WHERE level IN ('error', 'warning')"
        params: list[Any] = []

        if batch_id:
            query += " AND batch_id = ?"
            params.append(batch_id)

        if since:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        return await self._db.fetch_all(query, params)

    async def count_logs(
        self,
        batch_id: Optional[str] = None,
        level: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> int:
        """
        Count log entries.

        Args:
            batch_id: Filter by batch ID.
            level: Filter by log level.
            execution_id: Filter by execution ID.

        Returns:
            Count of matching log entries.
        """
        query = "SELECT COUNT(*) FROM logs WHERE 1=1"
        params: list[Any] = []

        if batch_id:
            query += " AND batch_id = ?"
            params.append(batch_id)

        if level:
            query += " AND level = ?"
            params.append(level)

        if execution_id:
            query += " AND execution_id = ?"
            params.append(execution_id)

        result = await self._db.fetch_value(query, params)
        return result or 0

    async def delete_log(self, id: int) -> bool:
        """
        Delete log entry by ID.

        Args:
            id: Log entry ID.

        Returns:
            True if deleted, False otherwise.
        """
        result = await self._db.execute(
            "DELETE FROM logs WHERE id = ?",
            (id,),
        )
        return result > 0

    async def delete_logs_by_batch(self, batch_id: str) -> int:
        """
        Delete all log entries for a batch.

        Args:
            batch_id: Batch ID.

        Returns:
            Number of deleted entries.
        """
        return await self._db.execute(
            "DELETE FROM logs WHERE batch_id = ?",
            (batch_id,),
        )

    async def delete_logs_by_execution(self, execution_id: str) -> int:
        """
        Delete all log entries for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Number of deleted entries.
        """
        return await self._db.execute(
            "DELETE FROM logs WHERE execution_id = ?",
            (execution_id,),
        )

    async def delete_logs_before(self, before: datetime) -> int:
        """
        Delete log entries older than specified timestamp.

        Args:
            before: Delete entries with timestamp before this.

        Returns:
            Number of deleted entries.
        """
        return await self._db.execute(
            "DELETE FROM logs WHERE timestamp < ?",
            (before.isoformat(),),
        )

    async def cleanup_old_logs(
        self,
        days: int = 30,
        keep_errors: bool = True,
    ) -> int:
        """
        Clean up old log entries.

        Args:
            days: Delete logs older than this many days.
            keep_errors: Keep error logs even if old.

        Returns:
            Number of deleted entries.
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)

        query = "DELETE FROM logs WHERE timestamp < ?"
        params: list[Any] = [cutoff.isoformat()]

        if keep_errors:
            query += " AND level NOT IN ('error', 'warning')"

        return await self._db.execute(query, params)
