"""
CRUD operations for the ProcessData entity.

This module provides comprehensive Create, Read, Update, Delete operations for process execution
records in the F2X NeuroHub Manufacturing Execution System. Supports filtering by serial, LOT,
process type, result status, operator, and date range with advanced query capabilities.

Functions:
    - get: Retrieve a single ProcessData record by ID
    - get_multi: Retrieve multiple ProcessData records with pagination
    - create: Create a new ProcessData record
    - update: Update an existing ProcessData record
    - delete: Delete a ProcessData record
    - get_by_serial: Get all process data for a specific serial
    - get_by_lot: Get all process data for a specific LOT
    - get_by_process: Filter process data by process type
    - get_by_result: Filter process data by result status (PASS/FAIL/REWORK)
    - get_failures: Get failed process records for defect analysis
    - get_by_operator: Filter process data by operator
    - get_by_date_range: Filter process data by date range

Key Features:
    - Type-safe with comprehensive type hints
    - Pydantic schema validation for input
    - Efficient database queries with selective joins
    - Pagination support for all list operations
    - Result sorting and ordering for analytics
"""

from datetime import datetime
from typing import List, Optional, Literal

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload, selectinload, Query

from app.models.process_data import ProcessData, ProcessResult, DataLevel
from app.models.process import Process
from app.models.serial import Serial
from app.models.lot import Lot
from app.models.user import User
from app.schemas.process_data import ProcessDataCreate, ProcessDataUpdate


def _build_optimized_query(
    query: Query,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> Query:
    """
    Build an optimized query with appropriate eager loading strategy.

    Query strategies to avoid N+1 problems:
    - minimal: No eager loading (use when relationships aren't needed)
    - standard: Load common relationships (lot, serial, process, operator)
    - full: Load all relationships including nested ones and equipment

    Strategy explanation:
    - joinedload: Best for many-to-one relationships (single row).
      Uses LEFT OUTER JOIN in the same query. Used for: lot, serial,
      process, operator as they are single parent records.
    - selectinload: Best for one-to-many relationships.
      Uses separate SELECT IN query to avoid cartesian products.

    Args:
        query: Base SQLAlchemy query
        eager_loading: Level of eager loading to apply

    Returns:
        Query with optimized eager loading
    """
    if eager_loading == "minimal":
        return query
    elif eager_loading == "standard":
        # Load all commonly accessed relationships using joinedload
        # This converts N+1 queries into a single JOIN query
        return query.options(
            joinedload(ProcessData.lot),
            joinedload(ProcessData.serial),
            joinedload(ProcessData.process),
            joinedload(ProcessData.operator),
            joinedload(ProcessData.wip_item)
        )
    elif eager_loading == "full":
        # Load relationships and their nested relationships
        return query.options(
            joinedload(ProcessData.lot).joinedload("product_model"),
            joinedload(ProcessData.lot).joinedload("production_line"),
            joinedload(ProcessData.serial).joinedload("lot"),
            joinedload(ProcessData.process),
            joinedload(ProcessData.operator),
            joinedload(ProcessData.wip_item),
            joinedload(ProcessData.equipment)
        )
    return query


def get(
    db: Session,
    *,
    process_data_id: int,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> Optional[ProcessData]:
    """
    Retrieve a single ProcessData record by ID.

    Fetches a specific process data record with relationships loaded,
    enabling access to related lot, serial, process, and operator info.

    Query optimization:
    - Standard loading: 1 query with JOINs for all relationships
    - Without optimization: 1 + 4+ queries when accessing relationships

    Args:
        db: SQLAlchemy Session for database operations
        process_data_id: Primary key identifier of the ProcessData record
        eager_loading: Control eager loading depth

    Returns:
        ProcessData object if found, None otherwise

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> process_data = get(db, process_data_id=1)
        >>> if process_data:
        ...     print(f"Process: {process_data.process.name}")  # No N+1
        ...     print(f"Operator: {process_data.operator.username}")
    """
    query = db.query(ProcessData).filter(
        ProcessData.id == process_data_id
    )
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[ProcessData]:
    """
    Retrieve multiple ProcessData records with pagination.

    Fetches a paginated list of process data records ordered by creation
    time in descending order (newest first). Useful for displaying recent
    process execution history.

    Query optimization:
    - With standard loading for 100 records: 1 query with JOINs
    - Without optimization: 1 + 400+ queries (N+1 for each relationship)

    Args:
        db: SQLAlchemy Session for database operations
        skip: Number of records to skip (default 0, for pagination)
        limit: Maximum number of records to return (default 100)
        eager_loading: Control eager loading depth

    Returns:
        List of ProcessData objects (may be empty if no records found)

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> recent_data = get_multi(db, skip=0, limit=50)
        >>> for pd in recent_data:
        ...     print(f"Serial: {pd.serial.serial_number}")  # No N+1
        ...     print(f"Process: {pd.process.name}")
    """
    query = db.query(ProcessData).order_by(desc(ProcessData.created_at))
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def create(db: Session, *, obj_in: ProcessDataCreate) -> ProcessData:
    """
    Create a new ProcessData record.

    Inserts a new process execution record into the database with validation
    of data_level and serial_id consistency, and timestamp validation.
    The database trigger will automatically calculate duration_seconds.

    Args:
        db: SQLAlchemy Session for database operations
        obj_in: ProcessDataCreate schema with validated input data

    Returns:
        Created ProcessData object with auto-generated ID

    Raises:
        SQLAlchemy exceptions: On constraint violations (FK, unique, check)

    Example:
        >>> from app.database import SessionLocal
        >>> from app.schemas.process_data import ProcessDataCreate
        >>> db = SessionLocal()
        >>> schema = ProcessDataCreate(
        ...     lot_id=1,
        ...     serial_id=1,
        ...     process_id=1,
        ...     operator_id=1,
        ...     data_level="SERIAL",
        ...     result="PASS",
        ...     started_at=datetime.utcnow(),
        ...     completed_at=datetime.utcnow(),
        ... )
        >>> pd = create(db, obj_in=schema)
        >>> db.commit()
        >>> print(f"Created ProcessData ID: {pd.id}")
    """
    db_obj = ProcessData(
        lot_id=obj_in.lot_id,
        serial_id=obj_in.serial_id,
        wip_id=obj_in.wip_id,
        process_id=obj_in.process_id,
        operator_id=obj_in.operator_id,
        data_level=obj_in.data_level.value,
        result=obj_in.result.value,
        measurements=obj_in.measurements,
        defects=obj_in.defects,
        notes=obj_in.notes,
        started_at=obj_in.started_at,
        completed_at=obj_in.completed_at,
    )
    db.add(db_obj)
    db.flush()
    return db_obj


def update(
    db: Session, *, db_obj: ProcessData, obj_in: ProcessDataUpdate
) -> ProcessData:
    """
    Update an existing ProcessData record.

    Performs a partial update of the specified ProcessData record, allowing
    modification of result, measurements, defects, completion status, and notes.
    Only provided fields are updated; others retain their existing values.

    Args:
        db: SQLAlchemy Session for database operations
        db_obj: Existing ProcessData object to update
        obj_in: ProcessDataUpdate schema with fields to update (optional fields)

    Returns:
        Updated ProcessData object

    Example:
        >>> from app.database import SessionLocal
        >>> from app.schemas.process_data import ProcessDataUpdate
        >>> db = SessionLocal()
        >>> pd = get(db, process_data_id=1)
        >>> update_schema = ProcessDataUpdate(
        ...     result="PASS",
        ...     completed_at=datetime.utcnow(),
        ...     measurements={"temperature": 98.6}
        ... )
        >>> updated = update(db, db_obj=pd, obj_in=update_schema)
        >>> db.commit()
    """
    update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            if field == "data_level" and value is not None:
                setattr(db_obj, field, value.value)
            elif field == "result" and value is not None:
                setattr(db_obj, field, value.value)
            else:
                setattr(db_obj, field, value)

    db.add(db_obj)
    db.flush()
    return db_obj


def delete(db: Session, *, process_data_id: int) -> bool:
    """
    Delete a ProcessData record.

    Removes a process data record from the database. Foreign key constraints
    and cascade rules are enforced at the database level. Typically used only
    for correcting data entry errors rather than operational deletions.

    Args:
        db: SQLAlchemy Session for database operations
        process_data_id: Primary key identifier of the ProcessData record to delete

    Returns:
        True if record was deleted, False if record was not found

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> success = delete(db, process_data_id=1)
        >>> if success:
        ...     db.commit()
        ...     print("ProcessData deleted successfully")
    """
    db_obj = db.query(ProcessData).filter(ProcessData.id == process_data_id).first()
    if db_obj:
        db.delete(db_obj)
        db.flush()
        return True
    return False


def get_by_serial(
    db: Session,
    *,
    serial_id: int,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[ProcessData]:
    """
    Get all process data for a specific serial.

    Retrieves the complete manufacturing execution history for a single
    unit (serial), ordered by process sequence number (1→2→3→...→8).
    Useful for tracing the entire quality and process journey of a unit.

    Query optimization: Eager loads relationships to avoid N+1 queries.

    Args:
        db: SQLAlchemy Session for database operations
        serial_id: Primary key of the serial to fetch process data for
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)
        eager_loading: Control eager loading depth

    Returns:
        List of ProcessData objects for the serial, ordered by sequence

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> serial_history = get_by_serial(db, serial_id=42)
        >>> for pd in serial_history:
        ...     process_name = pd.process.name  # No additional query
        ...     print(f"Process {pd.process.process_number}: {pd.result}")
    """
    query = (
        db.query(ProcessData)
        .join(Process)
        .filter(ProcessData.serial_id == serial_id)
        .order_by(Process.process_number)
    )
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def get_by_lot(
    db: Session, *, lot_id: int, skip: int = 0, limit: int = 100
) -> List[ProcessData]:
    """
    Get all process data for a specific LOT.

    Retrieves all process execution records for a production batch (LOT), including
    both LOT-level data (serial_id=NULL) and SERIAL-level data (serial_id=NOT NULL).
    Ordered by creation time descending for chronological analysis.

    Args:
        db: SQLAlchemy Session for database operations
        lot_id: Primary key of the LOT to fetch process data for
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects for the LOT, ordered by creation time

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> lot_data = get_by_lot(db, lot_id=5, limit=200)
        >>> print(f"Total records for LOT: {len(lot_data)}")
    """
    return (
        db.query(ProcessData)
        .filter(ProcessData.lot_id == lot_id)
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_process(
    db: Session, *, process_id: int, skip: int = 0, limit: int = 100
) -> List[ProcessData]:
    """
    Filter process data by process type.

    Retrieves all execution records for a specific manufacturing process across all
    serials and LOTs. Useful for analyzing process-specific quality metrics and
    trends.

    Args:
        db: SQLAlchemy Session for database operations
        process_id: Primary key of the process to filter by
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects for the specified process

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> laser_marking_data = get_by_process(db, process_id=1, limit=500)
        >>> pass_count = sum(1 for pd in laser_marking_data if pd.result == "PASS")
        >>> print(f"Pass rate: {pass_count}/{len(laser_marking_data)}")
    """
    return (
        db.query(ProcessData)
        .filter(ProcessData.process_id == process_id)
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_result(
    db: Session,
    *,
    result: str,
    skip: int = 0,
    limit: int = 100
) -> List[ProcessData]:
    """
    Filter process data by result status.

    Retrieves process execution records filtered by result (PASS, FAIL, REWORK).
    Useful for quality analysis, defect tracking, and process performance metrics.

    Args:
        db: SQLAlchemy Session for database operations
        result: Result status to filter by ("PASS", "FAIL", or "REWORK")
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects with the specified result status

    Raises:
        ValueError: If result is not a valid ProcessResult value

    Example:
        >>> from app.database import SessionLocal
        >>> from app.models.process_data import ProcessResult
        >>> db = SessionLocal()
        >>> failures = get_by_result(db, result=ProcessResult.FAIL.value, limit=200)
        >>> for pd in failures:
        ...     print(f"Process {pd.process_id}: {pd.defects}")
    """
    return (
        db.query(ProcessData)
        .filter(ProcessData.result == result)
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_failures(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[ProcessData]:
    """
    Get failed process records for defect analysis.

    Retrieves all ProcessData records with result=FAIL, ordered by creation time
    descending (most recent failures first). Designed for failure analysis, root
    cause investigation, and quality trend monitoring.

    Args:
        db: SQLAlchemy Session for database operations
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects with result=FAIL

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> recent_failures = get_failures(db, limit=50)
        >>> for pd in recent_failures:
        ...     print(f"Serial {pd.serial_id}: {len(pd.defects or [])} defects")
        ...     for defect in (pd.defects or []):
        ...         print(f"  - {defect.get('code')}: {defect.get('description')}")
    """
    return (
        db.query(ProcessData)
        .filter(ProcessData.result == ProcessResult.FAIL.value)
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_operator(
    db: Session, *, operator_id: int, skip: int = 0, limit: int = 100
) -> List[ProcessData]:
    """
    Filter process data by operator.

    Retrieves all process execution records performed by a specific operator,
    ordered by creation time descending. Useful for operator performance metrics,
    training effectiveness, and quality accountability analysis.

    Args:
        db: SQLAlchemy Session for database operations
        operator_id: Primary key of the operator (user) to filter by
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects performed by the specified operator

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> operator_records = get_by_operator(db, operator_id=10, limit=1000)
        >>> failures = [pd for pd in operator_records if pd.result == "FAIL"]
        >>> failure_rate = len(failures) / len(operator_records) if operator_records else 0
        >>> print(f"Operator failure rate: {failure_rate:.2%}")
    """
    return (
        db.query(ProcessData)
        .filter(ProcessData.operator_id == operator_id)
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_date_range(
    db: Session,
    *,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> List[ProcessData]:
    """
    Filter process data by date range.

    Retrieves process execution records within a specified time window based on
    the started_at timestamp. Useful for time-based analytics, trend analysis,
    and historical data retrieval.

    Args:
        db: SQLAlchemy Session for database operations
        start_date: Start of date range (inclusive) for filtering
        end_date: End of date range (inclusive) for filtering
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects within the date range, ordered by creation time

    Example:
        >>> from app.database import SessionLocal
        >>> from datetime import datetime, timedelta
        >>> db = SessionLocal()
        >>> today = datetime.utcnow().date()
        >>> start = datetime.combine(today, datetime.min.time())
        >>> end = datetime.combine(today, datetime.max.time())
        >>> today_data = get_by_date_range(db, start_date=start, end_date=end)
        >>> print(f"Records created today: {len(today_data)}")
    """
    return (
        db.query(ProcessData)
        .filter(
            and_(
                ProcessData.started_at >= start_date,
                ProcessData.started_at <= end_date
            )
        )
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_serial_and_process(
    db: Session,
    *,
    serial_id: int,
    process_id: int
) -> Optional[ProcessData]:
    """
    Get process data for a specific serial and process combination.

    Retrieves a single process execution record for a specific serial-process pair.
    Useful for tracking a unit through a specific manufacturing step.

    Args:
        db: SQLAlchemy Session for database operations
        serial_id: Primary key of the serial
        process_id: Primary key of the process

    Returns:
        ProcessData object if found, None otherwise

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> record = get_by_serial_and_process(db, serial_id=42, process_id=1)
        >>> if record and record.result == "FAIL":
        ...     print(f"Serial failed at process 1: {record.defects}")
    """
    return (
        db.query(ProcessData)
        .filter(
            and_(
                ProcessData.serial_id == serial_id,
                ProcessData.process_id == process_id
            )
        )
        .first()
    )


def get_by_lot_and_process(
    db: Session,
    *,
    lot_id: int,
    process_id: int
) -> Optional[ProcessData]:
    """
    Get LOT-level process data for a specific LOT and process combination.

    Retrieves a single LOT-level (serial_id=NULL) process record for a specific
    LOT-process pair. Used for batch-level process tracking.

    Args:
        db: SQLAlchemy Session for database operations
        lot_id: Primary key of the LOT
        process_id: Primary key of the process

    Returns:
        ProcessData object with data_level=LOT if found, None otherwise

    Example:
        >>> from app.database import SessionLocal
        >>> from app.models.process_data import DataLevel
        >>> db = SessionLocal()
        >>> record = get_by_lot_and_process(db, lot_id=5, process_id=1)
        >>> if record and record.data_level == DataLevel.LOT.value:
        ...     print(f"LOT-level process 1: {record.measurements}")
    """
    return (
        db.query(ProcessData)
        .filter(
            and_(
                ProcessData.lot_id == lot_id,
                ProcessData.process_id == process_id,
                ProcessData.serial_id.is_(None)
            )
        )
        .first()
    )


def get_by_lot_process_wip(
    db: Session,
    *,
    lot_id: int,
    process_id: int,
    wip_id: int
) -> Optional[ProcessData]:
    """
    Get process data for a specific LOT, process, and WIP item combination.

    Retrieves a single process record for a specific WIP item within a LOT.
    Used for WIP-level process tracking where multiple WIP items exist in one LOT.

    Args:
        db: SQLAlchemy Session for database operations
        lot_id: Primary key of the LOT
        process_id: Primary key of the process
        wip_id: Primary key of the WIP item

    Returns:
        ProcessData object if found, None otherwise
    """
    return (
        db.query(ProcessData)
        .filter(
            and_(
                ProcessData.lot_id == lot_id,
                ProcessData.process_id == process_id,
                ProcessData.wip_id == wip_id
            )
        )
        .first()
    )


def get_failures_by_process(
    db: Session,
    *,
    process_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ProcessData]:
    """
    Get failed process records for a specific process.

    Retrieves failure records for a specific manufacturing process, useful for
    process-specific root cause analysis and quality improvement initiatives.

    Args:
        db: SQLAlchemy Session for database operations
        process_id: Primary key of the process to analyze
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects with result=FAIL for the specified process

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> laser_failures = get_failures_by_process(db, process_id=1, limit=100)
        >>> defect_counts = {}
        >>> for pd in laser_failures:
        ...     for defect in (pd.defects or []):
        ...         code = defect.get('code')
        ...         defect_counts[code] = defect_counts.get(code, 0) + 1
        >>> most_common = max(defect_counts.items(), key=lambda x: x[1])
        >>> print(f"Most common defect: {most_common[0]} ({most_common[1]} occurrences)")
    """
    return (
        db.query(ProcessData)
        .filter(
            and_(
                ProcessData.process_id == process_id,
                ProcessData.result == ProcessResult.FAIL.value
            )
        )
        .order_by(desc(ProcessData.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_incomplete_processes(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[ProcessData]:
    """
    Get in-progress process records (not yet completed).

    Retrieves process execution records where completed_at is NULL, representing
    processes still in progress. Useful for real-time production monitoring.

    Args:
        db: SQLAlchemy Session for database operations
        skip: Number of records to skip for pagination (default 0)
        limit: Maximum number of records to return (default 100)

    Returns:
        List of ProcessData objects with completed_at=NULL

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> in_progress = get_incomplete_processes(db)
        >>> print(f"Active processes: {len(in_progress)}")
        >>> for pd in in_progress:
        ...     elapsed = (datetime.utcnow() - pd.started_at).total_seconds()
        ...     print(f"Serial {pd.serial_id}: {elapsed:.0f} seconds elapsed")
    """
    return (
        db.query(ProcessData)
        .filter(ProcessData.completed_at.is_(None))
        .order_by(ProcessData.started_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_by_result(db: Session, *, result: str) -> int:
    """
    Count process records by result status.

    Returns the total count of process execution records with a specific result.
    More efficient than retrieving all records when only count is needed.

    Args:
        db: SQLAlchemy Session for database operations
        result: Result status to count ("PASS", "FAIL", or "REWORK")

    Returns:
        Count of ProcessData records with the specified result

    Example:
        >>> from app.database import SessionLocal
        >>> from app.models.process_data import ProcessResult
        >>> db = SessionLocal()
        >>> pass_count = count_by_result(db, result=ProcessResult.PASS.value)
        >>> fail_count = count_by_result(db, result=ProcessResult.FAIL.value)
        >>> total = pass_count + fail_count
        >>> rate = (pass_count / total * 100) if total > 0 else 0
        >>> print(f"Overall pass rate: {rate:.1f}%")
    """
    return db.query(ProcessData).filter(
        ProcessData.result == result
    ).count()


def count_by_process(db: Session, *, process_id: int) -> int:
    """
    Count total process records for a specific process.

    Returns the total count of execution records for a manufacturing process.

    Args:
        db: SQLAlchemy Session for database operations
        process_id: Primary key of the process to count

    Returns:
        Count of ProcessData records for the specified process

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> count = count_by_process(db, process_id=1)
        >>> print(f"Process 1 has been executed {count} times")
    """
    return db.query(ProcessData).filter(
        ProcessData.process_id == process_id
    ).count()


def count_by_serial(db: Session, *, serial_id: int) -> int:
    """
    Count process records for a specific serial.

    Returns the total count of process execution records for a unit (serial).
    Helps track progress through the 8-process manufacturing sequence.

    Args:
        db: SQLAlchemy Session for database operations
        serial_id: Primary key of the serial to count

    Returns:
        Count of ProcessData records for the specified serial

    Example:
        >>> from app.database import SessionLocal
        >>> db = SessionLocal()
        >>> count = count_by_serial(db, serial_id=42)
        >>> print(f"Serial 42 has completed {count}/8 processes")
    """
    return db.query(ProcessData).filter(
        ProcessData.serial_id == serial_id
    ).count()
