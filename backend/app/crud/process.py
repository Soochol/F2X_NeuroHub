"""
CRUD operations for the Process entity.

This module implements Create, Read, Update, Delete operations for manufacturing
processes in the F2X NeuroHub MES system. Provides standard CRUD functions plus
specialized queries for retrieving processes by unique identifiers and active
processes in sequence order.

Functions:
    get: Get a single process by ID
    get_multi: Get multiple processes with pagination and filtering
    create: Create a new process
    update: Update an existing process
    delete: Delete a process (deletion is protected by trigger)
    get_by_number: Get process by unique process_number (1-8)
    get_by_code: Get process by unique process_code
    get_active: Get all active processes ordered by sort_order
    get_sequence: Get all 8 processes in sequential order (1-8)
"""

from typing import List, Optional, Literal
from sqlalchemy.orm import Session, selectinload, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.process import Process
from app.schemas.process import ProcessCreate, ProcessUpdate


def _build_optimized_query(
    query: Query,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> Query:
    """
    Build an optimized query with appropriate eager loading strategy.

    Query strategies to avoid N+1 problems:
    - minimal: No eager loading (use when relationships aren't needed)
    - standard: Load equipment_types relationship
    - full: Load all relationships including nested ones

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
        # Load equipment_types relationship if it exists
        # Note: Process model may have relationships to lot_processes, etc.
        options = []
        if hasattr(Process, 'equipment_types'):
            options.append(selectinload(Process.equipment_types))
        return query.options(*options) if options else query
    elif eager_loading == "full":
        # Load all relationships including nested ones
        options = []
        if hasattr(Process, 'equipment_types'):
            options.append(selectinload(Process.equipment_types))
        if hasattr(Process, 'lot_processes'):
            options.append(selectinload(Process.lot_processes))
        return query.options(*options) if options else query
    return query


def get(
    db: Session,
    process_id: int,
    eager_loading: Literal["minimal", "standard", "full"] = "minimal"
) -> Optional[Process]:
    """
    Get a single process by ID.

    Retrieves a process record from the database by its primary key.
    Uses minimal eager loading by default since Process has fewer relationships.

    Query strategy:
    - Minimal loading: 1 query (process only)
    - Standard/Full loading: Additional queries for relationships if they exist

    Args:
        db: SQLAlchemy database session
        process_id: Primary key ID of the process to retrieve
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        Process instance if found, None otherwise

    Example:
        process = get(db, process_id=1)
        if process:
            print(f"Found: {process.process_name_en}")
    """
    query = db.query(Process).filter(Process.id == process_id)
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    eager_loading: Literal["minimal", "standard", "full"] = "minimal"
) -> List[Process]:
    """
    Get multiple processes with pagination and optional filtering.

    Retrieves a list of processes with support for offset/limit pagination
    and optional filtering by active status. Results are ordered by sort_order
    for consistent UI display. Uses minimal eager loading by default.

    Query strategy:
    - Minimal loading: 1 query (processes only)
    - Standard/Full loading: Additional queries for relationships if needed

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        is_active: Optional filter for active status (True/False/None for all)
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of Process instances matching the criteria

    Example:
        # Get first 10 active processes
        processes = get_multi(db, skip=0, limit=10, is_active=True)

        # Get all processes
        all_processes = get_multi(db, limit=100)
    """
    query = db.query(Process)

    if is_active is not None:
        query = query.filter(Process.is_active == is_active)

    query = _build_optimized_query(query, eager_loading)
    return query.order_by(Process.sort_order).offset(skip).limit(limit).all()


def create(
    db: Session,
    process_in: ProcessCreate,
) -> Process:
    """
    Create a new process.

    Creates and saves a new process record in the database using validated
    Pydantic schema input. Automatic timestamps are set by the database.

    Args:
        db: SQLAlchemy database session
        process_in: ProcessCreate schema with validated process data

    Returns:
        Created Process instance with ID and timestamps populated

    Raises:
        IntegrityError: If process_number or process_code already exists
        SQLAlchemyError: For other database operation errors

    Example:
        process_data = ProcessCreate(
            process_number=1,
            process_code="LASER_MARKING",
            process_name_ko="레이저 마킹",
            process_name_en="Laser Marking",
            sort_order=1,
            quality_criteria={"min_power": 50}
        )
        new_process = create(db, process_data)
    """
    db_process = Process(
        process_number=process_in.process_number,
        process_code=process_in.process_code,
        process_name_ko=process_in.process_name_ko,
        process_name_en=process_in.process_name_en,
        description=process_in.description,
        estimated_duration_seconds=process_in.estimated_duration_seconds,
        quality_criteria=process_in.quality_criteria,
        is_active=process_in.is_active,
        sort_order=process_in.sort_order,
    )

    try:
        db.add(db_process)
        db.commit()
        db.refresh(db_process)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_process


def update(
    db: Session,
    process_id: int,
    process_in: ProcessUpdate,
) -> Optional[Process]:
    """
    Update an existing process.

    Updates one or more fields of an existing process. Only provided fields
    (those not None) are updated. The updated_at timestamp is automatically
    set by the database.

    Args:
        db: SQLAlchemy database session
        process_id: ID of the process to update
        process_in: ProcessUpdate schema with fields to update

    Returns:
        Updated Process instance if found and updated, None if not found

    Raises:
        IntegrityError: If update violates unique constraints (process_number, process_code)
        SQLAlchemyError: For other database operation errors

    Example:
        # Update only the description
        update_data = ProcessUpdate(description="Updated description")
        updated = update(db, process_id=1, process_in=update_data)

        # Update multiple fields
        update_data = ProcessUpdate(
            process_name_en="New Name",
            estimated_duration_seconds=120,
            is_active=False
        )
        updated = update(db, process_id=1, process_in=update_data)
    """
    db_process = get(db, process_id)
    if not db_process:
        return None

    update_data = process_in.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(db_process, field, value)

        db.commit()
        db.refresh(db_process)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_process


def delete(db: Session, process_id: int) -> bool:
    """
    Delete a process.

    Attempts to delete a process from the database. Note: Process deletion
    is restricted by a database trigger to prevent deletion of processes
    that have associated data (lot_processes). Check for FK constraint
    violations when handling exceptions.

    Args:
        db: SQLAlchemy database session
        process_id: ID of the process to delete

    Returns:
        True if process was deleted, False if process not found

    Raises:
        IntegrityError: If deletion violates FK constraints (has dependent data)
        SQLAlchemyError: For other database operation errors

    Example:
        try:
            deleted = delete(db, process_id=1)
            if deleted:
                print("Process deleted successfully")
            else:
                print("Process not found")
        except IntegrityError:
            print("Cannot delete: process has associated data")
    """
    db_process = get(db, process_id)
    if not db_process:
        return False

    try:
        db.delete(db_process)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_by_number(
    db: Session,
    process_number: int,
    eager_loading: Literal["minimal", "standard", "full"] = "minimal"
) -> Optional[Process]:
    """
    Get a process by unique process_number.

    Retrieves a single process by its unique sequence number (1-8).
    Each manufacturing process has exactly one process_number.

    Args:
        db: SQLAlchemy database session
        process_number: Process sequence number (1-8)
        eager_loading: Control eager loading depth

    Returns:
        Process instance if found, None otherwise

    Example:
        # Get the first process in the sequence
        process = get_by_number(db, 1)
        if process:
            print(f"Process 1: {process.process_name_en}")

        # Get process 5
        process_5 = get_by_number(db, 5)
    """
    query = db.query(Process).filter(
        Process.process_number == process_number
    )
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_by_code(
    db: Session,
    process_code: str,
    eager_loading: Literal["minimal", "standard", "full"] = "minimal"
) -> Optional[Process]:
    """
    Get a process by unique process_code.

    Retrieves a single process by its unique code identifier.
    Process codes are case-insensitive (stored and queried in uppercase).

    Args:
        db: SQLAlchemy database session
        process_code: Unique process code (e.g., 'LASER_MARKING')
        eager_loading: Control eager loading depth

    Returns:
        Process instance if found, None otherwise

    Example:
        process = get_by_code(db, "LASER_MARKING")
        if process:
            print(f"Found: {process.process_name_en}")

        # Code will be uppercased automatically
        process = get_by_code(db, "laser_marking")  # Also works
    """
    query = db.query(Process).filter(
        Process.process_code == process_code.upper()
    )
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_active(
    db: Session,
    eager_loading: Literal["minimal", "standard", "full"] = "minimal"
) -> List[Process]:
    """
    Get all active processes ordered by sort_order.

    Retrieves all processes where is_active is True, ordered by sort_order
    for proper display sequence in the UI. Useful for populating dropdowns
    and process selection interfaces.

    Args:
        db: SQLAlchemy database session
        eager_loading: Control eager loading depth

    Returns:
        List of active Process instances ordered by sort_order

    Example:
        active_processes = get_active(db)
        for process in active_processes:
            print(f"{process.sort_order}. {process.process_name_en}")
    """
    query = db.query(Process).filter(Process.is_active.is_(True))
    query = _build_optimized_query(query, eager_loading)
    return query.order_by(Process.sort_order).all()


def get_sequence(
    db: Session,
    eager_loading: Literal["minimal", "standard", "full"] = "minimal"
) -> List[Process]:
    """
    Get all 8 processes in sequential order (1-8).

    Retrieves all active processes ordered by process_number to display
    the complete manufacturing workflow sequence. Returns exactly 8 processes
    when all are active, representing the full production line.

    Args:
        db: SQLAlchemy database session
        eager_loading: Control eager loading depth

    Returns:
        List of Process instances ordered by process_number (1-8)

    Example:
        # Display the complete manufacturing workflow
        sequence = get_sequence(db)
        for process in sequence:
            step = process.process_number
            name = process.process_name_en
            print(f"Step {step}: {name}")

        # Expected output:
        # Step 1: Laser Marking
        # Step 2: Quality Check
        # ... (through Step 8)
    """
    query = db.query(Process).filter(Process.is_active.is_(True))
    query = _build_optimized_query(query, eager_loading)
    return query.order_by(Process.process_number).all()
