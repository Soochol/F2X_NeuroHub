"""FastAPI router for ProductionLine entity endpoints.

This module provides RESTful API endpoints for managing production lines
in the F2X NeuroHub MES system. It implements standard CRUD operations plus
additional query endpoints for filtering production lines by various criteria.

Provides:
    - GET /: List all production lines with pagination
    - GET /{id}: Get production line by primary key
    - GET /code/{line_code}: Get production line by unique code
    - GET /active: List active production lines
    - GET /capacity-range: Filter production lines by capacity range
    - POST /: Create new production line
    - PUT /{id}: Update existing production line
    - DELETE /{id}: Delete production line

All endpoints include:
    - Comprehensive docstrings with operation descriptions
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
    - Error handling with descriptive HTTPException responses
    - Dependency injection for database sessions
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.crud import production_line as crud
from app.schemas.production_line import (
    ProductionLineCreate,
    ProductionLineUpdate,
    ProductionLineInDB,
    ProductionLineResponse,
)
from app.core.exceptions import (
    ProductionLineNotFoundException,
    DuplicateResourceException,
    ConstraintViolationException,
    ValidationException,
)


router = APIRouter(
    prefix="/production-lines",
    tags=["Production Lines"],
    responses={
        404: {"description": "Production line not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)


@router.get(
    "/",
    response_model=List[ProductionLineInDB],
    summary="List all production lines",
    description="Retrieve a paginated list of all production lines ordered by line code (ascending)",
)
def list_production_lines(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProductionLineInDB]:
    """List all production lines with pagination.

    Retrieves a paginated list of all production lines from the database, ordered by
    line_code in ascending order. Supports configurable offset and limit for pagination.

    Args:
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[ProductionLineInDB]: List of production line records with database fields.
    """
    return crud.get_multi(db, skip=skip, limit=limit)


@router.get(
    "/active",
    response_model=List[ProductionLineInDB],
    summary="List active production lines",
    description="Retrieve paginated list of active production lines (is_active=True)",
)
def get_active_production_lines(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProductionLineInDB]:
    """Get active production lines with pagination.

    Retrieves only production lines with is_active=True, indicating they are
    currently operational. Results are ordered by line_code (ascending).

    Args:
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[ProductionLineInDB]: List of active production line records.
    """
    return crud.get_active(db, skip=skip, limit=limit)


@router.get(
    "/capacity-range",
    response_model=List[ProductionLineInDB],
    summary="Filter production lines by capacity range",
    description="Retrieve production lines within a specified capacity range",
)
def get_production_lines_by_capacity_range(
    min_capacity: int = Query(..., gt=0, description="Minimum capacity per shift (inclusive)"),
    max_capacity: int = Query(..., gt=0, description="Maximum capacity per shift (inclusive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProductionLineInDB]:
    """Get production lines within capacity range.

    Retrieves production lines with capacity_per_shift between min_capacity and
    max_capacity (inclusive). Results are ordered by capacity (descending).

    Args:
        min_capacity: Minimum capacity per shift (inclusive).
        max_capacity: Maximum capacity per shift (inclusive).
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[ProductionLineInDB]: List of production lines within the capacity range.

    Raises:
        HTTPException: 400 if min_capacity > max_capacity.
    """
    if min_capacity > max_capacity:
        raise ValidationException(message="min_capacity must be less than or equal to max_capacity")
    return crud.get_by_capacity_range(
        db, min_capacity=min_capacity, max_capacity=max_capacity, skip=skip, limit=limit
    )


@router.get(
    "/code/{line_code}",
    response_model=ProductionLineInDB,
    summary="Get production line by code",
    description="Retrieve a production line using its unique line code",
    responses={404: {"description": "Production line not found"}},
)
def get_production_line_by_code(
    line_code: str = Path(..., min_length=1, description="Unique line code identifier"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProductionLineInDB:
    """Get production line by unique line code.

    Retrieves a single production line using its unique line_code identifier.

    Args:
        line_code: Unique line identifier (e.g., 'LINE-A').
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        ProductionLineInDB: Production line record with all database fields.

    Raises:
        HTTPException: 404 Not Found if production line does not exist.
    """
    obj = crud.get_by_code(db, line_code=line_code)
    if not obj:
        raise ProductionLineNotFoundException(line_id=line_code)
    return obj


@router.get(
    "/{id}",
    response_model=ProductionLineInDB,
    summary="Get production line by ID",
    description="Retrieve a specific production line using its primary key identifier",
    responses={404: {"description": "Production line not found"}},
)
def get_production_line(
    id: int = Path(..., gt=0, description="Primary key identifier of the production line"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProductionLineInDB:
    """Get production line by primary key ID.

    Retrieves a single production line record from the database using its unique
    primary key identifier.

    Args:
        id: Primary key identifier of the production line to retrieve.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        ProductionLineInDB: Production line record with all database fields.

    Raises:
        HTTPException: 404 Not Found if production line does not exist with given ID.
    """
    obj = crud.get(db, production_line_id=id)
    if not obj:
        raise ProductionLineNotFoundException(line_id=id)
    return obj


@router.post(
    "/",
    response_model=ProductionLineInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new production line",
    description="Create a new production line with specified parameters",
)
def create_production_line(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: ProductionLineCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> ProductionLineInDB:
    """Create new production line.

    Creates a new production line record with validated data from the request body.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        obj_in: ProductionLineCreate schema with validated production line data.
        current_user: Current authenticated user (injected via dependency).

    Returns:
        ProductionLineInDB: Newly created production line record with all fields.

    Raises:
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 409 Conflict if constraint violation occurs (e.g., duplicate line_code).
    """
    # Check if line_code already exists
    existing = crud.get_by_code(db, line_code=obj_in.line_code)
    if existing:
        raise DuplicateResourceException(resource_type="Production line", identifier=f"code='{obj_in.line_code}'")

    try:
        return crud.create(db, production_line_in=obj_in)
    except Exception as e:
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate" in error_str:
            raise DuplicateResourceException(resource_type="Production line", identifier="constraint violation during creation")
        raise


@router.put(
    "/{id}",
    response_model=ProductionLineInDB,
    summary="Update production line",
    description="Update existing production line with new values",
    responses={
        404: {"description": "Production line not found"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)
def update_production_line(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0, description="Primary key identifier of the production line"),
    obj_in: ProductionLineUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> ProductionLineInDB:
    """Update existing production line.

    Updates specific fields in an existing production line record. All fields are
    optional, supporting partial updates.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        id: Primary key identifier of production line to update.
        obj_in: ProductionLineUpdate schema with field updates.
        current_user: Current authenticated user (injected via dependency).

    Returns:
        ProductionLineInDB: Updated production line record with all fields.

    Raises:
        HTTPException: 404 Not Found if production line does not exist.
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 409 Conflict if constraint violation occurs.
    """
    obj = crud.get(db, production_line_id=id)
    if not obj:
        raise ProductionLineNotFoundException(line_id=id)

    # Check if updating line_code to an existing code
    if obj_in.line_code and obj_in.line_code.upper() != obj.line_code:
        existing = crud.get_by_code(db, line_code=obj_in.line_code)
        if existing:
            raise DuplicateResourceException(resource_type="Production line", identifier=f"code='{obj_in.line_code}'")

    try:
        return crud.update(db, production_line_id=id, production_line_in=obj_in)
    except Exception as e:
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate" in error_str:
            raise DuplicateResourceException(resource_type="Production line", identifier="constraint violation during update")
        raise


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete production line",
    description="Delete an existing production line",
    responses={
        404: {"description": "Production line not found"},
        409: {"description": "Cannot delete production line with associated records"},
    },
)
def delete_production_line(
    id: int = Path(..., gt=0, description="Primary key identifier of the production line"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete production line by ID.

    Removes a production line record from the database.

    Args:
        id: Primary key identifier of production line to delete.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Raises:
        HTTPException: 404 Not Found if production line does not exist.
        HTTPException: 409 Conflict if deletion violates constraints (has associated records).
    """
    obj = crud.get(db, production_line_id=id)
    if not obj:
        raise ProductionLineNotFoundException(line_id=id)

    try:
        deleted = crud.delete(db, production_line_id=id)
        if not deleted:
            raise ProductionLineNotFoundException(line_id=id)
    except Exception as e:
        error_str = str(e).lower()
        if "foreign key" in error_str or "constraint" in error_str:
            raise ConstraintViolationException(message="Cannot delete production line with associated records")
        raise
