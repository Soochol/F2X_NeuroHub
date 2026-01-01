"""
Logs API routes for Station Service.

This module provides endpoints for querying execution logs.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from station_service.api.dependencies import get_database
from station_service.api.schemas.responses import ErrorResponse, PaginatedData, PaginatedResponse
from station_service.api.schemas.result import LogEntry
from station_service.storage.database import Database
from station_service.storage.repositories.log_repository import LogRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["Logs"])


class LogLevel(str, Enum):
    """Log level filter options."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@router.get(
    "",
    response_model=PaginatedResponse[LogEntry],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Query logs",
    description="""
    Retrieve a paginated list of log entries.

    Supports filtering by:
    - batch_id: Filter logs for a specific batch
    - level: Filter by log level (debug, info, warning, error)
    - from/to: Filter by time range
    - search: Full-text search in log messages

    Logs are returned in descending order by timestamp (newest first).
    """,
)
async def query_logs(
    database: Database = Depends(get_database),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    execution_id: Optional[str] = Query(None, description="Filter by execution ID"),
    level: Optional[LogLevel] = Query(None, description="Filter by log level"),
    from_time: Optional[datetime] = Query(None, alias="from", description="Filter logs from this time"),
    to_time: Optional[datetime] = Query(None, alias="to", description="Filter logs until this time"),
    search: Optional[str] = Query(None, description="Search term in log messages"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
) -> PaginatedResponse[LogEntry]:
    """
    Query log entries with optional filtering.

    Returns a paginated list of log entries matching the specified filters.
    Useful for debugging, monitoring, and audit purposes.

    Args:
        database: Database instance (injected)
        batch_id: Optional batch ID to filter logs
        execution_id: Optional execution ID to filter logs
        level: Optional log level filter (debug, info, warning, error)
        from_time: Optional start time for time range filter
        to_time: Optional end time for time range filter
        search: Optional search term for full-text search in messages
        limit: Maximum number of log entries to return (default: 100, max: 1000)
        offset: Number of logs to skip for pagination

    Returns:
        PaginatedResponse[LogEntry]: Paginated list of log entries

    Raises:
        HTTPException: 500 if there's an error querying logs
    """
    try:
        repo = LogRepository(database)

        # Build query with filters
        query = "SELECT * FROM logs WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM logs WHERE 1=1"
        params: List[Any] = []
        count_params: List[Any] = []

        if batch_id:
            query += " AND batch_id = ?"
            count_query += " AND batch_id = ?"
            params.append(batch_id)
            count_params.append(batch_id)

        if execution_id:
            query += " AND execution_id = ?"
            count_query += " AND execution_id = ?"
            params.append(execution_id)
            count_params.append(execution_id)

        if level:
            query += " AND level = ?"
            count_query += " AND level = ?"
            params.append(level.value)
            count_params.append(level.value)

        if from_time:
            query += " AND timestamp >= ?"
            count_query += " AND timestamp >= ?"
            params.append(from_time.isoformat())
            count_params.append(from_time.isoformat())

        if to_time:
            query += " AND timestamp <= ?"
            count_query += " AND timestamp <= ?"
            params.append(to_time.isoformat())
            count_params.append(to_time.isoformat())

        if search:
            query += " AND message LIKE ?"
            count_query += " AND message LIKE ?"
            search_pattern = f"%{search}%"
            params.append(search_pattern)
            count_params.append(search_pattern)

        # Add ordering and pagination
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Execute queries
        rows = await database.fetch_all(query, params)
        total = await database.fetch_value(count_query, count_params) or 0

        # Convert to response models
        items = []
        for row in rows:
            # Parse timestamp
            timestamp = row.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except (ValueError, TypeError):
                    timestamp = datetime.now()
            elif timestamp is None:
                timestamp = datetime.now()

            items.append(
                LogEntry(
                    id=row["id"],
                    batch_id=row["batch_id"],
                    execution_id=row.get("execution_id"),
                    level=row["level"],
                    message=row["message"],
                    timestamp=timestamp,
                )
            )

        return PaginatedResponse(
            success=True,
            data=PaginatedData(
                total=total,
                items=items,
            ),
        )
    except Exception as e:
        logger.exception("Failed to query logs")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query logs: {str(e)}",
        )
