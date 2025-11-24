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
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.schemas.lot import (
    LotCreate,
    LotUpdate,
    LotInDB,
    LotStatus,
)
from app.schemas.wip_item import WIPItemInDB
from app.services.lot_service import lot_service


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
    status: Optional[str] = Query(None, description="Filter by LOT status (CREATED, IN_PROGRESS, COMPLETED, CLOSED)"),
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
    """
    # Convert empty string to None, validate non-empty strings
    status_enum: Optional[LotStatus] = None
    if status and status.strip():
        try:
            status_enum = LotStatus(status.upper())
        except ValueError:
            from app.exceptions import ValidationException
            raise ValidationException(
                message=f"Invalid status value: '{status}'. Must be one of: CREATED, IN_PROGRESS, COMPLETED, CLOSED",
                details={"field": "status", "value": status, "allowed_values": [s.value for s in LotStatus]}
            )
    
    return lot_service.get_lots(db, skip=skip, limit=limit, status=status_enum)


@router.get(
    "/number/{lot_number}",
    response_model=LotInDB,
    summary="Get LOT by LOT number",
    description="Retrieve a LOT using its unique LOT number (11 characters)",
    responses={404: {"description": "Lot not found"}},
)
def get_lot_by_number(
    lot_number: str = Path(..., pattern=r"^[A-Z0-9]{10,15}$", description="Unique LOT identifier"),
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
        LotNotFoundException: 404 Not Found if LOT does not exist with given number.
    """
    return lot_service.get_lot_by_number(db, lot_number=lot_number)


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
    """
    return lot_service.get_active_lots(db, skip=skip, limit=limit)


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
    """
    return lot_service.get_lots_by_date_range(db, start_date=start_date, end_date=end_date, skip=skip, limit=limit)


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
    """
    return lot_service.get_lots_by_product_model(db, product_model_id=product_model_id, skip=skip, limit=limit)


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
    """
    return lot_service.get_lots_by_status(db, status=status, skip=skip, limit=limit)


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
        LotNotFoundException: 404 Not Found if LOT does not exist with given ID.
    """
    return lot_service.get_lot(db, lot_id=id)


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
        LotNotFoundException: 404 Not Found if LOT does not exist.
    """
    return lot_service.get_lot(db, lot_id=id)


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
            Required: product_model_id, production_date, target_quantity
            Optional: status (defaults to CREATED)

    Returns:
        LotInDB: Newly created LOT record with all fields including
            database-generated lot_number, ID, and timestamps.

    Raises:
        ValidationException: 400 Bad Request if validation fails.
        DuplicateResourceException: 409 Conflict if constraint violation occurs.
        DatabaseException: 500 Internal Server Error on unexpected database errors.
    """
    return lot_service.create_lot(db, lot_in=obj_in)


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
        BR-001: LOT must be in CREATED or IN_PROGRESS status
        BR-002: WIP generation transitions LOT to IN_PROGRESS

    Args:
        id: LOT identifier
        quantity: Number of WIP IDs (1-100)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of created WIP items

    Raises:
        LotNotFoundException: 404 if LOT not found
        WIPValidationError: 400 if validation fails
    """
    return lot_service.start_wip_generation(db, lot_id=id, quantity=quantity, current_user=current_user)


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
        LotNotFoundException: 404 Not Found if LOT does not exist.
        ValidationException: 400 Bad Request if validation fails.
        DuplicateResourceException: 409 Conflict if constraint violation occurs.
        DatabaseException: 500 Internal Server Error on unexpected database errors.
    """
    return lot_service.update_lot(db, lot_id=id, lot_in=obj_in)
