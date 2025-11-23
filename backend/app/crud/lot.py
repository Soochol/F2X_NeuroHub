"""
CRUD operations for the Lot entity.

This module implements Create, Read, Update, Delete operations for LOT (production batch)
management in the F2X NeuroHub Manufacturing Execution System. Provides standard CRUD
functions plus specialized queries for retrieving LOTs by unique identifiers, date ranges,
product models, and status filters.

Functions:
    get: Get a single LOT by ID
    get_multi: Get multiple LOTs with pagination
    create: Create a new LOT
    update: Update an existing LOT
    delete: Delete a LOT (protected by trigger)
    get_by_number: Get LOT by unique LOT number (WF-KR-YYMMDD{D|N}-nnn)
    get_active: Get LOTs in CREATED or IN_PROGRESS status
    get_by_date_range: Filter LOTs by production date range
    get_by_product_model: Filter LOTs by product model
    get_by_status: Filter LOTs by status
    update_quantities: Recalculate quantities from serials
    close_lot: Close completed LOT (set status to CLOSED and closed_at timestamp)
"""

from datetime import date, datetime
from typing import List, Optional, Literal

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, selectinload, joinedload, Query
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.lot import Lot, LotStatus
from app.models.serial import Serial, SerialStatus
from app.schemas.lot import LotCreate, LotUpdate


def _build_optimized_query(
    query: Query,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> Query:
    """
    Build an optimized query with appropriate eager loading strategy.

    Query strategies to avoid N+1 problems:
    - minimal: No eager loading (use when relationships aren't needed)
    - standard: Load common relationships (serials, wip_items)
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
        # Use selectinload for collections to avoid cartesian product
        return query.options(
            selectinload(Lot.serials),
            selectinload(Lot.wip_items),
            # Use joinedload for single relationships
            joinedload(Lot.product_model),
            joinedload(Lot.production_line)
        )
    elif eager_loading == "full":
        # Load nested relationships as well
        return query.options(
            selectinload(Lot.serials).joinedload(Serial.lot),
            selectinload(Lot.wip_items),
            joinedload(Lot.product_model),
            joinedload(Lot.production_line)
        )
    return query


def get(db: Session, lot_id: int, eager_loading: Literal["minimal", "standard", "full"] = "standard") -> Optional[Lot]:
    """
    Get a single LOT by ID.

    Retrieves a LOT record from the database by its primary key.
    By default, eager loads common relationships to avoid N+1 queries.

    Query strategy:
    - Standard loading: 3 queries total (1 for LOT + 1 for serials + 1 for wip_items)
    - Without optimization: 1 + N queries where N is number of accessed relationships

    Args:
        db: SQLAlchemy database session
        lot_id: Primary key ID of the LOT to retrieve
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        Lot instance if found, None otherwise

    Example:
        # Standard usage with optimized loading
        lot = get(db, lot_id=1)
        if lot:
            print(f"Found LOT: {lot.lot_number}")
            print(f"Serials: {len(lot.serials)}")  # No additional query

        # Minimal loading when relationships aren't needed
        lot = get(db, lot_id=1, eager_loading="minimal")
    """
    query = db.query(Lot).filter(Lot.id == lot_id)
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[Lot]:
    """
    Get multiple LOTs with pagination.

    Retrieves a list of LOTs with support for offset/limit pagination.
    Results are ordered by created_at (descending) and id (descending) to show
    most recently created LOTs first.

    Query optimization:
    - With standard loading for 100 LOTs: ~4 queries total
    - Without optimization for 100 LOTs: 1 + 200+ queries (N+1 problem)

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of Lot instances matching the criteria

    Example:
        # Get first 10 LOTs with optimized loading
        lots = get_multi(db, skip=0, limit=10)
        for lot in lots:
            print(f"{lot.lot_number}: {len(lot.serials)} serials")  # No N+1

        # Get LOTs without relationship loading for listing
        lots = get_multi(db, eager_loading="minimal")
    """
    query = db.query(Lot).order_by(Lot.created_at.desc(), Lot.id.desc())
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def create(
    db: Session,
    lot_in: LotCreate,
) -> Lot:
    """
    Create a new LOT.

    Creates and saves a new LOT record in the database using validated
    Pydantic schema input. The LOT number is auto-generated in Python code
    (format: {Country 2}{Line 2}{Model 3}{Month 4}{Seq 2} = 13 chars).
    The sequence number is auto-incremented within the same month.
    Status defaults to CREATED.

    Args:
        db: SQLAlchemy database session
        lot_in: LotCreate schema with validated LOT data

    Returns:
        Created Lot instance with ID, lot_number, and timestamps populated

    Raises:
        IntegrityError: If creation violates unique constraints
        SQLAlchemyError: For other database operation errors
        ValueError: If product_model_id or production_line_id is invalid

    Example:
        lot_data = LotCreate(
            product_model_id=1,
            production_line_id=1,
            production_date=date(2025, 11, 18),
            target_quantity=50,
            status=LotStatus.CREATED
        )
        new_lot = create(db, lot_data)
        # Generated lot_number: KR01PSA251101 (13 chars)
    """
    # Import ProductModel and ProductionLine here to avoid circular imports
    from app.models.product_model import ProductModel
    from app.models.production_line import ProductionLine

    # 1. Get ProductModel to extract model prefix
    product_model = db.query(ProductModel).filter(
        ProductModel.id == lot_in.product_model_id
    ).first()
    if not product_model:
        raise ValueError(f"Invalid product_model_id: {lot_in.product_model_id}")

    # Extract model prefix from model_code (first 3 chars, e.g., "PSA10" -> "PSA")
    model_prefix = product_model.model_code[:3].upper()

    # 2. Get ProductionLine to extract line code
    production_line = db.query(ProductionLine).filter(
        ProductionLine.id == lot_in.production_line_id
    ).first()
    if not production_line:
        raise ValueError(f"Invalid production_line_id: {lot_in.production_line_id}")

    line_code = production_line.line_code

    # 3. Generate LOT number: {Country 2}{Line 2}{Model 3}{Month 4}{Seq 2} = 13 chars
    # Extract components for LOT generation
    # line_code format: "KR001" → country="KR", line_number="01"
    if len(line_code) < 3:
        raise ValueError(f"Invalid line_code format: {line_code}")

    country_code = line_code[:2].upper()  # "KR"
    line_number_str = line_code[2:]  # "001"
    try:
        line_number = int(line_number_str)  # 1
        line_number_formatted = f"{line_number:02d}"  # "01"
    except ValueError:
        raise ValueError(f"Invalid line number in line_code: {line_code}")

    # model_prefix is already 3 chars (e.g., "PSA")
    model_code = model_prefix[:3].upper()

    # Format production month as YYMM
    production_month = lot_in.production_date.strftime('%y%m')  # "2511" for Nov 2025

    # Generate base LOT number (11 chars)
    lot_number_base = f"{country_code}{line_number_formatted}{model_code}{production_month}"

    # 4. Find the last sequence number for this base LOT number
    last_lot = (
        db.query(Lot)
        .filter(Lot.lot_number.like(f"{lot_number_base}%"))
        .order_by(Lot.lot_number.desc())
        .first()
    )

    # Calculate next sequence number
    if last_lot and len(last_lot.lot_number) >= 13:
        try:
            last_seq = int(last_lot.lot_number[-2:])
            new_seq = last_seq + 1
        except ValueError:
            # If last 2 chars are not numeric, start from 1
            new_seq = 1
    else:
        new_seq = 1

    # Validate sequence doesn't exceed 99 (2-digit limit)
    if new_seq > 99:
        raise ValueError(
            f"LOT sequence limit exceeded for {lot_number_base}. "
            f"Maximum 99 LOTs per line/model/month combination."
        )

    # Generate final 13-char LOT number
    lot_number = f"{lot_number_base}{new_seq:02d}"

    db_lot = Lot(
        lot_number=lot_number,
        product_model_id=lot_in.product_model_id,
        production_line_id=lot_in.production_line_id,
        production_date=lot_in.production_date,
        target_quantity=lot_in.target_quantity,
        status=lot_in.status,
        parent_spring_lot=lot_in.parent_spring_lot,
        sma_spring_lot=lot_in.sma_spring_lot,
        # actual_quantity, passed_quantity, failed_quantity default to 0
    )

    try:
        db.add(db_lot)
        db.commit()
        db.refresh(db_lot)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_lot


def update(
    db: Session,
    lot_id: int,
    lot_in: LotUpdate,
) -> Optional[Lot]:
    """
    Update an existing LOT.

    Updates one or more fields of an existing LOT. Only provided fields
    (those not None) are updated. The updated_at timestamp is automatically
    set by the database.

    Args:
        db: SQLAlchemy database session
        lot_id: ID of the LOT to update
        lot_in: LotUpdate schema with fields to update

    Returns:
        Updated Lot instance if found and updated, None if not found

    Raises:
        IntegrityError: If update violates unique constraints
        SQLAlchemyError: For other database operation errors

    Example:
        # Update status and quantities
        update_data = LotUpdate(
            status=LotStatus.IN_PROGRESS,
            actual_quantity=50,
            passed_quantity=48
        )
        updated = update(db, lot_id=1, lot_in=update_data)
    """
    db_lot = get(db, lot_id)
    if not db_lot:
        return None

    update_data = lot_in.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(db_lot, field, value)

        db.commit()
        db.refresh(db_lot)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_lot


def delete(db: Session, lot_id: int) -> bool:
    """
    Delete a LOT.

    Attempts to delete a LOT from the database. Note: LOT deletion is
    restricted by a database trigger to prevent deletion of LOTs that have
    associated serials. Check for FK constraint violations when handling exceptions.

    Args:
        db: SQLAlchemy database session
        lot_id: ID of the LOT to delete

    Returns:
        True if LOT was deleted, False if LOT not found

    Raises:
        IntegrityError: If deletion violates FK constraints (has dependent serials)
        SQLAlchemyError: For other database operation errors

    Example:
        try:
            deleted = delete(db, lot_id=1)
            if deleted:
                print("LOT deleted successfully")
            else:
                print("LOT not found")
        except IntegrityError:
            print("Cannot delete: LOT has associated serials")
    """
    db_lot = get(db, lot_id)
    if not db_lot:
        return False

    try:
        db.delete(db_lot)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_by_number(db: Session, lot_number: str, eager_loading: Literal["minimal", "standard", "full"] = "standard") -> Optional[Lot]:
    """
    Get a LOT by unique LOT number.

    Retrieves a single LOT by its unique lot_number identifier.
    LOT number format: {Country 2}{Line 2}{Model 3}{Month 4}{Seq 2} = 13 chars
    (e.g., KR01PSA251101)

    Query optimization: Uses eager loading to prevent N+1 queries when accessing relationships.

    Args:
        db: SQLAlchemy database session
        lot_number: Unique LOT identifier
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        Lot instance if found, None otherwise

    Example:
        lot = get_by_number(db, "KR01PSA251101")
        if lot:
            print(f"Found LOT: {lot.lot_number}")
            print(f"Model: {lot.product_model.model_code}")  # No additional query
    """
    query = db.query(Lot).filter(Lot.lot_number == lot_number)
    query = _build_optimized_query(query, eager_loading)
    return query.first()


def get_active(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[Lot]:
    """
    Get active LOTs (CREATED or IN_PROGRESS status).

    Retrieves LOTs that are currently in active production. Results are ordered
    by production_date (descending) and lot_number (descending) to show recent
    LOTs first.

    Query optimization: Eager loads relationships to avoid N+1 queries for active lots.

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of Lot instances with CREATED or IN_PROGRESS status

    Example:
        # Get active LOTs with optimized loading
        active_lots = get_active(db)
        for lot in active_lots:
            print(f"{lot.lot_number}: {len(lot.serials)}/{lot.target_quantity}")

        # Get first 50 active LOTs with minimal loading
        active_lots = get_active(db, skip=0, limit=50, eager_loading="minimal")
    """
    query = (
        db.query(Lot)
        .filter(Lot.status.in_([LotStatus.CREATED, LotStatus.IN_PROGRESS]))
        .order_by(desc(Lot.production_date), desc(Lot.lot_number))
    )
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def get_by_date_range(
    db: Session,
    start_date: date,
    end_date: date,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Lot]:
    """
    Get LOTs by production date range.

    Retrieves LOTs with production_date between start_date and end_date (inclusive).
    Results are ordered by production_date (descending) and lot_number (descending).

    Args:
        db: SQLAlchemy database session
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Lot instances within the date range

    Example:
        from datetime import date, timedelta

        # Get LOTs from the last 7 days
        end = date.today()
        start = end - timedelta(days=7)
        lots = get_by_date_range(db, start, end)

        # Get LOTs from November 2025
        lots = get_by_date_range(db, date(2025, 11, 1), date(2025, 11, 30))
    """
    return (
        db.query(Lot)
        .filter(and_(
            Lot.production_date >= start_date,
            Lot.production_date <= end_date
        ))
        .order_by(desc(Lot.production_date), desc(Lot.lot_number))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_product_model(
    db: Session,
    product_model_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Lot]:
    """
    Get LOTs by product model.

    Retrieves all LOTs for a specific product model, ordered by production_date
    (descending) and lot_number (descending).

    Args:
        db: SQLAlchemy database session
        product_model_id: Product model ID to filter by
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Lot instances for the specified product model

    Example:
        # Get all LOTs for product model 1
        lots = get_by_product_model(db, product_model_id=1)

        # Get first 50 LOTs for product model 2
        lots = get_by_product_model(db, product_model_id=2, limit=50)
    """
    return (
        db.query(Lot)
        .filter(Lot.product_model_id == product_model_id)
        .order_by(desc(Lot.production_date), desc(Lot.lot_number))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_status(
    db: Session,
    status: str,
    *,
    skip: int = 0,
    limit: int = 100,
    eager_loading: Literal["minimal", "standard", "full"] = "standard"
) -> List[Lot]:
    """
    Get LOTs by status.

    Retrieves LOTs with the specified status, ordered by production_date
    (descending) and lot_number (descending). Status must be one of:
    CREATED, IN_PROGRESS, COMPLETED, CLOSED

    Query optimization: Uses eager loading to prevent N+1 queries.

    Args:
        db: SQLAlchemy database session
        status: LOT status to filter by (CREATED, IN_PROGRESS, COMPLETED, CLOSED)
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        eager_loading: Control eager loading depth ("minimal", "standard", "full")

    Returns:
        List of Lot instances with the specified status

    Example:
        # Get all completed LOTs with relationships
        completed = get_by_status(db, LotStatus.COMPLETED)
        for lot in completed:
            print(f"{lot.lot_number}: {lot.passed_quantity}/{lot.actual_quantity}")

        # Get all closed LOTs with minimal loading for listing
        closed = get_by_status(db, LotStatus.CLOSED, limit=50, eager_loading="minimal")
    """
    query = (
        db.query(Lot)
        .filter(Lot.status == status)
        .order_by(desc(Lot.production_date), desc(Lot.lot_number))
    )
    query = _build_optimized_query(query, eager_loading)
    return query.offset(skip).limit(limit).all()


def update_quantities(db: Session, lot_id: int) -> Optional[Lot]:
    """
    Recalculate LOT quantities from associated serials.

    Recalculates actual_quantity, passed_quantity, and failed_quantity by
    counting serials with different statuses. This is typically called after
    bulk serial status updates.

    Quantities calculated:
        - actual_quantity: Count of all serials
        - passed_quantity: Count of serials with status PASSED
        - failed_quantity: Count of serials with status FAILED

    Args:
        db: SQLAlchemy database session
        lot_id: ID of the LOT to update

    Returns:
        Updated Lot instance if found, None if LOT not found

    Raises:
        SQLAlchemyError: For database operation errors

    Example:
        # Recalculate quantities after bulk serial updates
        lot = update_quantities(db, lot_id=1)
        if lot:
            print(f"Actual: {lot.actual_quantity}, Passed: {lot.passed_quantity}")
    """
    db_lot = get(db, lot_id)
    if not db_lot:
        return None

    try:
        # Count total serials
        actual_qty = (
            db.query(func.count(Serial.id))
            .filter(Serial.lot_id == lot_id)
            .scalar() or 0
        )

        # Count passed serials
        passed_qty = (
            db.query(func.count(Serial.id))
            .filter(and_(
                Serial.lot_id == lot_id,
                Serial.status == SerialStatus.PASSED
            ))
            .scalar() or 0
        )

        # Count failed serials
        failed_qty = (
            db.query(func.count(Serial.id))
            .filter(and_(
                Serial.lot_id == lot_id,
                Serial.status == SerialStatus.FAILED
            ))
            .scalar() or 0
        )

        # Update LOT quantities
        db_lot.actual_quantity = actual_qty
        db_lot.passed_quantity = passed_qty
        db_lot.failed_quantity = failed_qty

        db.commit()
        db.refresh(db_lot)

    except SQLAlchemyError:
        db.rollback()
        raise

    return db_lot


def close_lot(db: Session, lot_id: int) -> Optional[Lot]:
    """
    Close a completed LOT.

    Transitions a LOT to CLOSED status and sets the closed_at timestamp to current time.
    This typically happens after a LOT has been COMPLETED and all quality checks are done.

    Status transition: Any status → CLOSED (with closed_at timestamp)

    Args:
        db: SQLAlchemy database session
        lot_id: ID of the LOT to close

    Returns:
        Updated Lot instance if found and closed, None if LOT not found

    Raises:
        SQLAlchemyError: For database operation errors

    Example:
        # Close a completed LOT
        closed_lot = close_lot(db, lot_id=1)
        if closed_lot:
            print(f"LOT {closed_lot.lot_number} closed at {closed_lot.closed_at}")
    """
    db_lot = get(db, lot_id)
    if not db_lot:
        return None

    try:
        db_lot.status = LotStatus.CLOSED
        db_lot.closed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_lot)

    except SQLAlchemyError:
        db.rollback()
        raise

    return db_lot
