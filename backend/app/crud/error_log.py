"""
CRUD operations for the ErrorLog entity.

This module implements Create and Read operations for error log management
in the F2X NeuroHub MES system. Provides functions for creating error logs
(via middleware), retrieving error logs with filters, and generating statistics.

Functions:
    get: Get a single error log by ID
    get_by_trace_id: Get an error log by trace_id
    get_multi: Get multiple error logs with pagination and filtering
    create: Create a new error log entry
    count_total: Count total errors in time range
    count_by_error_code: Get error distribution by error code
    count_by_hour: Get hourly error counts for trend analysis
    get_top_paths: Get most error-prone API endpoints
    get_stats: Get comprehensive error statistics
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.error_log import ErrorLog
from app.models.user import User
from app.schemas.error_log import (
    ErrorLogCreate,
    ErrorCodeCount,
    HourlyErrorCount,
    TopErrorPath,
)


def get(db: Session, error_log_id: int) -> Optional[ErrorLog]:
    """
    Get a single error log by ID.

    Retrieves an error log record with related user entity eagerly loaded.

    Args:
        db: SQLAlchemy database session
        error_log_id: Primary key ID of the error log to retrieve

    Returns:
        ErrorLog instance if found, None otherwise

    Example:
        error_log = get(db, error_log_id=123)
        if error_log:
            print(f"Error: {error_log.error_code} - {error_log.message}")
    """
    return (
        db.query(ErrorLog)
        .options(joinedload(ErrorLog.user))
        .filter(ErrorLog.id == error_log_id)
        .first()
    )


def get_by_trace_id(db: Session, trace_id: UUID) -> Optional[ErrorLog]:
    """
    Get an error log by trace_id (for debugging).

    Retrieves an error log record using the unique trace_id that correlates
    frontend and backend errors.

    Args:
        db: SQLAlchemy database session
        trace_id: UUID trace ID from StandardErrorResponse

    Returns:
        ErrorLog instance if found, None otherwise

    Example:
        error_log = get_by_trace_id(db, trace_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    """
    return (
        db.query(ErrorLog)
        .options(joinedload(ErrorLog.user))
        .filter(ErrorLog.trace_id == trace_id)
        .first()
    )


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    error_code: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    min_status_code: Optional[int] = None,
    max_status_code: Optional[int] = None,
) -> List[ErrorLog]:
    """
    Get multiple error logs with pagination and filtering.

    Retrieves a paginated list of error logs with optional filters for error code,
    date range, user, path, method, and status code. Results are ordered by
    timestamp (newest first).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 50)
        error_code: Optional filter by error code (e.g., "RES_002")
        start_date: Optional filter by timestamp (from)
        end_date: Optional filter by timestamp (to)
        user_id: Optional filter by user ID
        path: Optional filter by API path
        method: Optional filter by HTTP method
        min_status_code: Optional minimum status code (e.g., 400)
        max_status_code: Optional maximum status code (e.g., 499)

    Returns:
        List of ErrorLog instances matching the criteria

    Example:
        # Get 404 errors for a specific user
        error_logs = get_multi(
            db,
            error_code="RES_002",
            user_id=5,
            limit=20
        )

        # Get server errors (5xx) in last 24 hours
        from datetime import datetime, timedelta
        error_logs = get_multi(
            db,
            start_date=datetime.utcnow() - timedelta(hours=24),
            min_status_code=500,
            max_status_code=599
        )
    """
    query = db.query(ErrorLog).options(joinedload(ErrorLog.user))

    # Apply filters
    if error_code is not None:
        query = query.filter(ErrorLog.error_code == error_code)

    if start_date is not None:
        query = query.filter(ErrorLog.timestamp >= start_date)

    if end_date is not None:
        query = query.filter(ErrorLog.timestamp <= end_date)

    if user_id is not None:
        query = query.filter(ErrorLog.user_id == user_id)

    if path is not None:
        query = query.filter(ErrorLog.path == path)

    if method is not None:
        query = query.filter(ErrorLog.method == method)

    if min_status_code is not None:
        query = query.filter(ErrorLog.status_code >= min_status_code)

    if max_status_code is not None:
        query = query.filter(ErrorLog.status_code <= max_status_code)

    # Order by timestamp (newest first) with partition pruning
    return (
        query
        .order_by(desc(ErrorLog.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, *, error_log_in: ErrorLogCreate) -> ErrorLog:
    """
    Create a new error log entry.

    Typically called by ErrorLoggingMiddleware to record API errors.

    Args:
        db: SQLAlchemy database session
        error_log_in: ErrorLogCreate schema with error details

    Returns:
        Created ErrorLog instance

    Raises:
        SQLAlchemyError: If database insertion fails

    Example:
        from uuid import uuid4
        error_log_data = ErrorLogCreate(
            trace_id=uuid4(),
            error_code="RES_002",
            message="Lot not found",
            path="/api/v1/lots/999",
            method="GET",
            status_code=404,
            user_id=5
        )
        error_log = create(db, error_log_in=error_log_data)
    """
    db_error_log = ErrorLog(
        trace_id=error_log_in.trace_id,
        error_code=error_log_in.error_code,
        message=error_log_in.message,
        path=error_log_in.path,
        method=error_log_in.method,
        status_code=error_log_in.status_code,
        user_id=error_log_in.user_id,
        details=error_log_in.details,
        timestamp=error_log_in.timestamp,
    )
    db.add(db_error_log)
    db.commit()
    db.refresh(db_error_log)
    return db_error_log


def count_total(db: Session, *, since: Optional[datetime] = None) -> int:
    """
    Count total errors in time range.

    Args:
        db: SQLAlchemy database session
        since: Optional start datetime (default: all time)

    Returns:
        Total count of error logs

    Example:
        # Count errors in last 24 hours
        from datetime import datetime, timedelta
        count = count_total(db, since=datetime.utcnow() - timedelta(hours=24))
    """
    query = db.query(func.count(ErrorLog.id))

    if since is not None:
        query = query.filter(ErrorLog.timestamp >= since)

    return query.scalar() or 0


def count_by_error_code(
    db: Session,
    *,
    since: Optional[datetime] = None,
    limit: int = 20
) -> List[ErrorCodeCount]:
    """
    Get error distribution by error code.

    Returns the count of each error code, ordered by frequency (descending).
    Useful for identifying most common error types.

    Args:
        db: SQLAlchemy database session
        since: Optional start datetime for filtering
        limit: Maximum number of error codes to return (default: 20)

    Returns:
        List of ErrorCodeCount with error_code and count

    Example:
        # Get top 10 error codes in last 7 days
        from datetime import datetime, timedelta
        distribution = count_by_error_code(
            db,
            since=datetime.utcnow() - timedelta(days=7),
            limit=10
        )
        for item in distribution:
            print(f"{item.error_code}: {item.count} errors")
    """
    query = db.query(
        ErrorLog.error_code,
        func.count(ErrorLog.id).label("count")
    ).group_by(ErrorLog.error_code)

    if since is not None:
        query = query.filter(ErrorLog.timestamp >= since)

    results = (
        query
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )

    return [
        ErrorCodeCount(error_code=row.error_code, count=row.count)
        for row in results
    ]


def count_by_hour(
    db: Session,
    *,
    since: Optional[datetime] = None,
    hours: int = 24
) -> List[HourlyErrorCount]:
    """
    Get hourly error counts for trend analysis.

    Returns error counts aggregated by hour, useful for visualizing
    error trends over time in LineChart.

    Args:
        db: SQLAlchemy database session
        since: Optional start datetime (default: {hours} hours ago)
        hours: Number of hours to look back (default: 24)

    Returns:
        List of HourlyErrorCount with hour and count

    Example:
        # Get hourly error counts for last 24 hours
        hourly_counts = count_by_hour(db, hours=24)
        for item in hourly_counts:
            print(f"{item.hour}: {item.count} errors")
    """
    if since is None:
        since = datetime.utcnow() - timedelta(hours=hours)

    # Truncate timestamp to hour
    hour_column = func.date_trunc('hour', ErrorLog.timestamp).label('hour')

    query = db.query(
        hour_column,
        func.count(ErrorLog.id).label("count")
    ).filter(
        ErrorLog.timestamp >= since
    ).group_by(hour_column)

    results = query.order_by(desc(hour_column)).all()

    return [
        HourlyErrorCount(hour=row.hour, count=row.count)
        for row in results
    ]


def get_top_paths(
    db: Session,
    *,
    since: Optional[datetime] = None,
    limit: int = 10
) -> List[TopErrorPath]:
    """
    Get most error-prone API endpoints.

    Returns API paths with the highest error counts, useful for identifying
    problematic endpoints that need attention.

    Args:
        db: SQLAlchemy database session
        since: Optional start datetime for filtering
        limit: Maximum number of paths to return (default: 10)

    Returns:
        List of TopErrorPath with path, method, and count

    Example:
        # Get top 10 error-prone endpoints in last 24 hours
        from datetime import datetime, timedelta
        top_paths = get_top_paths(
            db,
            since=datetime.utcnow() - timedelta(hours=24),
            limit=10
        )
        for item in top_paths:
            print(f"{item.method} {item.path}: {item.count} errors")
    """
    query = db.query(
        ErrorLog.path,
        ErrorLog.method,
        func.count(ErrorLog.id).label("count")
    ).filter(
        ErrorLog.path.isnot(None)
    ).group_by(ErrorLog.path, ErrorLog.method)

    if since is not None:
        query = query.filter(ErrorLog.timestamp >= since)

    results = (
        query
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )

    return [
        TopErrorPath(path=row.path, method=row.method or "UNKNOWN", count=row.count)
        for row in results
    ]


def get_stats(
    db: Session,
    *,
    hours: int = 24
) -> Dict[str, Any]:
    """
    Get comprehensive error statistics.

    Combines multiple statistics queries into a single response for
    the error dashboard. Includes total count, distribution by error code,
    hourly trends, and top error-prone endpoints.

    Args:
        db: SQLAlchemy database session
        hours: Number of hours to look back (default: 24)

    Returns:
        Dictionary with keys: total_errors, by_error_code, by_hour, top_paths

    Example:
        stats = get_stats(db, hours=24)
        print(f"Total errors: {stats['total_errors']}")
        print(f"Error types: {len(stats['by_error_code'])}")
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    return {
        "total_errors": count_total(db, since=since),
        "by_error_code": count_by_error_code(db, since=since, limit=20),
        "by_hour": count_by_hour(db, since=since, hours=hours),
        "top_paths": get_top_paths(db, since=since, limit=10),
    }
