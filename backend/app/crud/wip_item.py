"""
CRUD operations for the WIP Item entity.

This module implements Create, Read, Update, Delete operations for WIP
(Work-In-Progress) item management in the F2X NeuroHub Manufacturing Execution
System. Provides standard CRUD functions plus specialized operations for batch
generation, process tracking, and serial conversion.

Functions:
    get: Get a single WIP by ID
    get_multi: Get multiple WIPs with pagination
    get_by_wip_id: Get WIP by unique WIP ID
    get_by_lot: Get all WIPs for a LOT
    get_by_status: Get WIPs by status
    create_batch: Create multiple WIP IDs in batch (BR-001, BR-002)
    update_status: Update WIP status with validation
    scan: Process barcode scan
    start_process: Start a process on WIP (BR-003)
    complete_process: Complete a process on WIP (BR-004)
    convert_to_serial: Convert WIP to serial number (BR-005)
    get_statistics: Get WIP statistics by LOT or process
"""

from datetime import datetime
from typing import List, Optional, Dict, Literal
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import Session, selectinload, joinedload, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.lot import Lot, LotStatus
from app.models.wip_item import WIPItem, WIPStatus
from app.models.wip_process_history import WIPProcessHistory, ProcessResult
from app.models.process import Process, ProcessType
from app.models.serial import Serial, SerialStatus
from app.utils.wip_number import generate_batch_wip_ids
from app.services import wip_service


def _build_optimized_query(
    query: Query,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> Query:
    """
    Build an optimized query with appropriate eager loading strategy.

    Query strategies to avoid N+1 problems:
    - minimal: No eager loading (use when relationships aren't needed)
    - standard: Load common relationships (lot, current_process, serial)
    - full: Load all relationships including process_history

    Strategy explanation:
    - selectinload: Best for one-to-many relationships with potentially many items.
      Uses a separate SELECT IN query, avoiding cartesian products.
    - joinedload: Best for many-to-one relationships (single row).
      Uses LEFT OUTER JOIN in the same query.

    Args:
        query: Base SQLAlchemy query
        eager_loading: Level of eager loading to apply

    Returns:
        Query with optimized eager loading
    """
    if eager_loading == "minimal":
        return query
    elif eager_loading == "standard":
        # Use joinedload for single relationships
        return query.options(
            joinedload(WIPItem.lot),
            joinedload(WIPItem.current_process),
            joinedload(WIPItem.serial)
        )
    elif eager_loading == "full":
        # Load nested relationships including process history
        return query.options(
            joinedload(WIPItem.lot).joinedload(Lot.product_model),
            joinedload(WIPItem.current_process),
            joinedload(WIPItem.serial),
            selectinload(WIPItem.process_history).joinedload(WIPProcessHistory.process)
        )
    return query


def get(db: Session, wip_id: int, eager_loading: Literal["minimal", "standard", "full"] = "standard") -> Optional[WIPItem]:
    """
    Get a single WIP by ID.

    Retrieves a WIP record with optimized eager loading to avoid N+1 queries.

    Query strategy:
    - Standard loading: 1-3 queries total (1 for WIP + joins for relationships)
    - Without optimization: 1 + N queries where N is number of accessed relationships

    Args:
        db: Database session
        wip_id: WIP primary key ID
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        WIPItem instance if found, None otherwise
    """
    query = db.query(WIPItem).filter(WIPItem.id == wip_id)
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[WIPItem]:
    """
    Get multiple WIPs with pagination.

    Retrieves WIP records with optimized eager loading to avoid N+1 queries.

    Query strategy:
    - Standard loading: 2-4 queries total regardless of result count
    - Without optimization: 1 + (N * M) queries where N is result count and M is relationships

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of WIPItem instances
    """
    query = db.query(WIPItem).order_by(desc(WIPItem.created_at), desc(WIPItem.id))
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def get_by_wip_id(db: Session, wip_id: str, eager_loading: Literal["minimal", "standard", "full"] = "standard") -> Optional[WIPItem]:
    """
    Get WIP by unique WIP ID.

    Retrieves a WIP by its unique string identifier with optimized eager loading.

    Args:
        db: Database session
        wip_id: Unique WIP identifier (e.g., "WIP-KR01PSA2511-001")
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        WIPItem instance if found, None otherwise
    """
    query = db.query(WIPItem).filter(WIPItem.wip_id == wip_id)
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_by_lot(
    db: Session,
    lot_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[WIPItem]:
    """
    Get all WIPs for a LOT.

    Retrieves WIP items belonging to a specific LOT with optimized eager loading.

    Args:
        db: Database session
        lot_id: LOT identifier to filter by
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of WIPItem instances for the specified LOT
    """
    query = db.query(WIPItem).filter(WIPItem.lot_id == lot_id).order_by(WIPItem.sequence_in_lot)
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def get_by_status(
    db: Session,
    status: str,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[WIPItem]:
    """
    Get WIPs by status.

    Retrieves WIP items filtered by status with optimized eager loading.

    Args:
        db: Database session
        status: WIP status to filter by (CREATED, IN_PROGRESS, etc.)
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of WIPItem instances with the specified status
    """
    query = db.query(WIPItem).filter(WIPItem.status == status).order_by(desc(WIPItem.created_at))
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def create_batch(
    db: Session,
    lot_id: int,
    quantity: int,
) -> List[WIPItem]:
    """
    Create multiple WIP IDs in batch (BR-001, BR-002).

    Business Rules:
        BR-001: LOT must be in CREATED or IN_PROGRESS status
        BR-002: WIP generation transitions LOT to IN_PROGRESS

    Args:
        db: Database session
        lot_id: LOT identifier
        quantity: Number of WIP IDs to generate (1-100)

    Returns:
        List of created WIP items

    Raises:
        ValueError: If validation fails
        IntegrityError: If database constraint violated
    """
    # Get LOT
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise ValueError(f"LOT with id {lot_id} not found")

    # BR-001: Validate LOT can generate WIP IDs
    wip_service.validate_lot_for_wip_generation(db, lot, quantity)

    # Find next sequence number
    last_wip = (
        db.query(WIPItem)
        .filter(WIPItem.lot_id == lot_id)
        .order_by(desc(WIPItem.sequence_in_lot))
        .first()
    )
    start_sequence = (last_wip.sequence_in_lot + 1) if last_wip else 1

    # Generate WIP IDs
    wip_ids = generate_batch_wip_ids(lot.lot_number, quantity, start_sequence=start_sequence)

    # Create WIP items
    wip_items = []
    try:
        for seq, wip_id in enumerate(wip_ids, start=start_sequence):
            wip_item = WIPItem(
                wip_id=wip_id,
                lot_id=lot_id,
                sequence_in_lot=seq,
                status=WIPStatus.CREATED.value,
            )
            db.add(wip_item)
            wip_items.append(wip_item)

        # BR-002: Transition LOT to IN_PROGRESS
        lot.status = LotStatus.IN_PROGRESS.value

        db.commit()

        # Refresh all items to get IDs
        for item in wip_items:
            db.refresh(item)

    except IntegrityError as e:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise

    return wip_items


def update_status(
    db: Session,
    wip_id: int,
    new_status: WIPStatus,
) -> Optional[WIPItem]:
    """Update WIP status with validation."""
    wip_item = get(db, wip_id)
    if not wip_item:
        return None

    try:
        wip_item.status = new_status.value

        # Set timestamps based on status
        if new_status == WIPStatus.COMPLETED:
            wip_item.completed_at = datetime.utcnow()
        elif new_status == WIPStatus.CONVERTED:
            wip_item.converted_at = datetime.utcnow()

        db.commit()
        db.refresh(wip_item)

    except SQLAlchemyError as e:
        db.rollback()
        raise

    return wip_item


def scan(
    db: Session,
    wip_id_str: str,
    process_id: Optional[int] = None,
) -> Optional[WIPItem]:
    """
    Process barcode scan.

    Args:
        db: Database session
        wip_id_str: Scanned WIP ID string
        process_id: Optional process ID for validation

    Returns:
        WIP item if found and valid, None otherwise
    """
    # Use minimal loading for initial scan, relationships loaded only if needed
    wip_item = get_by_wip_id(db, wip_id_str, eager_loading="minimal")
    if not wip_item:
        return None

    # If process_id provided, validate WIP can start this process
    if process_id:
        process = db.query(Process).filter(Process.id == process_id).first()
        if process:
            can_start, error_msg = wip_service.can_start_process(
                db, wip_item, process.process_number
            )
            if not can_start:
                raise ValueError(error_msg)

    return wip_item


def start_process(
    db: Session,
    wip_id: int,
    process_id: int,
    operator_id: int,
    equipment_id: Optional[int] = None,
    started_at: Optional[datetime] = None,
) -> WIPProcessHistory:
    """
    Start a process on WIP (BR-003).

    Business Rule BR-003: Process can only start if previous process is PASS
    (except process 1).

    Args:
        db: Database session
        wip_id: WIP item identifier
        process_id: Process identifier
        operator_id: Operator identifier
        equipment_id: Equipment identifier (optional)
        started_at: Process start timestamp (defaults to now)

    Returns:
        Created WIP process history record

    Raises:
        ValueError: If validation fails
    """
    # Get WIP item
    wip_item = get(db, wip_id)
    if not wip_item:
        raise ValueError(f"WIP with id {wip_id} not found")

    # Get process
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise ValueError(f"Process with id {process_id} not found")

    # BR-003: Validate process can start
    wip_service.validate_process_start(db, wip_item, process_id, process.process_number)

    # Create process history record (in-progress, no result yet)
    # Note: This is a "start" record - will be updated when completed
    if started_at is None:
        started_at = datetime.utcnow()

    try:
        # Update WIP status to IN_PROGRESS
        if wip_item.status == WIPStatus.CREATED.value:
            wip_item.status = WIPStatus.IN_PROGRESS.value

        wip_item.current_process_id = process_id

        db.commit()
        db.refresh(wip_item)

    except SQLAlchemyError as e:
        db.rollback()
        raise

    return wip_item


def complete_process(
    db: Session,
    wip_id: int,
    process_id: int,
    operator_id: int,
    result: str,
    measurements: Optional[dict] = None,
    defects: Optional[list] = None,
    notes: Optional[str] = None,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    equipment_id: Optional[int] = None,
) -> WIPProcessHistory:
    """
    Complete a process on WIP (BR-004).

    Business Rule BR-004: Same process cannot have duplicate PASS results.

    Args:
        db: Database session
        wip_id: WIP item identifier
        process_id: Process identifier
        operator_id: Operator identifier
        result: Process result (PASS or FAIL)
        measurements: Measurement data (optional)
        defects: Defect data (optional, required if FAIL)
        notes: Additional notes (optional)
        started_at: Process start timestamp (optional, defaults to now)
        completed_at: Process completion timestamp (optional, defaults to now)
        equipment_id: Equipment identifier (optional)

    Returns:
        Created WIP process history record

    Raises:
        ValueError: If validation fails
    """
    # Get WIP item
    wip_item = get(db, wip_id)
    if not wip_item:
        raise ValueError(f"WIP with id {wip_id} not found")

    # Get process
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise ValueError(f"Process with id {process_id} not found")

    # BR-004: Validate no duplicate PASS
    wip_service.validate_process_completion(db, wip_item, process_id, result)

    # Set timestamps
    if started_at is None:
        started_at = datetime.utcnow()
    if completed_at is None:
        completed_at = datetime.utcnow()

    # Calculate duration
    duration_seconds = int((completed_at - started_at).total_seconds())

    try:
        # Create process history record
        history = WIPProcessHistory(
            wip_item_id=wip_id,
            process_id=process_id,
            operator_id=operator_id,
            equipment_id=equipment_id,
            result=result,
            measurements=measurements or {},
            defects=defects or [],
            notes=notes,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
        )
        db.add(history)

        # Update WIP status based on result
        if result == ProcessResult.PASS.value:
            # Get count of active MANUFACTURING processes dynamically
            active_manufacturing_count = db.query(Process).filter(
                Process.process_type == ProcessType.MANUFACTURING.value,
                Process.is_active == True
            ).count()

            # Check if all MANUFACTURING processes are completed
            completed_processes = wip_service.get_completed_processes(db, wip_item)
            completed_processes.append(process.process_number)  # Add current

            if len(set(completed_processes)) >= active_manufacturing_count:
                wip_item.status = WIPStatus.COMPLETED.value
                wip_item.completed_at = datetime.utcnow()
                wip_item.current_process_id = None
            else:
                wip_item.status = WIPStatus.IN_PROGRESS.value
                wip_item.current_process_id = None

        elif result == ProcessResult.FAIL.value:
            wip_item.status = WIPStatus.FAILED.value
            wip_item.current_process_id = None

        elif result == ProcessResult.REWORK.value:
            # REWORK: Keep IN_PROGRESS status for rework attempt
            wip_item.status = WIPStatus.IN_PROGRESS.value
            wip_item.current_process_id = None

        db.commit()
        db.refresh(history)
        db.refresh(wip_item)

    except IntegrityError as e:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise

    return history


def convert_to_serial(
    db: Session,
    wip_id: int,
    operator_id: int,
    notes: Optional[str] = None,
) -> Serial:
    """
    Convert WIP to serial number (BR-005, process 7).

    Business Rule BR-005: All processes 1-6 must have PASS results.

    Args:
        db: Database session
        wip_id: WIP item identifier
        operator_id: Operator performing conversion
        notes: Additional notes (optional)

    Returns:
        Created Serial instance

    Raises:
        ValueError: If validation fails
    """
    # Get WIP item
    wip_item = get(db, wip_id)
    if not wip_item:
        raise ValueError(f"WIP with id {wip_id} not found")

    # BR-005: Validate all processes 1-6 are PASS
    wip_service.validate_serial_conversion(db, wip_item)

    # Get LOT
    lot = db.query(Lot).filter(Lot.id == wip_item.lot_id).first()
    if not lot:
        raise ValueError(f"LOT with id {wip_item.lot_id} not found")

    try:
        # Create serial number (reuse sequence from WIP)
        from app.utils.serial_number import generate_serial_number

        serial_number = generate_serial_number(
            lot.lot_number,
            wip_item.sequence_in_lot
        )

        # Create Serial record
        serial = Serial(
            serial_number=serial_number,
            lot_id=wip_item.lot_id,
            sequence_in_lot=wip_item.sequence_in_lot,
            status=SerialStatus.CREATED.value,
            rework_count=0,
        )
        db.add(serial)
        db.flush()  # Get serial ID

        # Update WIP
        wip_item.status = WIPStatus.CONVERTED.value
        wip_item.serial_id = serial.id
        wip_item.converted_at = datetime.utcnow()

        db.commit()
        db.refresh(serial)
        db.refresh(wip_item)

    except IntegrityError as e:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise

    return serial


def get_statistics(
    db: Session,
    lot_id: Optional[int] = None,
    process_id: Optional[int] = None,
) -> Dict:
    """
    Get WIP statistics by LOT or process.

    Args:
        db: Database session
        lot_id: Optional LOT identifier for filtering
        process_id: Optional process identifier for filtering

    Returns:
        Dictionary with statistics
    """
    query = db.query(WIPItem)

    if lot_id:
        query = query.filter(WIPItem.lot_id == lot_id)

    if process_id:
        query = query.filter(WIPItem.current_process_id == process_id)

    wip_items = query.all()

    total = len(wip_items)
    created = sum(1 for w in wip_items if w.status == WIPStatus.CREATED.value)
    in_progress = sum(1 for w in wip_items if w.status == WIPStatus.IN_PROGRESS.value)
    completed = sum(1 for w in wip_items if w.status == WIPStatus.COMPLETED.value)
    failed = sum(1 for w in wip_items if w.status == WIPStatus.FAILED.value)
    converted = sum(1 for w in wip_items if w.status == WIPStatus.CONVERTED.value)

    return {
        "total": total,
        "created": created,
        "in_progress": in_progress,
        "completed": completed,
        "failed": failed,
        "converted": converted,
        "by_lot": {},
        "by_process": {},
    }
