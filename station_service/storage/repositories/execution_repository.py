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

    # ==================== Report Aggregation Queries ====================

    async def get_batch_statistics(self, batch_id: str) -> Optional[dict[str, Any]]:
        """
        Get aggregated statistics for a batch.

        Args:
            batch_id: Batch ID.

        Returns:
            Dict with total_executions, pass_count, fail_count, avg_duration,
            first_execution, last_execution, sequence_name, sequence_version.
        """
        row = await self._db.fetch_one(
            """
            SELECT
                COUNT(*) as total_executions,
                SUM(CASE WHEN overall_pass = 1 THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN overall_pass = 0 OR overall_pass IS NULL THEN 1 ELSE 0 END) as fail_count,
                AVG(duration) as avg_duration,
                MIN(started_at) as first_execution,
                MAX(started_at) as last_execution,
                sequence_name,
                sequence_version
            FROM execution_results
            WHERE batch_id = ? AND status IN ('completed', 'failed')
            GROUP BY batch_id
            """,
            (batch_id,),
        )
        return dict(row) if row else None

    async def get_step_statistics_by_batch(self, batch_id: str) -> list[dict[str, Any]]:
        """
        Get per-step statistics for a batch.

        Args:
            batch_id: Batch ID.

        Returns:
            List of dicts with step_name, step_order, total_runs, pass_count,
            fail_count, avg_duration, min_duration, max_duration.
        """
        rows = await self._db.fetch_all(
            """
            SELECT
                sr.step_name,
                sr.step_order,
                COUNT(*) as total_runs,
                SUM(CASE WHEN sr.pass = 1 THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN sr.pass = 0 OR sr.pass IS NULL THEN 1 ELSE 0 END) as fail_count,
                AVG(sr.duration) as avg_duration,
                MIN(sr.duration) as min_duration,
                MAX(sr.duration) as max_duration
            FROM step_results sr
            JOIN execution_results er ON sr.execution_id = er.id
            WHERE er.batch_id = ? AND sr.status IN ('completed', 'failed')
            GROUP BY sr.step_name, sr.step_order
            ORDER BY sr.step_order
            """,
            (batch_id,),
        )
        return [dict(row) for row in rows]

    async def get_period_statistics(
        self,
        period_type: str,
        from_date: datetime,
        to_date: datetime,
        batch_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get statistics grouped by time period.

        Args:
            period_type: Period type (daily, weekly, monthly).
            from_date: Start date.
            to_date: End date.
            batch_id: Optional batch filter.

        Returns:
            List of dicts with period_label, total, pass_count, fail_count, avg_duration.
        """
        # SQLite strftime format for grouping
        period_format = {
            "daily": "%Y-%m-%d",
            "weekly": "%Y-W%W",
            "monthly": "%Y-%m",
        }
        fmt = period_format.get(period_type, "%Y-%m-%d")

        where_clause = "WHERE started_at >= ? AND started_at <= ? AND status IN ('completed', 'failed')"
        params: list[Any] = [from_date.isoformat(), to_date.isoformat()]

        if batch_id:
            where_clause += " AND batch_id = ?"
            params.append(batch_id)

        query = f"""
            SELECT
                strftime('{fmt}', started_at) as period_label,
                MIN(started_at) as period_start,
                MAX(started_at) as period_end,
                COUNT(*) as total,
                SUM(CASE WHEN overall_pass = 1 THEN 1 ELSE 0 END) as pass_count,
                SUM(CASE WHEN overall_pass = 0 OR overall_pass IS NULL THEN 1 ELSE 0 END) as fail_count,
                AVG(duration) as avg_duration
            FROM execution_results
            {where_clause}
            GROUP BY period_label
            ORDER BY period_label
        """

        rows = await self._db.fetch_all(query, params)
        return [dict(row) for row in rows]

    async def get_step_analysis(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        batch_id: Optional[str] = None,
        step_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get step-level analysis sorted by failure rate.

        Args:
            from_date: Optional start date filter.
            to_date: Optional end date filter.
            batch_id: Optional batch filter.
            step_name: Optional step name filter.

        Returns:
            List of dicts with step_name, total_runs, fail_count, fail_rate,
            avg_duration, min_duration, max_duration.
        """
        where_clauses = ["sr.status IN ('completed', 'failed')"]
        params: list[Any] = []

        if from_date:
            where_clauses.append("er.started_at >= ?")
            params.append(from_date.isoformat())
        if to_date:
            where_clauses.append("er.started_at <= ?")
            params.append(to_date.isoformat())
        if batch_id:
            where_clauses.append("er.batch_id = ?")
            params.append(batch_id)
        if step_name:
            where_clauses.append("sr.step_name = ?")
            params.append(step_name)

        where_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT
                sr.step_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN sr.pass = 0 OR sr.pass IS NULL THEN 1 ELSE 0 END) as fail_count,
                AVG(sr.duration) as avg_duration,
                MIN(sr.duration) as min_duration,
                MAX(sr.duration) as max_duration
            FROM step_results sr
            JOIN execution_results er ON sr.execution_id = er.id
            WHERE {where_clause}
            GROUP BY sr.step_name
            ORDER BY (CAST(fail_count AS REAL) / NULLIF(total_runs, 0)) DESC
        """

        rows = await self._db.fetch_all(query, params)
        return [dict(row) for row in rows]

    async def get_step_durations(
        self,
        step_name: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        batch_id: Optional[str] = None,
    ) -> list[float]:
        """
        Get all durations for a step (for percentile calculation).

        Args:
            step_name: Step name.
            from_date: Optional start date filter.
            to_date: Optional end date filter.
            batch_id: Optional batch filter.

        Returns:
            List of duration values.
        """
        where_clauses = [
            "sr.step_name = ?",
            "sr.status IN ('completed', 'failed')",
            "sr.duration IS NOT NULL",
        ]
        params: list[Any] = [step_name]

        if from_date:
            where_clauses.append("er.started_at >= ?")
            params.append(from_date.isoformat())
        if to_date:
            where_clauses.append("er.started_at <= ?")
            params.append(to_date.isoformat())
        if batch_id:
            where_clauses.append("er.batch_id = ?")
            params.append(batch_id)

        where_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT sr.duration
            FROM step_results sr
            JOIN execution_results er ON sr.execution_id = er.id
            WHERE {where_clause}
            ORDER BY sr.duration
        """

        rows = await self._db.fetch_all(query, params)
        return [row["duration"] for row in rows if row["duration"] is not None]

    async def get_failure_reasons_by_step(
        self,
        step_name: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        batch_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get aggregated failure reasons for a step.

        Args:
            step_name: Step name.
            from_date: Optional start date filter.
            to_date: Optional end date filter.
            batch_id: Optional batch filter.
            limit: Maximum number of reasons to return.

        Returns:
            List of dicts with error, occurrence_count.
        """
        where_clauses = [
            "sr.step_name = ?",
            "sr.pass = 0",
            "sr.error IS NOT NULL",
            "sr.error != ''",
        ]
        params: list[Any] = [step_name]

        if from_date:
            where_clauses.append("er.started_at >= ?")
            params.append(from_date.isoformat())
        if to_date:
            where_clauses.append("er.started_at <= ?")
            params.append(to_date.isoformat())
        if batch_id:
            where_clauses.append("er.batch_id = ?")
            params.append(batch_id)

        where_clause = " AND ".join(where_clauses)
        params.append(limit)

        query = f"""
            SELECT
                sr.error,
                COUNT(*) as occurrence_count
            FROM step_results sr
            JOIN execution_results er ON sr.execution_id = er.id
            WHERE {where_clause}
            GROUP BY sr.error
            ORDER BY occurrence_count DESC
            LIMIT ?
        """

        rows = await self._db.fetch_all(query, params)
        return [dict(row) for row in rows]

    async def get_multiple_executions_with_steps(
        self,
        result_ids: list[str],
    ) -> list[dict[str, Any]]:
        """
        Get multiple execution results with their steps for bulk export.

        Args:
            result_ids: List of execution IDs.

        Returns:
            List of execution results with steps.
        """
        if not result_ids:
            return []

        placeholders = ",".join("?" * len(result_ids))
        rows = await self._db.fetch_all(
            f"""
            SELECT * FROM execution_results
            WHERE id IN ({placeholders})
            ORDER BY started_at DESC
            """,
            result_ids,
        )

        results = []
        for row in rows:
            execution = dict(row)
            if execution.get("parameters_json"):
                execution["parameters"] = json.loads(execution["parameters_json"])
            else:
                execution["parameters"] = {}
            del execution["parameters_json"]

            # Get steps for this execution
            steps = await self.get_step_results(execution["id"])
            execution["steps"] = steps
            results.append(execution)

        return results
