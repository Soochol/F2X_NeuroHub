"""
FastAPI router for ErrorLog entity endpoints.

This module implements RESTful API endpoints for error log monitoring and analytics including:
    - Error log retrieval with pagination and filtering
    - Error statistics and trends
    - Trace ID search for debugging

Endpoints:
    GET    /error-logs/              - List all error logs with pagination and filters
    GET    /error-logs/{id}          - Get error log by ID
    GET    /error-logs/trace/{trace_id} - Get error log by trace ID (debugging)
    GET    /error-logs/stats         - Get error statistics for dashboard

Security:
    - All endpoints require admin role
    - Error logs are read-only (no create/update/delete via API)
    - Error logs are created automatically by ErrorLoggingMiddleware
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models import User
from app.schemas.error_log import (
    ErrorLogResponse,
    ErrorLogListResponse,
    ErrorLogStats,
)
from app.core.exceptions import (
    ResourceNotFoundException,
    DatabaseException,
)


# Create APIRouter
router = APIRouter(
    prefix="/error-logs",
    tags=["Error Logs"],
)


@router.get(
    "/",
    response_model=ErrorLogListResponse,
    summary="List all error logs",
    description="Retrieve a paginated list of error logs with optional filtering. Admin only.",
)
def list_error_logs(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),  # TODO: Use admin check
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        50,
        ge=1,
        le=1000,
        description="Maximum number of records to return (max: 1000)",
    ),
    error_code: Optional[str] = Query(
        None,
        max_length=20,
        description="Filter by error code (e.g., RES_002, VAL_001)",
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter by timestamp (from)",
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter by timestamp (to)",
    ),
    user_id: Optional[int] = Query(
        None,
        description="Filter by user ID",
    ),
    path: Optional[str] = Query(
        None,
        max_length=500,
        description="Filter by API endpoint path",
    ),
    method: Optional[str] = Query(
        None,
        max_length=10,
        description="Filter by HTTP method (GET, POST, PUT, DELETE, PATCH)",
    ),
    min_status_code: Optional[int] = Query(
        None,
        ge=400,
        lt=600,
        description="Minimum HTTP status code (4xx or 5xx)",
    ),
    max_status_code: Optional[int] = Query(
        None,
        ge=400,
        lt=600,
        description="Maximum HTTP status code (4xx or 5xx)",
    ),
):
    """
    Retrieve a paginated list of error logs.

    Query parameters allow filtering by error code, date range, user, path, method,
    and status code. Results are ordered by timestamp (newest first).

    Returns:
        ErrorLogListResponse with error logs list and pagination info

    Security:
        - Requires admin role (TODO: implement role check)
    """
    try:
        # Get filtered error logs
        error_logs = crud.error_log.get_multi(
            db,
            skip=skip,
            limit=limit,
            error_code=error_code,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            path=path,
            method=method,
            min_status_code=min_status_code,
            max_status_code=max_status_code,
        )

        # Get total count (for pagination)
        total = crud.error_log.count_total(
            db,
            since=start_date,
        )

        # Convert to response format with username
        error_log_responses = []
        for error_log in error_logs:
            error_log_dict = {
                **error_log.to_dict(),
                "username": error_log.user.username if error_log.user else None,
            }
            error_log_responses.append(ErrorLogResponse(**error_log_dict))

        return ErrorLogListResponse(
            items=error_log_responses,
            total=total,
            skip=skip,
            limit=limit,
        )

    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database error: {str(e)}")


@router.get(
    "/stats",
    response_model=ErrorLogStats,
    summary="Get error statistics",
    description="Retrieve error statistics for dashboard visualizations. Admin only.",
)
def get_error_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),  # TODO: Use admin check
    hours: int = Query(
        24,
        ge=1,
        le=168,
        description="Number of hours to analyze (max: 168 = 1 week)",
    ),
):
    """
    Get error statistics for dashboard.

    Includes:
        - Total error count
        - Error distribution by error code
        - Hourly error trend
        - Top error-prone API endpoints

    Args:
        hours: Number of hours to look back (default: 24, max: 168)

    Returns:
        ErrorLogStats with comprehensive error statistics

    Security:
        - Requires admin role (TODO: implement role check)
    """
    try:
        stats = crud.error_log.get_stats(db, hours=hours)
        return ErrorLogStats(**stats)

    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database error: {str(e)}")


@router.get(
    "/{error_log_id}",
    response_model=ErrorLogResponse,
    summary="Get error log by ID",
    description="Retrieve a single error log by its ID. Admin only.",
)
def get_error_log(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),  # TODO: Use admin check
    error_log_id: int = Path(..., gt=0, description="Error log ID"),
):
    """
    Retrieve a single error log by ID.

    Args:
        error_log_id: Error log ID to retrieve

    Returns:
        ErrorLogResponse with error log details and username

    Raises:
        404: Error log not found

    Security:
        - Requires admin role (TODO: implement role check)
    """
    try:
        error_log = crud.error_log.get(db, error_log_id=error_log_id)
        if not error_log:
            raise ResourceNotFoundException(
                resource_type="ErrorLog",
                resource_id=str(error_log_id)
            )

        # Convert to response format with username
        error_log_dict = {
            **error_log.to_dict(),
            "username": error_log.user.username if error_log.user else None,
        }

        return ErrorLogResponse(**error_log_dict)

    except (ResourceNotFoundException, DatabaseException):
        raise
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database error: {str(e)}")


@router.get(
    "/trace/{trace_id}",
    response_model=ErrorLogResponse,
    summary="Get error log by trace ID",
    description="Retrieve an error log by trace ID for debugging. Admin only.",
)
def get_error_by_trace_id(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),  # TODO: Use admin check
    trace_id: UUID = Path(..., description="Trace ID from StandardErrorResponse"),
):
    """
    Retrieve an error log by trace ID.

    Used for debugging by correlating frontend error with backend error log.
    The trace_id is included in StandardErrorResponse and displayed to users.

    Args:
        trace_id: UUID trace ID from error response

    Returns:
        ErrorLogResponse with error log details

    Raises:
        404: Error log not found for given trace ID

    Security:
        - Requires admin role (TODO: implement role check)

    Example:
        GET /api/v1/error-logs/trace/a1b2c3d4-e5f6-7890-abcd-ef1234567890
    """
    try:
        error_log = crud.error_log.get_by_trace_id(db, trace_id=trace_id)
        if not error_log:
            raise ResourceNotFoundException(
                resource_type="ErrorLog",
                resource_id=f"trace_id={trace_id}"
            )

        # Convert to response format with username
        error_log_dict = {
            **error_log.to_dict(),
            "username": error_log.user.username if error_log.user else None,
        }

        return ErrorLogResponse(**error_log_dict)

    except (ResourceNotFoundException, DatabaseException):
        raise
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database error: {str(e)}")
