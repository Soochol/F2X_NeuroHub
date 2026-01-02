"""FastAPI router for ProcessHeader entity endpoints.

This module provides RESTful API endpoints for managing process headers
(execution sessions) in the F2X NeuroHub MES system.

ProcessHeader tracks execution sessions at the station/batch level, enabling:
- Station/batch-level process tracking
- Parameter and hardware configuration snapshots
- Aggregated statistics (pass/fail counts)

Provides:
    - GET /: List all headers with pagination and filters
    - GET /stats: Get aggregated statistics
    - GET /{id}: Get header by ID
    - GET /open: Get open header for station+batch+process
    - POST /: Create new header
    - POST /open: Open or get existing header
    - POST /{id}/close: Close an open header
    - POST /{id}/cancel: Cancel an open header
    - PUT /{id}: Update header
    - DELETE /{id}: Delete cancelled header
    - GET /station/{station_id}: Get headers by station
    - GET /batch/{batch_id}: Get headers by batch

All endpoints include:
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
    - Error handling with HTTPException
"""

from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Query, status, Path, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.deps import StationAuth, get_auth_context
from app.models import User
from app.crud import process_header as crud
from app.schemas.process_header import (
    HeaderStatus,
    ProcessHeaderCreate,
    ProcessHeaderUpdate,
    ProcessHeaderOpen,
    ProcessHeaderClose,
    ProcessHeaderCancel,
    ProcessHeaderInDB,
    ProcessHeaderSummary,
    ProcessHeaderListResponse,
    ProcessHeaderStatsResponse,
    ProcessHeaderFilter,
)


router = APIRouter(
    prefix="/process-headers",
    tags=["Process Headers"],
    responses={
        404: {"description": "Header not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)


@router.get(
    "/",
    response_model=ProcessHeaderListResponse,
    summary="List all process headers",
    description="Retrieve a paginated list of process headers with optional filters. Supports both JWT and API Key authentication.",
)
def list_headers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    process_id: Optional[int] = Query(None, ge=1, description="Filter by process ID"),
    status: Optional[HeaderStatus] = Query(None, description="Filter by status"),
    opened_after: Optional[datetime] = Query(None, description="Filter by opened_at >= this time"),
    opened_before: Optional[datetime] = Query(None, description="Filter by opened_at <= this time"),
    db: Session = Depends(deps.get_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> ProcessHeaderListResponse:
    """List all process headers with pagination and filters.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        station_id: Optional filter by station ID
        batch_id: Optional filter by batch ID
        process_id: Optional filter by process ID
        status: Optional filter by header status
        opened_after: Optional filter by opened_at
        opened_before: Optional filter by opened_at
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        ProcessHeaderListResponse with items, total, skip, limit
    """
    filters = ProcessHeaderFilter(
        station_id=station_id,
        batch_id=batch_id,
        process_id=process_id,
        status=status,
        opened_after=opened_after,
        opened_before=opened_before,
    )

    items, total = crud.get_multi(db, skip=skip, limit=limit, filters=filters)

    # Convert to summary schemas
    summaries = []
    for item in items:
        summary = ProcessHeaderSummary(
            id=item.id,
            station_id=item.station_id,
            batch_id=item.batch_id,
            process_id=item.process_id,
            status=item.status,
            total_count=item.total_count,
            pass_count=item.pass_count,
            fail_count=item.fail_count,
            opened_at=item.opened_at,
            closed_at=item.closed_at,
            process_name=item.process.process_name_ko if item.process else None,
            process_code=item.process.process_code if item.process else None,
        )
        summaries.append(summary)

    return ProcessHeaderListResponse(
        items=summaries,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/stats",
    response_model=ProcessHeaderStatsResponse,
    summary="Get header statistics",
    description="Get aggregated statistics for process headers",
)
def get_stats(
    station_id: Optional[str] = Query(None, description="Filter by station ID"),
    process_id: Optional[int] = Query(None, ge=1, description="Filter by process ID"),
    opened_after: Optional[datetime] = Query(None, description="Filter by opened_at"),
    opened_before: Optional[datetime] = Query(None, description="Filter by opened_at"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessHeaderStatsResponse:
    """Get aggregated statistics for process headers.

    Args:
        station_id: Optional filter by station ID
        process_id: Optional filter by process ID
        opened_after: Optional filter by opened_at
        opened_before: Optional filter by opened_at
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        ProcessHeaderStatsResponse with statistics
    """
    stats = crud.get_stats(
        db,
        station_id=station_id,
        process_id=process_id,
        opened_after=opened_after,
        opened_before=opened_before,
    )

    return ProcessHeaderStatsResponse(
        total_headers=stats["total_headers"],
        open_headers=stats["open_headers"],
        closed_headers=stats["closed_headers"],
        cancelled_headers=stats["cancelled_headers"],
        total_items_processed=stats["total_items_processed"],
        total_pass=stats["total_pass"],
        total_fail=stats["total_fail"],
        overall_pass_rate=stats["overall_pass_rate"],
        by_station=stats["by_station"],
        by_process=stats["by_process"],
    )


@router.get(
    "/open",
    response_model=Optional[ProcessHeaderInDB],
    summary="Get open header",
    description="Get the currently open header for a station+batch+process combination. Supports both JWT and API Key authentication.",
)
def get_open_header(
    station_id: str = Query(..., description="Station ID"),
    batch_id: str = Query(..., description="Batch ID"),
    process_id: int = Query(..., ge=1, description="Process ID"),
    db: Session = Depends(deps.get_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> Optional[ProcessHeaderInDB]:
    """Get the open header for a station+batch+process.

    Only one header can be OPEN for a given combination.

    Args:
        station_id: Station identifier
        batch_id: Batch identifier
        process_id: Process identifier
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        ProcessHeaderInDB if found, None otherwise
    """
    header = crud.get_open(db, station_id=station_id, batch_id=batch_id, process_id=process_id)
    return header


@router.get(
    "/station/{station_id}",
    response_model=List[ProcessHeaderSummary],
    summary="Get headers by station",
    description="Get all headers for a specific station",
)
def get_by_station(
    station_id: str = Path(..., description="Station ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status: Optional[HeaderStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProcessHeaderSummary]:
    """Get all headers for a specific station.

    Args:
        station_id: Station identifier
        skip: Number of records to skip
        limit: Maximum records to return
        status: Optional filter by status
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        List of ProcessHeaderSummary
    """
    headers = crud.get_by_station(db, station_id=station_id, skip=skip, limit=limit, status=status)

    return [
        ProcessHeaderSummary(
            id=h.id,
            station_id=h.station_id,
            batch_id=h.batch_id,
            process_id=h.process_id,
            status=h.status,
            total_count=h.total_count,
            pass_count=h.pass_count,
            fail_count=h.fail_count,
            opened_at=h.opened_at,
            closed_at=h.closed_at,
            process_name=h.process.process_name_ko if h.process else None,
            process_code=h.process.process_code if h.process else None,
        )
        for h in headers
    ]


@router.get(
    "/batch/{batch_id}",
    response_model=List[ProcessHeaderSummary],
    summary="Get headers by batch",
    description="Get all headers for a specific batch",
)
def get_by_batch(
    batch_id: str = Path(..., description="Batch ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProcessHeaderSummary]:
    """Get all headers for a specific batch.

    Args:
        batch_id: Batch identifier
        skip: Number of records to skip
        limit: Maximum records to return
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        List of ProcessHeaderSummary
    """
    headers = crud.get_by_batch(db, batch_id=batch_id, skip=skip, limit=limit)

    return [
        ProcessHeaderSummary(
            id=h.id,
            station_id=h.station_id,
            batch_id=h.batch_id,
            process_id=h.process_id,
            status=h.status,
            total_count=h.total_count,
            pass_count=h.pass_count,
            fail_count=h.fail_count,
            opened_at=h.opened_at,
            closed_at=h.closed_at,
            process_name=h.process.process_name_ko if h.process else None,
            process_code=h.process.process_code if h.process else None,
        )
        for h in headers
    ]


@router.get(
    "/{header_id}",
    response_model=ProcessHeaderInDB,
    summary="Get header by ID",
    description="Retrieve a single process header by its ID. Supports both JWT and API Key authentication.",
)
def get_header(
    header_id: int = Path(..., ge=1, description="Header ID"),
    db: Session = Depends(deps.get_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> ProcessHeaderInDB:
    """Get a single process header by ID.

    Args:
        header_id: Primary key ID of the header
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        ProcessHeaderInDB

    Raises:
        HTTPException 404: If header not found
    """
    header = crud.get(db, header_id=header_id)
    if not header:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process header with ID {header_id} not found",
        )
    return header


@router.post(
    "/",
    response_model=ProcessHeaderInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new header",
    description="Create a new process header",
)
def create_header(
    header_in: ProcessHeaderCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessHeaderInDB:
    """Create a new process header.

    Args:
        header_in: ProcessHeaderCreate schema with data
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        Created ProcessHeaderInDB

    Raises:
        HTTPException 409: If constraint violation
    """
    try:
        header = crud.create(db, header_in=header_in)
        return header
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Failed to create header: {str(e)}",
        )


@router.post(
    "/open",
    response_model=ProcessHeaderInDB,
    summary="Open or get header",
    description="Open a new header or return existing OPEN header for the same combination. Supports both JWT and API Key authentication.",
)
def open_or_get_header(
    header_in: ProcessHeaderOpen,
    db: Session = Depends(deps.get_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> ProcessHeaderInDB:
    """Open a new header or return existing OPEN header.

    This is the primary method for opening execution sessions.
    If a header already exists for the same station+batch+process
    combination and is OPEN, it will be returned.

    Args:
        header_in: ProcessHeaderOpen schema with data
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        ProcessHeaderInDB (new or existing)
    """
    header, was_created = crud.open_or_get(db, header_in=header_in)
    return header


@router.post(
    "/{header_id}/close",
    response_model=ProcessHeaderInDB,
    summary="Close header",
    description="Close an open process header. Supports both JWT and API Key authentication.",
)
def close_header(
    header_id: int = Path(..., ge=1, description="Header ID"),
    close_data: Optional[ProcessHeaderClose] = None,
    db: Session = Depends(deps.get_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> ProcessHeaderInDB:
    """Close an open process header.

    Only OPEN headers can be closed. The status will be set to CLOSED
    and closed_at will be set to current timestamp.

    Args:
        header_id: ID of the header to close
        close_data: Optional close data with notes
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        Updated ProcessHeaderInDB

    Raises:
        HTTPException 404: If header not found
        HTTPException 400: If header is not OPEN
    """
    try:
        header = crud.close(db, header_id=header_id)
        if not header:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Process header with ID {header_id} not found",
            )
        return header
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{header_id}/cancel",
    response_model=ProcessHeaderInDB,
    summary="Cancel header",
    description="Cancel an open process header",
)
def cancel_header(
    header_id: int = Path(..., ge=1, description="Header ID"),
    cancel_data: Optional[ProcessHeaderCancel] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessHeaderInDB:
    """Cancel an open process header.

    Only OPEN headers can be cancelled. The status will be set to CANCELLED
    and closed_at will be set to current timestamp.

    Args:
        header_id: ID of the header to cancel
        cancel_data: Optional cancel data with reason
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        Updated ProcessHeaderInDB

    Raises:
        HTTPException 404: If header not found
        HTTPException 400: If header is not OPEN
    """
    reason = cancel_data.reason if cancel_data else None
    try:
        header = crud.cancel(db, header_id=header_id, reason=reason)
        if not header:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Process header with ID {header_id} not found",
            )
        return header
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{header_id}",
    response_model=ProcessHeaderInDB,
    summary="Update header",
    description="Update a process header (parameters/hardware_config only)",
)
def update_header(
    header_id: int = Path(..., ge=1, description="Header ID"),
    header_in: ProcessHeaderUpdate = ...,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessHeaderInDB:
    """Update a process header.

    Only parameters and hardware_config can be updated.
    Status changes should use close/cancel endpoints.

    Args:
        header_id: ID of the header to update
        header_in: ProcessHeaderUpdate schema with update data
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Returns:
        Updated ProcessHeaderInDB

    Raises:
        HTTPException 404: If header not found
    """
    header = crud.update(db, header_id=header_id, header_in=header_in)
    if not header:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process header with ID {header_id} not found",
        )
    return header


@router.delete(
    "/{header_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete header",
    description="Delete a cancelled process header with no associated data",
)
def delete_header(
    header_id: int = Path(..., ge=1, description="Header ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> None:
    """Delete a process header.

    Only CANCELLED headers with no associated process data can be deleted.

    Args:
        header_id: ID of the header to delete
        db: SQLAlchemy database session
        current_user: Current authenticated user

    Raises:
        HTTPException 404: If header not found
        HTTPException 400: If header cannot be deleted
    """
    try:
        deleted = crud.delete(db, header_id=header_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Process header with ID {header_id} not found",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
