"""
CRUD operations for the Serial entity.

This module implements Create, Read, Update, Delete operations for individual
serial units within production lots in the F2X NeuroHub MES system. Provides
standard CRUD functions plus specialized queries for retrieving serials by
lot, status, serial number, and rework status.

Functions:
    get: Get a single serial by ID
    get_multi: Get multiple serials with pagination and filtering
    create: Create a new serial
    update: Update an existing serial
    delete: Delete a serial
    get_by_number: Get serial by unique serial_number
    get_by_lot: Get all serials in a LOT with pagination
    get_by_status: Get serials filtered by status with pagination
    get_failed: Get FAILED serials available for rework
    increment_rework: Increment rework count and reset status to IN_PROGRESS
    update_status: Update serial status with validation and failure reason
    can_rework: Check if a serial is eligible for rework
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.serial import Serial, SerialStatus
from app.schemas.serial import SerialCreate, SerialUpdate, SerialInDB


def get(db: Session, serial_id: int) -> Optional[Serial]:
    """
    Get a single serial by ID.

    Retrieves a serial record from the database by its primary key.

    Args:
        db: SQLAlchemy database session
        serial_id: Primary key ID of the serial to retrieve

    Returns:
        Serial instance if found, None otherwise

    Example:
        serial = get(db, serial_id=42)
        if serial:
            print(f"Serial: {serial.serial_number}, Status: {serial.status.value}")
    """
    return db.query(Serial).filter(Serial.id == serial_id).first()


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> List[Serial]:
    """
    Get multiple serials with pagination and optional filtering.

    Retrieves a list of serials with support for offset/limit pagination
    and optional filtering by status. Results are ordered by sequence_in_lot
    for consistent ordering within each lot.

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        status: Optional filter for serial status (CREATED, IN_PROGRESS, PASSED, FAILED)

    Returns:
        List of Serial instances matching the criteria

    Raises:
        ValueError: If status is provided but invalid

    Example:
        # Get first 10 serials
        serials = get_multi(db, skip=0, limit=10)

        # Get all failed serials
        failed_serials = get_multi(db, status="FAILED", limit=100)

        # Get passed serials with pagination
        passed_serials = get_multi(db, skip=20, limit=10, status="PASSED")
    """
    query = db.query(Serial)

    if status is not None:
        # Validate status value
        valid_statuses = {s.value for s in SerialStatus}
        if status not in valid_statuses:
            raise ValueError(
                f"status must be one of {valid_statuses}, got '{status}'"
            )
        query = query.filter(Serial.status == status)

    return (
        query.order_by(Serial.sequence_in_lot)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session,
    serial_in: SerialCreate,
) -> Serial:
    """
    Create a new serial.

    Creates and saves a new serial record in the database using validated
    Pydantic schema input. The serial_number is auto-generated in format:
    {LOT_NUMBER}-{sequence_in_lot:04d} (e.g., "LOT-001-0001").

    Args:
        db: SQLAlchemy database session
        serial_in: SerialCreate schema with validated serial data

    Returns:
        Created Serial instance with ID, serial_number, and timestamps populated

    Raises:
        IntegrityError: If lot_id is invalid or other unique constraints violated
        ValueError: If lot not found
        SQLAlchemyError: For other database operation errors

    Example:
        serial_data = SerialCreate(
            lot_id=5,
            sequence_in_lot=1,
            status="CREATED",
            rework_count=0
        )
        new_serial = create(db, serial_data)
        print(f"Created: {new_serial.serial_number}")
    """
    # Get the lot to extract lot_number for serial_number generation
    from app.models import Lot
    lot = db.query(Lot).filter(Lot.id == serial_in.lot_id).first()
    if not lot:
        raise ValueError(f"Lot with ID {serial_in.lot_id} not found")

    # Generate serial_number in format: {LOT_NUMBER}-{sequence:04d}
    serial_number = f"{lot.lot_number}-{serial_in.sequence_in_lot:04d}"

    db_serial = Serial(
        serial_number=serial_number,
        lot_id=serial_in.lot_id,
        sequence_in_lot=serial_in.sequence_in_lot,
        status=SerialStatus(serial_in.status),
        rework_count=serial_in.rework_count,
        failure_reason=serial_in.failure_reason,
    )

    try:
        db.add(db_serial)
        db.commit()
        db.refresh(db_serial)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_serial


def update(
    db: Session,
    serial_id: int,
    serial_in: SerialUpdate,
) -> Optional[Serial]:
    """
    Update an existing serial.

    Updates one or more fields of an existing serial. Only provided fields
    (those not None) are updated. The updated_at timestamp is automatically
    set by the database.

    Args:
        db: SQLAlchemy database session
        serial_id: ID of the serial to update
        serial_in: SerialUpdate schema with fields to update

    Returns:
        Updated Serial instance if found and updated, None if not found

    Raises:
        IntegrityError: If update violates constraints
        SQLAlchemyError: For other database operation errors

    Example:
        # Update only the status
        update_data = SerialUpdate(status="IN_PROGRESS")
        updated = update(db, serial_id=42, serial_in=update_data)

        # Update status and rework count
        update_data = SerialUpdate(
            status="IN_PROGRESS",
            rework_count=1
        )
        updated = update(db, serial_id=42, serial_in=update_data)
    """
    db_serial = get(db, serial_id)
    if not db_serial:
        return None

    update_data = serial_in.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            # Allow setting fields to None explicitly (e.g., clearing failure_reason)
            if field == "status" and value is not None:
                setattr(db_serial, field, SerialStatus(value))
            else:
                setattr(db_serial, field, value)

        db.commit()
        db.refresh(db_serial)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_serial


def delete(db: Session, serial_id: int) -> bool:
    """
    Delete a serial.

    Removes a serial record from the database by its primary key.
    Deletion cascades to associated process_data records.

    Args:
        db: SQLAlchemy database session
        serial_id: ID of the serial to delete

    Returns:
        True if serial was deleted, False if serial not found

    Raises:
        IntegrityError: If deletion violates foreign key constraints
        SQLAlchemyError: For other database operation errors

    Example:
        deleted = delete(db, serial_id=42)
        if deleted:
            print("Serial deleted successfully")
        else:
            print("Serial not found")
    """
    db_serial = get(db, serial_id)
    if not db_serial:
        return False

    try:
        db.delete(db_serial)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_by_number(db: Session, serial_number: str) -> Optional[Serial]:
    """
    Get a serial by unique serial_number.

    Retrieves a single serial by its unique auto-generated identifier.
    Serial numbers follow the format: {LOT_NUMBER}-XXXX (e.g., WF-KR-251110D-001-0001).

    Args:
        db: SQLAlchemy database session
        serial_number: Unique serial identifier string

    Returns:
        Serial instance if found, None otherwise

    Example:
        serial = get_by_number(db, "WF-KR-251110D-001-0001")
        if serial:
            print(f"Status: {serial.status.value}, Rework: {serial.rework_count}")

        # Alternative usage with lot and sequence info
        serial = get_by_number(db, "WF-KR-251110D-001-0042")
    """
    return (
        db.query(Serial)
        .filter(Serial.serial_number == serial_number)
        .first()
    )


def get_by_lot(
    db: Session,
    lot_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Serial]:
    """
    Get all serials in a LOT with pagination.

    Retrieves all serials belonging to a specific lot, ordered by their
    sequence within the lot for proper unit tracking.

    Args:
        db: SQLAlchemy database session
        lot_id: ID of the lot to retrieve serials from
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Serial instances in the specified lot, ordered by sequence_in_lot

    Example:
        # Get all serials in a lot
        lot_serials = get_by_lot(db, lot_id=5)

        # Get serials with pagination (10 per page, page 2)
        page_2 = get_by_lot(db, lot_id=5, skip=10, limit=10)

        # Display serials
        for serial in lot_serials:
            print(f"{serial.sequence_in_lot}: {serial.serial_number} - {serial.status.value}")
    """
    return (
        db.query(Serial)
        .filter(Serial.lot_id == lot_id)
        .order_by(Serial.sequence_in_lot)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_status(
    db: Session,
    status: str,
    skip: int = 0,
    limit: int = 100,
) -> List[Serial]:
    """
    Get serials filtered by status with pagination.

    Retrieves serials with a specific status, ordered by lot_id and sequence_in_lot
    for efficient batch processing.

    Args:
        db: SQLAlchemy database session
        status: Serial status filter (CREATED, IN_PROGRESS, PASSED, FAILED)
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Serial instances with the specified status

    Raises:
        ValueError: If status is not a valid SerialStatus value

    Example:
        # Get all created serials
        created = get_by_status(db, status="CREATED")

        # Get in-progress serials with pagination
        in_progress = get_by_status(db, status="IN_PROGRESS", skip=0, limit=50)

        # Get failed serials
        failed = get_by_status(db, status="FAILED", limit=100)
    """
    # Validate status value
    valid_statuses = {s.value for s in SerialStatus}
    if status not in valid_statuses:
        raise ValueError(
            f"status must be one of {valid_statuses}, got '{status}'"
        )

    return (
        db.query(Serial)
        .filter(Serial.status == status)
        .order_by(Serial.lot_id, Serial.sequence_in_lot)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_failed(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Serial]:
    """
    Get FAILED serials available for rework.

    Retrieves all serials with FAILED status that are candidates for rework
    (rework_count < 3). Results are ordered by lot and sequence for processing.

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of failed Serial instances available for rework

    Example:
        # Get all failed serials available for rework
        rework_candidates = get_failed(db)

        # Get first 20 failed serials
        batch = get_failed(db, skip=0, limit=20)

        # Process rework queue
        for serial in rework_candidates:
            print(f"Rework {serial.sequence_in_lot}: {serial.failure_reason}")
            increment_rework(db, serial_id=serial.id)
    """
    return (
        db.query(Serial)
        .filter(
            Serial.status == SerialStatus.FAILED,
            Serial.rework_count < 3
        )
        .order_by(Serial.lot_id, Serial.sequence_in_lot)
        .offset(skip)
        .limit(limit)
        .all()
    )


def increment_rework(db: Session, serial_id: int) -> Optional[Serial]:
    """
    Increment rework count and reset status to IN_PROGRESS.

    Transitions a failed serial back to IN_PROGRESS for rework. Increments
    rework_count by 1. Maximum 3 rework attempts are allowed.

    Args:
        db: SQLAlchemy database session
        serial_id: ID of the serial to rework

    Returns:
        Updated Serial instance with incremented rework_count and IN_PROGRESS status

    Raises:
        ValueError: If serial is not found, not in FAILED status, or max reworks exhausted
        SQLAlchemyError: For database operation errors

    Example:
        try:
            # Start rework for a failed serial
            serial = increment_rework(db, serial_id=42)
            print(f"Rework attempt {serial.rework_count} started")
        except ValueError as e:
            print(f"Cannot rework: {e}")

        # Typical workflow
        for serial in get_failed(db, limit=10):
            if serial.can_rework():
                reworked = increment_rework(db, serial_id=serial.id)
                print(f"Rework {reworked.rework_count}/3 for {reworked.serial_number}")
    """
    db_serial = get(db, serial_id)
    if not db_serial:
        raise ValueError(f"Serial with id {serial_id} not found")

    if db_serial.status != SerialStatus.FAILED:
        raise ValueError(
            f"Serial {db_serial.serial_number} is not in FAILED status, "
            f"current status: {db_serial.status.value}"
        )

    if db_serial.rework_count >= 3:
        raise ValueError(
            f"Serial {db_serial.serial_number} has exceeded maximum rework count (3)"
        )

    try:
        db_serial.rework_count += 1
        db_serial.status = SerialStatus.IN_PROGRESS
        db_serial.failure_reason = None  # Clear failure reason when reworking
        db.commit()
        db.refresh(db_serial)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_serial


def update_status(
    db: Session,
    serial_id: int,
    status: str,
    failure_reason: Optional[str] = None,
) -> Optional[Serial]:
    """
    Update serial status with validation and optional failure reason.

    Updates the serial status with state machine validation. Enforces valid
    transitions and requires failure_reason when transitioning to FAILED status.
    Automatically sets completed_at timestamp when reaching terminal states.

    Args:
        db: SQLAlchemy database session
        serial_id: ID of the serial to update
        status: Target status (CREATED, IN_PROGRESS, PASSED, FAILED)
        failure_reason: Failure reason string (required if status=FAILED, ignored otherwise)

    Returns:
        Updated Serial instance with new status, or None if not found

    Raises:
        ValueError: If status transition is invalid or constraints violated
        SQLAlchemyError: For database operation errors

    Example:
        # Transition from CREATED to IN_PROGRESS
        serial = update_status(db, serial_id=42, status="IN_PROGRESS")
        print(f"Started processing: {serial.serial_number}")

        # Mark as passed
        serial = update_status(db, serial_id=42, status="PASSED")
        print(f"Completed at: {serial.completed_at}")

        # Mark as failed with reason
        serial = update_status(
            db,
            serial_id=42,
            status="FAILED",
            failure_reason="Dimension out of tolerance"
        )

        # Invalid transition (PASSED cannot transition)
        try:
            serial = update_status(db, serial_id=42, status="FAILED")
        except ValueError as e:
            print(f"Invalid transition: {e}")
    """
    db_serial = get(db, serial_id)
    if not db_serial:
        return None

    # Validate status value
    valid_statuses = {s.value for s in SerialStatus}
    if status not in valid_statuses:
        raise ValueError(
            f"status must be one of {valid_statuses}, got '{status}'"
        )

    # Check state machine validity
    new_status = SerialStatus(status)
    if not db_serial.can_transition_to(new_status):
        raise ValueError(
            f"Invalid status transition from {db_serial.status.value} "
            f"to {new_status.value} for serial {db_serial.serial_number}"
        )

    # Validate failure_reason requirement
    if new_status == SerialStatus.FAILED:
        if not failure_reason:
            raise ValueError(
                f"failure_reason is required when updating serial to FAILED status"
            )
        db_serial.failure_reason = failure_reason

    try:
        db_serial.status = new_status

        # Set completed_at when reaching terminal states
        if new_status in (SerialStatus.PASSED, SerialStatus.FAILED):
            if db_serial.completed_at is None:
                db_serial.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_serial)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_serial


def can_rework(db: Session, serial_id: int) -> bool:
    """
    Check if a serial is eligible for rework.

    Determines whether a serial can be reworked based on current status
    and rework count. A serial is eligible for rework if:
    1. Current status is FAILED
    2. Rework count is less than 3 (max attempts)

    Args:
        db: SQLAlchemy database session
        serial_id: ID of the serial to check

    Returns:
        True if serial can be reworked, False otherwise

    Example:
        serial = get(db, serial_id=42)
        if can_rework(db, serial_id=42):
            reworked = increment_rework(db, serial_id=42)
            print(f"Rework {reworked.rework_count}/3 started")
        else:
            print("Serial cannot be reworked")

        # Check before attempting rework
        if serial.status.value == "FAILED":
            if can_rework(db, serial.id):
                increment_rework(db, serial.id)
            else:
                # Archive for scrap/return
                delete(db, serial.id)
    """
    db_serial = get(db, serial_id)
    if not db_serial:
        return False

    return db_serial.can_rework()
