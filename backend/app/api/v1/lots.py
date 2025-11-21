"""FastAPI router for Lot entity endpoints.

This module provides RESTful API endpoints for managing production batches (LOTs)
in the F2X NeuroHub MES system. It implements standard CRUD operations plus
additional query endpoints for filtering LOTs by various criteria.

Provides:
    - GET /: List all LOTs with pagination
    - GET /{id}: Get LOT by primary key
    - GET /number/{lot_number}: Get LOT by unique LOT number (WF-KR-YYMMDD{D|N}-nnn)
    - GET /active: List active LOTs (CREATED or IN_PROGRESS status)
    - GET /date-range: Filter LOTs by production date range
    - GET /product/{product_model_id}: Filter LOTs by product model
    - GET /status/{status}: Filter LOTs by status
    - GET /{id}/quantities: Get current quantities (actual, passed, failed)
    - POST /: Create new LOT
    - POST /{id}/start-wip-generation: Generate WIP IDs for LOT (BR-001, BR-002)
    - POST /{id}/close: Close completed LOT (transition to CLOSED status)
    - PUT /{id}: Update existing LOT
    - PUT /{id}/quantities: Recalculate quantities from serials
    - DELETE /{id}: Delete LOT

All endpoints include:
    - Comprehensive docstrings with operation descriptions
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
    - Error handling with descriptive HTTPException responses
    - Dependency injection for database sessions
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.crud import lot as crud
from app.crud import wip_item as wip_crud
from app.schemas.lot import (
    LotCreate,
    LotUpdate,
    LotInDB,
    LotStatus,
    Shift,
)
from app.schemas.wip_item import WIPItemInDB
# New exception imports
from app.core.exceptions import (
    LotNotFoundException,
    DuplicateResourceException,
    ValidationException,
)
from app.services.wip_service import WIPValidationError


router = APIRouter(
    prefix="/lots",
    tags=["Lots"],
    responses={
        404: {"description": "Lot not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)


@router.get(
    "/",
    response_model=List[LotInDB],
    summary="List all LOTs",
    description="Retrieve a paginated list of LOTs ordered by production date (newest first), optionally filtered by status",
)
def list_lots(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of records to return"),
    status: Optional[LotStatus] = Query(None, description="Filter by LOT status (CREATED, IN_PROGRESS, COMPLETED, CLOSED)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[LotInDB]:
    """List all LOTs with pagination and optional status filter.

    Retrieves a paginated list of LOTs from the database, ordered by
    production date in descending order (newest first) and lot number (descending).
    Supports configurable offset and limit for pagination control, and optional
    status filtering.

    Args:
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        status: Optional LOT status filter.
            If provided, only LOTs with this status are returned.
            Valid values: CREATED, IN_PROGRESS, COMPLETED, CLOSED
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[LotInDB]: List of LOT records with database fields.
            Empty list if no records match criteria.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get first 10 LOTs:
        >>> GET /api/v1/lots/?skip=0&limit=10

        Get next page (items 10-20):
        >>> GET /api/v1/lots/?skip=10&limit=10

        Get all records (large limit):
        >>> GET /api/v1/lots/?skip=0&limit=10000

        Get only COMPLETED LOTs:
        >>> GET /api/v1/lots/?status=COMPLETED

        Get IN_PROGRESS LOTs with pagination:
        >>> GET /api/v1/lots/?status=IN_PROGRESS&skip=0&limit=20

    OpenAPI Parameters:
        skip: Query parameter, non-negative integer
        limit: Query parameter, positive integer (1-10000)
        status: Query parameter, optional LOT status enum
    """
    # Debug - Status Filter Investigation
    print(f"\n{'='*80}")
    print(f"[STATUS FILTER DEBUG] list_lots called")
    print(f"  status parameter: {status}")
    print(f"  status type: {type(status)}")
    print(f"  skip: {skip}, limit: {limit}")
    print(f"{'='*80}\n")

    # If status filter is provided, use get_by_status
    if status:
        print(f"[FILTER] Using get_by_status with status={status.value}")
        result = crud.get_by_status(db, status=status.value, skip=skip, limit=limit)
        print(f"[FILTER] Returned {len(result)} LOTs")
        return result

    # Otherwise, return all LOTs
    print(f"[NO FILTER] Returning all LOTs")
    result = crud.get_multi(db, skip=skip, limit=limit)
    print(f"[NO FILTER] Returned {len(result)} LOTs")
    return result


@router.get(
    "/{id}",
    response_model=LotInDB,
    summary="Get LOT by ID",
    description="Retrieve a specific LOT using its primary key identifier",
    responses={404: {"description": "Lot not found"}},
)
def get_lot(
    id: int = Path(..., gt=0, description="Primary key identifier of the LOT"),
    db: Session = Depends(deps.get_db),
) -> LotInDB:
    """Get LOT by primary key ID.

    Retrieves a single LOT record from the database using its unique
    primary key identifier.

    Args:
        id: Primary key identifier of the LOT to retrieve.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        LotInDB: LOT record with all database fields.

    Raises:
        HTTPException: 404 Not Found if LOT does not exist with given ID.

    Examples:
        Get LOT with ID 1:
        >>> GET /api/v1/lots/1

        Get LOT with ID 42:
        >>> GET /api/v1/lots/42

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "product_model_id": 1,
            "production_date": "2025-11-18",
            "shift": "D",
            "target_quantity": 100,
            "actual_quantity": 95,
            "passed_quantity": 92,
            "failed_quantity": 3,
            "status": "IN_PROGRESS",
            "created_at": "2025-11-18T08:30:00",
            "updated_at": "2025-11-18T14:15:00",
            "closed_at": null,
            "product_model": {...},
            "defect_rate": 3.16,
            "pass_rate": 96.84
        }
    """
    obj = crud.get(db, lot_id=id)
    if not obj:
        raise LotNotFoundException(id)
    return obj


@router.get(
    "/number/{lot_number}",
    response_model=LotInDB,
    summary="Get LOT by LOT number",
    description="Retrieve a LOT using its unique LOT number (11 characters)",
    responses={404: {"description": "Lot not found"}},
)
def get_lot_by_number(
    lot_number: str = Path(..., pattern="^[A-Z]{2}\d{2}[A-Z]{3}\d{4}$", description="Unique LOT identifier (11 chars)"),
    db: Session = Depends(deps.get_db),
) -> LotInDB:
    """Get LOT by unique LOT number.

    Retrieves a single LOT using its unique LOT number identifier.
    LOT number format: {Country 2}{Line 2}{Model 3}{Month 4} = 11 chars
        - Country: 2-char country code (e.g., "KR" for Korea)
        - Line: 2-digit production line number (e.g., "01")
        - Model: 3-char model code (e.g., "PSA")
        - Month: 4-digit year/month YYMM format (e.g., "2511" for Nov 2025)

    Args:
        lot_number: Unique LOT identifier (11 characters)
            (e.g., KR01PSA2511)
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        LotInDB: LOT record with all database fields.

    Raises:
        HTTPException: 404 Not Found if LOT does not exist with given number.

    Examples:
        Get LOT by number:
        >>> GET /api/v1/lots/number/KR01PSA2511

        Get LOT with different number:
        >>> GET /api/v1/lots/number/KR02WFA2511

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "KR01PSA2511",
            "product_model_id": 1,
            "production_date": "2025-11-18",
            "shift": "D",
            "target_quantity": 100,
            "actual_quantity": 95,
            ...
        }
    """
    obj = crud.get_by_number(db, lot_number=lot_number)
    if not obj:
        raise LotNotFoundException(lot_number=lot_number)
    return obj


@router.get(
    "/active",
    response_model=List[LotInDB],
    summary="List active LOTs",
    description="Retrieve paginated list of active LOTs (CREATED or IN_PROGRESS status)",
)
def get_active_lots(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
) -> List[LotInDB]:
    """Get active LOTs with pagination.

    Retrieves only LOTs with CREATED or IN_PROGRESS status, indicating they are
    currently in active production. Results are ordered by production_date (descending)
    and lot_number (descending) to show recent LOTs first. Supports pagination for
    managing large result sets.

    Args:
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[LotInDB]: List of active LOT records.
            Empty list if no active LOTs exist.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get all active LOTs:
        >>> GET /api/v1/lots/active

        Paginate through active LOTs (10 per page):
        >>> GET /api/v1/lots/active?skip=0&limit=10
        >>> GET /api/v1/lots/active?skip=10&limit=10

    Response Example (200 OK):
        [
            {
                "id": 1,
                "lot_number": "WF-KR-251118D-001",
                "status": "IN_PROGRESS",
                ...
            },
            {
                "id": 2,
                "lot_number": "WF-KR-251118N-002",
                "status": "CREATED",
                ...
            }
        ]
    """
    return crud.get_active(db, skip=skip, limit=limit)


@router.get(
    "/date-range",
    response_model=List[LotInDB],
    summary="Filter LOTs by date range",
    description="Retrieve LOTs within a specified production date range",
)
def get_lots_by_date_range(
    start_date: date = Query(..., description="Start of date range (inclusive, YYYY-MM-DD)"),
    end_date: date = Query(..., description="End of date range (inclusive, YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
) -> List[LotInDB]:
    """Get LOTs within production date range.

    Retrieves LOTs with production_date between start_date and end_date (inclusive).
    Results are ordered by production_date (descending) and lot_number (descending).
    Useful for retrieving LOTs from specific periods (daily, weekly, monthly reports).

    Args:
        start_date: Start of date range (inclusive) in format YYYY-MM-DD.
        end_date: End of date range (inclusive) in format YYYY-MM-DD.
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[LotInDB]: List of LOTs within the date range.
            Empty list if no LOTs exist in range.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get LOTs from specific date:
        >>> GET /api/v1/lots/date-range?start_date=2025-11-18&end_date=2025-11-18

        Get LOTs from November 2025:
        >>> GET /api/v1/lots/date-range?start_date=2025-11-01&end_date=2025-11-30

        Get last 7 days with pagination:
        >>> GET /api/v1/lots/date-range?start_date=2025-11-11&end_date=2025-11-18&limit=50

    Response Example (200 OK):
        [
            {
                "id": 1,
                "lot_number": "WF-KR-251118D-001",
                "production_date": "2025-11-18",
                ...
            },
            {
                "id": 2,
                "lot_number": "WF-KR-251118N-002",
                "production_date": "2025-11-18",
                ...
            }
        ]
    """
    return crud.get_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)


@router.get(
    "/product/{product_model_id}",
    response_model=List[LotInDB],
    summary="Filter LOTs by product model",
    description="Retrieve paginated list of LOTs for a specific product model",
)
def get_lots_by_product_model(
    product_model_id: int = Path(..., gt=0, description="Product model identifier"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
) -> List[LotInDB]:
    """Get LOTs filtered by product model with pagination.

    Retrieves all LOTs for a specific product model, ordered by production_date
    (descending) and lot_number (descending). Useful for tracking production history
    and performance metrics for a specific product.

    Args:
        product_model_id: Product model ID to filter by.
            Must be a positive integer.
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[LotInDB]: List of LOTs for the specified product model.
            Empty list if no LOTs exist for product.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get all LOTs for product model 1:
        >>> GET /api/v1/lots/product/1

        Get first 50 LOTs for product model 2:
        >>> GET /api/v1/lots/product/2?skip=0&limit=50

        Get LOTs with pagination:
        >>> GET /api/v1/lots/product/1?skip=100&limit=25

    Response Example (200 OK):
        [
            {
                "id": 1,
                "lot_number": "WF-KR-251118D-001",
                "product_model_id": 1,
                "production_date": "2025-11-18",
                ...
            }
        ]
    """
    return crud.get_by_product_model(db, product_model_id=product_model_id, skip=skip, limit=limit)


@router.get(
    "/status/{status}",
    response_model=List[LotInDB],
    summary="Filter LOTs by status",
    description="Retrieve paginated list of LOTs filtered by status",
)
def get_lots_by_status(
    status: str = Path(..., description="LOT status: CREATED, IN_PROGRESS, COMPLETED, CLOSED"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
) -> List[LotInDB]:
    """Get LOTs filtered by status with pagination.

    Retrieves LOTs with the specified status, ordered by production_date
    (descending) and lot_number (descending). Status must be one of:
    CREATED, IN_PROGRESS, COMPLETED, CLOSED

    Args:
        status: LOT status to filter by.
            Valid values: CREATED, IN_PROGRESS, COMPLETED, CLOSED
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-10000).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[LotInDB]: List of LOTs with specified status.
            Empty list if no LOTs exist with status.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.

    Examples:
        Get all completed LOTs:
        >>> GET /api/v1/lots/status/COMPLETED

        Get all closed LOTs:
        >>> GET /api/v1/lots/status/CLOSED?limit=50

        Get in-progress LOTs with pagination:
        >>> GET /api/v1/lots/status/IN_PROGRESS?skip=0&limit=20

    Response Example (200 OK):
        [
            {
                "id": 1,
                "lot_number": "WF-KR-251118D-001",
                "status": "COMPLETED",
                ...
            }
        ]
    """
    return crud.get_by_status(db, status=status, skip=skip, limit=limit)


@router.get(
    "/{id}/quantities",
    response_model=LotInDB,
    summary="Get LOT quantities",
    description="Retrieve current quantity metrics (actual, passed, failed) for a LOT",
    responses={404: {"description": "Lot not found"}},
)
def get_lot_quantities(
    id: int = Path(..., gt=0, description="Primary key identifier of the LOT"),
    db: Session = Depends(deps.get_db),
) -> LotInDB:
    """Get current quantities for a LOT.

    Retrieves a LOT record with focus on quantity metrics:
    - actual_quantity: Total units produced in this LOT
    - passed_quantity: Units that passed all quality checks
    - failed_quantity: Units that failed quality checks
    - defect_rate: Calculated percentage of failed units (0-100%)
    - pass_rate: Calculated percentage of passed units (0-100%)

    These metrics are automatically calculated from associated serial records
    and can be recalculated using the PUT /{id}/quantities endpoint.

    Args:
        id: Primary key identifier of the LOT.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        LotInDB: LOT record with all quantity fields and calculated metrics.

    Raises:
        HTTPException: 404 Not Found if LOT does not exist.

    Examples:
        Get quantities for LOT ID 1:
        >>> GET /api/v1/lots/1/quantities

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "actual_quantity": 95,
            "passed_quantity": 92,
            "failed_quantity": 3,
            "defect_rate": 3.16,
            "pass_rate": 96.84,
            ...
        }
    """
    obj = crud.get(db, lot_id=id)
    if not obj:
        raise LotNotFoundException(id)
    return obj


@router.post(
    "/",
    response_model=LotInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new LOT",
    description="Create a new production batch (LOT) with specified parameters",
)
def create_lot(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: LotCreate,
) -> LotInDB:
    """Create new LOT.

    Creates a new LOT record with validated data from the request body.
    The LOT number is auto-generated by database trigger in format WF-KR-YYMMDD{D|N}-nnn.
    Status defaults to CREATED, and initial quantities default to 0.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        obj_in: LotCreate schema with validated LOT data.
            Required: product_model_id, production_date, shift, target_quantity
            Optional: status (defaults to CREATED)

    Returns:
        LotInDB: Newly created LOT record with all fields including
            database-generated lot_number, ID, and timestamps.

    Raises:
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 409 Conflict if constraint violation occurs.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Create minimal LOT:
        >>> POST /api/v1/lots/
        >>> {
        ...     "product_model_id": 1,
        ...     "production_date": "2025-11-18",
        ...     "shift": "D",
        ...     "target_quantity": 100
        ... }

        Create LOT with specific status:
        >>> POST /api/v1/lots/
        >>> {
        ...     "product_model_id": 1,
        ...     "production_date": "2025-11-18",
        ...     "shift": "N",
        ...     "target_quantity": 50,
        ...     "status": "CREATED"
        ... }

    Response Example (201 Created):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "product_model_id": 1,
            "production_date": "2025-11-18",
            "shift": "D",
            "target_quantity": 100,
            "actual_quantity": 0,
            "passed_quantity": 0,
            "failed_quantity": 0,
            "status": "CREATED",
            "created_at": "2025-11-18T08:30:00",
            "updated_at": "2025-11-18T08:30:00",
            "closed_at": null,
            "product_model": {...},
            "defect_rate": null,
            "pass_rate": null
        }
    """
    try:
        return crud.create(db, lot_in=obj_in)
    except IntegrityError as e:
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate" in error_str:
            raise DuplicateResourceException(
                resource_type="Lot",
                identifier=f"lot_number={obj_in.lot_number}"
            )
        if "foreign key" in error_str:
            raise ConstraintViolationException(
                message="Invalid product_model_id or other foreign key reference"
            )
        raise DatabaseException(message=f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database operation failed: {str(e)}")


@router.post(
    "/{id}/start-wip-generation",
    response_model=List[WIPItemInDB],
    status_code=status.HTTP_201_CREATED,
    summary="Generate WIP IDs for LOT",
    description="Generate batch of WIP IDs for a LOT (BR-001, BR-002)",
    responses={
        404: {"description": "LOT not found"},
        400: {"description": "Invalid request data (validation failed)"},
    },
)
def start_wip_generation(
    id: int = Path(..., gt=0, description="LOT identifier"),
    quantity: int = Query(..., ge=1, le=100, description="Number of WIP IDs to generate"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[WIPItemInDB]:
    """
    Generate batch of WIP IDs for a LOT.

    Business Rules:
        BR-001: LOT must be in CREATED status
        BR-002: WIP generation transitions LOT to IN_PROGRESS

    Args:
        id: LOT identifier
        quantity: Number of WIP IDs (1-100)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of created WIP items

    Raises:
        HTTPException: 404 if LOT not found, 400 if validation fails
    """
    try:
        wip_items = wip_crud.create_batch(db, id, quantity)
        return wip_items
    except WIPValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{id}",
    response_model=LotInDB,
    summary="Update LOT",
    description="Update existing LOT with new values",
    responses={
        404: {"description": "Lot not found"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)
def update_lot(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0, description="Primary key identifier of the LOT"),
    obj_in: LotUpdate,
) -> LotInDB:
    """Update existing LOT.

    Updates specific fields in an existing LOT record. All fields are
    optional, supporting partial updates. Only provided fields are modified;
    unspecified fields retain their current values. The updated_at timestamp
    is automatically set by the database.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        id: Primary key identifier of LOT to update.
            Must be a positive integer.
        obj_in: LotUpdate schema with field updates.
            All fields are optional. Only provided fields are updated.

    Returns:
        LotInDB: Updated LOT record with all fields.

    Raises:
        HTTPException: 404 Not Found if LOT does not exist.
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 409 Conflict if constraint violation occurs.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Update status to IN_PROGRESS:
        >>> PUT /api/v1/lots/1
        >>> {
        ...     "status": "IN_PROGRESS"
        ... }

        Update quantities after production:
        >>> PUT /api/v1/lots/1
        >>> {
        ...     "actual_quantity": 95,
        ...     "passed_quantity": 92,
        ...     "failed_quantity": 3
        ... }

        Update multiple fields:
        >>> PUT /api/v1/lots/1
        >>> {
        ...     "status": "COMPLETED",
        ...     "actual_quantity": 100,
        ...     "passed_quantity": 98,
        ...     "failed_quantity": 2
        ... }

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "status": "IN_PROGRESS",
            "actual_quantity": 95,
            "passed_quantity": 92,
            "failed_quantity": 3,
            "updated_at": "2025-11-18T14:15:00",
            ...
        }
    """
    obj = crud.get(db, lot_id=id)
    if not obj:
        raise LotNotFoundException(lot_id=id)

    try:
        return crud.update(db, lot_id=id, lot_in=obj_in)
    except IntegrityError as e:
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate" in error_str:
            raise DuplicateResourceException(
                resource_type="Lot",
                identifier=f"lot_id={id}"
            )
        if "foreign key" in error_str:
            raise ConstraintViolationException(
                message="Invalid reference in update"
            )
        raise DatabaseException(message=f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database operation failed: {str(e)}")


@router.post(
    "/{id}/close",
    response_model=LotInDB,
    summary="Close completed LOT",
    description="Transition a completed LOT to CLOSED status and set closure timestamp",
    responses={404: {"description": "Lot not found"}},
)
def close_lot(
    id: int = Path(..., gt=0, description="Primary key identifier of the LOT"),
    db: Session = Depends(deps.get_db),
) -> LotInDB:
    """Close a completed LOT.

    Transitions a LOT to CLOSED status and sets the closed_at timestamp to
    the current UTC time. This operation typically happens after a LOT has been
    COMPLETED and all quality checks are done. The closed LOT is then archived.

    Status Transition Rules:
    - Any status can transition to CLOSED
    - closed_at timestamp is automatically set to current UTC time
    - updated_at timestamp is also automatically updated

    Args:
        id: Primary key identifier of the LOT to close.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        LotInDB: Updated LOT with CLOSED status and closed_at timestamp set.

    Raises:
        HTTPException: 404 Not Found if LOT does not exist.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Close a completed LOT:
        >>> POST /api/v1/lots/1/close

        Close LOT with ID 42:
        >>> POST /api/v1/lots/42/close

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "status": "CLOSED",
            "closed_at": "2025-11-18T18:45:00",
            "updated_at": "2025-11-18T18:45:00",
            ...
        }
    """
    obj = crud.get(db, lot_id=id)
    if not obj:
        raise LotNotFoundException(lot_id=id)

    try:
        return crud.close_lot(db, lot_id=id)
    except IntegrityError as e:
        raise DatabaseException(message=f"Database integrity error while closing lot: {str(e)}")
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Failed to close Lot: {str(e)}")


@router.put(
    "/{id}/quantities",
    response_model=LotInDB,
    summary="Recalculate LOT quantities",
    description="Recalculate quantities (actual, passed, failed) from associated serials",
    responses={404: {"description": "Lot not found"}},
)
def recalculate_lot_quantities(
    id: int = Path(..., gt=0, description="Primary key identifier of the LOT"),
    db: Session = Depends(deps.get_db),
) -> LotInDB:
    """Recalculate LOT quantities from serials.

    Recalculates actual_quantity, passed_quantity, and failed_quantity by
    counting associated serial records with different statuses. This is typically
    called after bulk serial status updates to synchronize LOT-level metrics.

    Quantities Calculated:
        - actual_quantity: Count of all serials in this LOT
        - passed_quantity: Count of serials with status PASSED
        - failed_quantity: Count of serials with status FAILED
        - defect_rate: Calculated percentage of failed units
        - pass_rate: Calculated percentage of passed units

    Args:
        id: Primary key identifier of the LOT.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        LotInDB: Updated LOT with recalculated quantities and metrics.

    Raises:
        HTTPException: 404 Not Found if LOT does not exist.
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Recalculate quantities for LOT ID 1:
        >>> PUT /api/v1/lots/1/quantities

        Sync after bulk serial updates:
        >>> PUT /api/v1/lots/42/quantities

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "actual_quantity": 95,
            "passed_quantity": 92,
            "failed_quantity": 3,
            "defect_rate": 3.16,
            "pass_rate": 96.84,
            "updated_at": "2025-11-18T15:20:00",
            ...
        }
    """
    obj = crud.get(db, lot_id=id)
    if not obj:
        raise LotNotFoundException(lot_id=id)

    try:
        return crud.update_quantities(db, lot_id=id)
    except IntegrityError as e:
        raise DatabaseException(message=f"Database integrity error while recalculating: {str(e)}")
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Failed to recalculate Lot quantities: {str(e)}")


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete LOT",
    description="Delete an existing LOT (protected by database trigger)",
    responses={
        404: {"description": "Lot not found"},
        409: {"description": "Cannot delete LOT with associated serials"},
    },
)
def delete_lot(
    id: int = Path(..., gt=0, description="Primary key identifier of the LOT"),
    db: Session = Depends(deps.get_db),
):
    """Delete LOT by ID.

    Removes a LOT record from the database. Note: LOT deletion is restricted
    by a database trigger to prevent deletion of LOTs that have associated
    serial records. Delete all related serials first if deletion is required.
    Returns the deleted record for confirmation.

    Args:
        id: Primary key identifier of LOT to delete.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        LotInDB: Deleted LOT record (as it was before deletion).

    Raises:
        HTTPException: 404 Not Found if LOT does not exist.
        HTTPException: 409 Conflict if deletion violates trigger constraints
            (e.g., has associated serials).
        HTTPException: 500 Internal Server Error on unexpected database errors.

    Examples:
        Delete LOT with ID 1:
        >>> DELETE /api/v1/lots/1

        Delete LOT with ID 42:
        >>> DELETE /api/v1/lots/42

    Response Example (200 OK):
        {
            "id": 1,
            "lot_number": "WF-KR-251118D-001",
            "product_model_id": 1,
            ...
        }

    Error Example (409 Conflict):
        If LOT has associated serials, deletion is blocked:
        {
            "detail": "Cannot delete Lot with associated serials"
        }
    """
    obj = crud.get(db, lot_id=id)
    if not obj:
        raise LotNotFoundException(lot_id=id)

    try:
        deleted = crud.delete(db, lot_id=id)
        if not deleted:
            raise LotNotFoundException(lot_id=id)
    except IntegrityError as e:
        error_str = str(e).lower()
        if "foreign key" in error_str or "constraint" in error_str:
            raise ConstraintViolationException(
                message="Cannot delete Lot with associated serials"
            )
        raise DatabaseException(message=f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Failed to delete Lot: {str(e)}")
