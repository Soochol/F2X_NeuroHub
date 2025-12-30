"""
Execution Repository for Station Service.

Provides CRUD operations for ExecutionResult and StepResult entities.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from station_service.storage.database import Database

logger = logging.getLogger(__name__)


class ExecutionRepository:
    """
    Repository for ExecutionResult and StepResult CRUD operations.

    Handles persistence of execution results and step results to SQLite database.

    Usage:
        db = await get_database()
        repo = ExecutionRepository(db)

        # Create execution result
        await repo.create_execution(
            id="exec_20250120_123456",
            batch_id="batch_1",
            sequence_name="PCB_Test",
            sequence_version="1.0.0",
            status="running",
            started_at=datetime.now(),
            parameters={"voltage": 5.0}
        )

        # Add step results
        await repo.create_step_result(
            execution_id="exec_20250120_123456",
            step_name="measure_voltage",
            step_order=1,
            status="completed",
            pass_result=True,
            duration=1.5,
            result={"voltage": 5.01}
        )

        # Update execution status
        await repo.update_execution_status(
            id="exec_20250120_123456",
            status="completed",
            overall_pass=True,
            completed_at=datetime.now(),
            duration=10
        )
    """

    def __init__(self, db: Database) -> None:
        """
        Initialize repository with database instance.

        Args:
            db: Database instance for queries.
        """
        self._db = db

    # ==================== Execution Result CRUD ====================

    async def create_execution(
        self,
        id: str,
        batch_id: str,
        sequence_name: str,
        sequence_version: str,
        status: str,
        started_at: datetime,
        parameters: Optional[dict[str, Any]] = None,
        overall_pass: Optional[bool] = None,
        completed_at: Optional[datetime] = None,
        duration: Optional[int] = None,
        synced_at: Optional[datetime] = None,
    ) -> str:
        """
        Create a new execution result.

        Args:
            id: Execution ID (e.g., "exec_20250120_123456").
            batch_id: Associated batch ID.
            sequence_name: Name of the executed sequence.
            sequence_version: Version of the sequence.
            status: Execution status (running, completed, failed, stopped).
            started_at: Execution start timestamp.
            parameters: Execution parameters as dict.
            overall_pass: Overall pass/fail result.
            completed_at: Execution completion timestamp.
            duration: Execution duration in seconds.
            synced_at: Backend sync timestamp.

        Returns:
            Created execution ID.
        """
        parameters_json = json.dumps(parameters) if parameters else None

        await self._db.execute(
            """
            INSERT INTO execution_results (
                id, batch_id, sequence_name, sequence_version, status,
                overall_pass, parameters_json, started_at, completed_at,
                duration, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id,
                batch_id,
                sequence_name,
                sequence_version,
                status,
                overall_pass,
                parameters_json,
                started_at.isoformat() if started_at else None,
                completed_at.isoformat() if completed_at else None,
                duration,
                synced_at.isoformat() if synced_at else None,
            ),
        )

        logger.debug(f"Created execution result: {id}")
        return id

    async def get_execution(self, id: str) -> Optional[dict[str, Any]]:
        """
        Get execution result by ID.

        Args:
            id: Execution ID.

        Returns:
            Execution result as dict or None if not found.
        """
        row = await self._db.fetch_one(
            "SELECT * FROM execution_results WHERE id = ?",
            (id,),
        )

        if row:
            # Parse JSON fields
            if row.get("parameters_json"):
                row["parameters"] = json.loads(row["parameters_json"])
            else:
                row["parameters"] = {}
            del row["parameters_json"]

        return row

    async def get_execution_with_steps(self, id: str) -> Optional[dict[str, Any]]:
        """
        Get execution result with all step results.

        Args:
            id: Execution ID.

        Returns:
            Execution result with steps list or None if not found.
        """
        execution = await self.get_execution(id)
        if not execution:
            return None

        steps = await self.get_step_results(id)
        execution["steps"] = steps

        return execution

    async def get_executions_by_batch(
        self,
        batch_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Get execution results for a batch.

        Args:
            batch_id: Batch ID.
            limit: Maximum number of results.
            offset: Result offset for pagination.

        Returns:
            List of execution results.
        """
        rows = await self._db.fetch_all(
            """
            SELECT * FROM execution_results
            WHERE batch_id = ?
            ORDER BY started_at DESC
            LIMIT ? OFFSET ?
            """,
            (batch_id, limit, offset),
        )

        for row in rows:
            if row.get("parameters_json"):
                row["parameters"] = json.loads(row["parameters_json"])
            else:
                row["parameters"] = {}
            del row["parameters_json"]

        return rows

    async def get_unsynced_executions(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get execution results that haven't been synced to backend.

        Args:
            limit: Maximum number of results.

        Returns:
            List of unsynced execution results.
        """
        rows = await self._db.fetch_all(
            """
            SELECT * FROM execution_results
            WHERE synced_at IS NULL
            AND status IN ('completed', 'failed', 'stopped')
            ORDER BY started_at ASC
            LIMIT ?
            """,
            (limit,),
        )

        for row in rows:
            if row.get("parameters_json"):
                row["parameters"] = json.loads(row["parameters_json"])
            else:
                row["parameters"] = {}
            del row["parameters_json"]

        return rows

    async def update_execution_status(
        self,
        id: str,
        status: str,
        overall_pass: Optional[bool] = None,
        completed_at: Optional[datetime] = None,
        duration: Optional[int] = None,
    ) -> bool:
        """
        Update execution status.

        Args:
            id: Execution ID.
            status: New status.
            overall_pass: Overall pass/fail result.
            completed_at: Completion timestamp.
            duration: Duration in seconds.

        Returns:
            True if updated, False otherwise.
        """
        result = await self._db.execute(
            """
            UPDATE execution_results
            SET status = ?, overall_pass = ?, completed_at = ?, duration = ?
            WHERE id = ?
            """,
            (
                status,
                overall_pass,
                completed_at.isoformat() if completed_at else None,
                duration,
                id,
            ),
        )

        return result > 0

    async def mark_execution_synced(
        self,
        id: str,
        synced_at: Optional[datetime] = None,
    ) -> bool:
        """
        Mark execution as synced to backend.

        Args:
            id: Execution ID.
            synced_at: Sync timestamp (defaults to now).

        Returns:
            True if updated, False otherwise.
        """
        if synced_at is None:
            synced_at = datetime.now()

        result = await self._db.execute(
            "UPDATE execution_results SET synced_at = ? WHERE id = ?",
            (synced_at.isoformat(), id),
        )

        return result > 0

    async def delete_execution(self, id: str) -> bool:
        """
        Delete execution result and its step results.

        Args:
            id: Execution ID.

        Returns:
            True if deleted, False otherwise.
        """
        # Step results are deleted via CASCADE
        result = await self._db.execute(
            "DELETE FROM execution_results WHERE id = ?",
            (id,),
        )

        return result > 0

    async def count_executions(
        self,
        batch_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """
        Count execution results.

        Args:
            batch_id: Filter by batch ID.
            status: Filter by status.

        Returns:
            Count of matching execution results.
        """
        query = "SELECT COUNT(*) FROM execution_results WHERE 1=1"
        params: list[Any] = []

        if batch_id:
            query += " AND batch_id = ?"
            params.append(batch_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        result = await self._db.fetch_value(query, params)
        return result or 0

    # ==================== Step Result CRUD ====================

    async def create_step_result(
        self,
        execution_id: str,
        step_name: str,
        step_order: int,
        status: str,
        pass_result: Optional[bool] = None,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration: Optional[float] = None,
    ) -> int:
        """
        Create a new step result.

        Args:
            execution_id: Parent execution ID.
            step_name: Step name.
            step_order: Step order (1-based).
            status: Step status (pending, running, completed, failed, skipped).
            pass_result: Pass/fail result.
            result: Step result data as dict.
            error: Error message if failed.
            started_at: Step start timestamp.
            completed_at: Step completion timestamp.
            duration: Step duration in seconds.

        Returns:
            Created step result ID.
        """
        result_json = json.dumps(result) if result else None

        row_id = await self._db.execute(
            """
            INSERT INTO step_results (
                execution_id, step_name, step_order, status, pass,
                result_json, error, started_at, completed_at, duration
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                step_name,
                step_order,
                status,
                pass_result,
                result_json,
                error,
                started_at.isoformat() if started_at else None,
                completed_at.isoformat() if completed_at else None,
                duration,
            ),
        )

        logger.debug(f"Created step result: {step_name} for execution {execution_id}")
        return row_id

    async def get_step_results(self, execution_id: str) -> list[dict[str, Any]]:
        """
        Get all step results for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            List of step results ordered by step_order.
        """
        rows = await self._db.fetch_all(
            """
            SELECT * FROM step_results
            WHERE execution_id = ?
            ORDER BY step_order ASC
            """,
            (execution_id,),
        )

        for row in rows:
            if row.get("result_json"):
                row["result"] = json.loads(row["result_json"])
            else:
                row["result"] = {}
            del row["result_json"]
            # Rename 'pass' to 'pass_result' for Python compatibility
            row["pass_result"] = row.pop("pass", None)

        return rows

    async def update_step_result(
        self,
        execution_id: str,
        step_name: str,
        status: str,
        pass_result: Optional[bool] = None,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration: Optional[float] = None,
    ) -> bool:
        """
        Update step result.

        Args:
            execution_id: Execution ID.
            step_name: Step name.
            status: New status.
            pass_result: Pass/fail result.
            result: Step result data.
            error: Error message.
            started_at: Start timestamp.
            completed_at: Completion timestamp.
            duration: Duration in seconds.

        Returns:
            True if updated, False otherwise.
        """
        result_json = json.dumps(result) if result else None

        affected = await self._db.execute(
            """
            UPDATE step_results
            SET status = ?, pass = ?, result_json = ?, error = ?,
                started_at = ?, completed_at = ?, duration = ?
            WHERE execution_id = ? AND step_name = ?
            """,
            (
                status,
                pass_result,
                result_json,
                error,
                started_at.isoformat() if started_at else None,
                completed_at.isoformat() if completed_at else None,
                duration,
                execution_id,
                step_name,
            ),
        )

        return affected > 0

    async def delete_step_results(self, execution_id: str) -> int:
        """
        Delete all step results for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Number of deleted rows.
        """
        return await self._db.execute(
            "DELETE FROM step_results WHERE execution_id = ?",
            (execution_id,),
        )
