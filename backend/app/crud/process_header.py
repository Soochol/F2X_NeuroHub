"""
CRUD operations for the ProcessHeader entity.

This module implements Create, Read, Update, Delete operations for process headers
(execution sessions) in the F2X NeuroHub Manufacturing Execution System.

ProcessHeader tracks execution sessions at the station/batch level, providing:
- Station/batch-level process tracking
- Parameter and hardware configuration snapshots
- Aggregated statistics (pass/fail counts)

Functions:
    get: Get a single header by ID
    get_multi: Get multiple headers with pagination and filters
    get_open: Get open header for station+batch+process
    create: Create a new header
    open_or_get: Open a new header or return existing OPEN header
    close: Close an open header
    cancel: Cancel an open header
    update: Update header (parameters/hardware_config only)
    delete: Delete a header (only CANCELLED headers)
    get_by_station: Get all headers for a station
    get_by_batch: Get all headers for a batch
    get_stats: Get statistics for headers
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.process_header import ProcessHeader, HeaderStatus
from app.models.process import Process
from app.schemas.process_header import (
    ProcessHeaderCreate,
    ProcessHeaderUpdate,
    ProcessHeaderOpen,
    ProcessHeaderFilter,
)


def get(db: Session, header_id: int) -> Optional[ProcessHeader]:
    """
    Get a single process header by ID.

    Args:
        db: SQLAlchemy database session
        header_id: Primary key ID of the header

    Returns:
        ProcessHeader instance if found, None otherwise
    """
    return (
        db.query(ProcessHeader)
        .options(joinedload(ProcessHeader.process))
        .filter(ProcessHeader.id == header_id)
        .first()
    )


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[ProcessHeaderFilter] = None,
) -> Tuple[List[ProcessHeader], int]:
    """
    Get multiple process headers with pagination and optional filters.

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        filters: Optional filter criteria

    Returns:
        Tuple of (list of ProcessHeader instances, total count)
    """
    query = db.query(ProcessHeader).options(joinedload(ProcessHeader.process))

    # Apply filters
    if filters:
        if filters.station_id:
            query = query.filter(ProcessHeader.station_id == filters.station_id)
        if filters.batch_id:
            query = query.filter(ProcessHeader.batch_id == filters.batch_id)
        if filters.process_id:
            query = query.filter(ProcessHeader.process_id == filters.process_id)
        if filters.status:
            query = query.filter(ProcessHeader.status == filters.status.value)
        if filters.opened_after:
            query = query.filter(ProcessHeader.opened_at >= filters.opened_after)
        if filters.opened_before:
            query = query.filter(ProcessHeader.opened_at <= filters.opened_before)
        if filters.closed_after:
            query = query.filter(ProcessHeader.closed_at >= filters.closed_after)
        if filters.closed_before:
            query = query.filter(ProcessHeader.closed_at <= filters.closed_before)

    # Get total count before pagination
    total = query.count()

    # Apply ordering and pagination
    results = (
        query
        .order_by(desc(ProcessHeader.opened_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return results, total


def get_open(
    db: Session,
    station_id: str,
    batch_id: str,
    process_id: int,
) -> Optional[ProcessHeader]:
    """
    Get the currently open header for a station+batch+process combination.

    Only one header can be OPEN for a given station+batch+process at a time
    (enforced by unique partial index).

    Args:
        db: SQLAlchemy database session
        station_id: Station identifier
        batch_id: Batch identifier
        process_id: Process identifier

    Returns:
        ProcessHeader instance if found, None otherwise
    """
    return (
        db.query(ProcessHeader)
        .options(joinedload(ProcessHeader.process))
        .filter(
            and_(
                ProcessHeader.station_id == station_id,
                ProcessHeader.batch_id == batch_id,
                ProcessHeader.process_id == process_id,
                ProcessHeader.status == HeaderStatus.OPEN.value,
            )
        )
        .first()
    )


def create(db: Session, header_in: ProcessHeaderCreate) -> ProcessHeader:
    """
    Create a new process header.

    Args:
        db: SQLAlchemy database session
        header_in: ProcessHeaderCreate schema with validated data

    Returns:
        Created ProcessHeader instance

    Raises:
        IntegrityError: If creation violates constraints
    """
    db_header = ProcessHeader(
        station_id=header_in.station_id,
        batch_id=header_in.batch_id,
        process_id=header_in.process_id,
        sequence_package=header_in.sequence_package,
        sequence_version=header_in.sequence_version,
        parameters=header_in.parameters or {},
        hardware_config=header_in.hardware_config or {},
        status=HeaderStatus.OPEN.value,
        opened_at=datetime.now(timezone.utc),
    )

    try:
        db.add(db_header)
        db.commit()
        db.refresh(db_header)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_header


def open_or_get(db: Session, header_in: ProcessHeaderOpen) -> Tuple[ProcessHeader, bool]:
    """
    Open a new header or return the existing OPEN header.

    This is the primary method for opening execution sessions. It ensures
    only one OPEN header exists per station+batch+process combination.

    Args:
        db: SQLAlchemy database session
        header_in: ProcessHeaderOpen schema with data

    Returns:
        Tuple of (ProcessHeader instance, was_created: bool)
        - was_created=True: New header was created
        - was_created=False: Existing OPEN header was returned
    """
    # Check for existing OPEN header
    existing = get_open(
        db,
        station_id=header_in.station_id,
        batch_id=header_in.batch_id,
        process_id=header_in.process_id,
    )

    if existing:
        return existing, False

    # Create new header
    db_header = ProcessHeader(
        station_id=header_in.station_id,
        batch_id=header_in.batch_id,
        process_id=header_in.process_id,
        sequence_package=header_in.sequence_package,
        sequence_version=header_in.sequence_version,
        parameters=header_in.parameters or {},
        hardware_config=header_in.hardware_config or {},
        status=HeaderStatus.OPEN.value,
        opened_at=datetime.now(timezone.utc),
    )

    try:
        db.add(db_header)
        db.commit()
        db.refresh(db_header)
    except IntegrityError:
        db.rollback()
        # Race condition: another header was created, try to get it
        existing = get_open(
            db,
            station_id=header_in.station_id,
            batch_id=header_in.batch_id,
            process_id=header_in.process_id,
        )
        if existing:
            return existing, False
        raise

    return db_header, True


def close(db: Session, header_id: int) -> Optional[ProcessHeader]:
    """
    Close an open header.

    Only OPEN headers can be closed. The status will be set to CLOSED
    and closed_at will be set to current timestamp.

    Args:
        db: SQLAlchemy database session
        header_id: ID of the header to close

    Returns:
        Updated ProcessHeader instance if successful, None if not found or not OPEN

    Raises:
        ValueError: If header is not in OPEN status
    """
    db_header = get(db, header_id)

    if not db_header:
        return None

    if db_header.status != HeaderStatus.OPEN.value:
        raise ValueError(
            f"Cannot close header {header_id}: status is {db_header.status}, "
            f"expected OPEN"
        )

    db_header.status = HeaderStatus.CLOSED.value
    db_header.closed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(db_header)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_header


def cancel(db: Session, header_id: int, reason: Optional[str] = None) -> Optional[ProcessHeader]:
    """
    Cancel an open header.

    Only OPEN headers can be cancelled. The status will be set to CANCELLED
    and closed_at will be set to current timestamp.

    Args:
        db: SQLAlchemy database session
        header_id: ID of the header to cancel
        reason: Optional cancellation reason (not stored, for logging)

    Returns:
        Updated ProcessHeader instance if successful, None if not found or not OPEN

    Raises:
        ValueError: If header is not in OPEN status
    """
    db_header = get(db, header_id)

    if not db_header:
        return None

    if db_header.status != HeaderStatus.OPEN.value:
        raise ValueError(
            f"Cannot cancel header {header_id}: status is {db_header.status}, "
            f"expected OPEN"
        )

    db_header.status = HeaderStatus.CANCELLED.value
    db_header.closed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(db_header)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_header


def update(
    db: Session,
    header_id: int,
    header_in: ProcessHeaderUpdate,
) -> Optional[ProcessHeader]:
    """
    Update a process header.

    Only parameters and hardware_config can be updated.
    Status changes should use close/cancel functions.

    Args:
        db: SQLAlchemy database session
        header_id: ID of the header to update
        header_in: ProcessHeaderUpdate schema with update data

    Returns:
        Updated ProcessHeader instance if successful, None if not found
    """
    db_header = get(db, header_id)

    if not db_header:
        return None

    # Update only provided fields
    update_data = header_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            setattr(db_header, field, value)

    try:
        db.commit()
        db.refresh(db_header)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_header


def delete(db: Session, header_id: int) -> bool:
    """
    Delete a process header.

    Only CANCELLED headers with no associated process data can be deleted.

    Args:
        db: SQLAlchemy database session
        header_id: ID of the header to delete

    Returns:
        True if deleted, False if not found

    Raises:
        ValueError: If header is not CANCELLED or has associated data
    """
    db_header = get(db, header_id)

    if not db_header:
        return False

    if db_header.status != HeaderStatus.CANCELLED.value:
        raise ValueError(
            f"Cannot delete header {header_id}: status is {db_header.status}, "
            f"only CANCELLED headers can be deleted"
        )

    if db_header.total_count > 0:
        raise ValueError(
            f"Cannot delete header {header_id}: has {db_header.total_count} "
            f"associated process data records"
        )

    try:
        db.delete(db_header)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_by_station(
    db: Session,
    station_id: str,
    *,
    skip: int = 0,
    limit: int = 100,
    status: Optional[HeaderStatus] = None,
) -> List[ProcessHeader]:
    """
    Get all headers for a specific station.

    Args:
        db: SQLAlchemy database session
        station_id: Station identifier
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional filter by status

    Returns:
        List of ProcessHeader instances
    """
    query = (
        db.query(ProcessHeader)
        .options(joinedload(ProcessHeader.process))
        .filter(ProcessHeader.station_id == station_id)
    )

    if status:
        query = query.filter(ProcessHeader.status == status.value)

    return (
        query
        .order_by(desc(ProcessHeader.opened_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_batch(
    db: Session,
    batch_id: str,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[ProcessHeader]:
    """
    Get all headers for a specific batch.

    Args:
        db: SQLAlchemy database session
        batch_id: Batch identifier
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of ProcessHeader instances
    """
    return (
        db.query(ProcessHeader)
        .options(joinedload(ProcessHeader.process))
        .filter(ProcessHeader.batch_id == batch_id)
        .order_by(desc(ProcessHeader.opened_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_stats(
    db: Session,
    *,
    station_id: Optional[str] = None,
    process_id: Optional[int] = None,
    opened_after: Optional[datetime] = None,
    opened_before: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Get aggregated statistics for headers.

    Args:
        db: SQLAlchemy database session
        station_id: Optional filter by station
        process_id: Optional filter by process
        opened_after: Optional filter by opened_at
        opened_before: Optional filter by opened_at

    Returns:
        Dictionary with statistics:
        - total_headers: Total count of headers
        - open_headers: Count of OPEN headers
        - closed_headers: Count of CLOSED headers
        - cancelled_headers: Count of CANCELLED headers
        - total_items_processed: Sum of total_count
        - total_pass: Sum of pass_count
        - total_fail: Sum of fail_count
        - overall_pass_rate: Pass rate percentage
        - by_station: Stats grouped by station_id
        - by_process: Stats grouped by process_id
    """
    query = db.query(ProcessHeader)

    # Apply filters
    if station_id:
        query = query.filter(ProcessHeader.station_id == station_id)
    if process_id:
        query = query.filter(ProcessHeader.process_id == process_id)
    if opened_after:
        query = query.filter(ProcessHeader.opened_at >= opened_after)
    if opened_before:
        query = query.filter(ProcessHeader.opened_at <= opened_before)

    # Get all matching headers
    headers = query.all()

    # Calculate stats
    total_headers = len(headers)
    open_headers = sum(1 for h in headers if h.status == HeaderStatus.OPEN.value)
    closed_headers = sum(1 for h in headers if h.status == HeaderStatus.CLOSED.value)
    cancelled_headers = sum(1 for h in headers if h.status == HeaderStatus.CANCELLED.value)
    total_items = sum(h.total_count for h in headers)
    total_pass = sum(h.pass_count for h in headers)
    total_fail = sum(h.fail_count for h in headers)

    overall_pass_rate = (total_pass / total_items * 100) if total_items > 0 else 0.0

    # Group by station
    by_station: Dict[str, Dict[str, Any]] = {}
    for h in headers:
        if h.station_id not in by_station:
            by_station[h.station_id] = {
                "total_headers": 0,
                "total_items": 0,
                "pass_count": 0,
                "fail_count": 0,
            }
        by_station[h.station_id]["total_headers"] += 1
        by_station[h.station_id]["total_items"] += h.total_count
        by_station[h.station_id]["pass_count"] += h.pass_count
        by_station[h.station_id]["fail_count"] += h.fail_count

    # Calculate pass rates for each station
    for station_stats in by_station.values():
        items = station_stats["total_items"]
        station_stats["pass_rate"] = (
            (station_stats["pass_count"] / items * 100) if items > 0 else 0.0
        )

    # Group by process
    by_process: Dict[int, Dict[str, Any]] = {}
    for h in headers:
        if h.process_id not in by_process:
            by_process[h.process_id] = {
                "total_headers": 0,
                "total_items": 0,
                "pass_count": 0,
                "fail_count": 0,
            }
        by_process[h.process_id]["total_headers"] += 1
        by_process[h.process_id]["total_items"] += h.total_count
        by_process[h.process_id]["pass_count"] += h.pass_count
        by_process[h.process_id]["fail_count"] += h.fail_count

    # Calculate pass rates for each process
    for process_stats in by_process.values():
        items = process_stats["total_items"]
        process_stats["pass_rate"] = (
            (process_stats["pass_count"] / items * 100) if items > 0 else 0.0
        )

    return {
        "total_headers": total_headers,
        "open_headers": open_headers,
        "closed_headers": closed_headers,
        "cancelled_headers": cancelled_headers,
        "total_items_processed": total_items,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "overall_pass_rate": round(overall_pass_rate, 2),
        "by_station": by_station,
        "by_process": by_process,
    }


def increment_counts(
    db: Session,
    header_id: int,
    result: str,
) -> Optional[ProcessHeader]:
    """
    Increment the counts for a header based on process result.

    Note: This is typically handled by database triggers, but can be
    called manually if needed.

    Args:
        db: SQLAlchemy database session
        header_id: ID of the header
        result: Process result (PASS, FAIL, REWORK)

    Returns:
        Updated ProcessHeader instance if successful, None if not found
    """
    db_header = get(db, header_id)

    if not db_header:
        return None

    db_header.total_count += 1
    if result.upper() == "PASS":
        db_header.pass_count += 1
    elif result.upper() == "FAIL":
        db_header.fail_count += 1
    # REWORK counts as total but not pass or fail

    try:
        db.commit()
        db.refresh(db_header)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_header
