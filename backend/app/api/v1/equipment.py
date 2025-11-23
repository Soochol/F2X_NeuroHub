"""FastAPI router for Equipment entity endpoints.

This module provides RESTful API endpoints for managing manufacturing equipment
in the F2X NeuroHub MES system. It implements standard CRUD operations plus
additional query endpoints for filtering equipment by various criteria.

Provides:
    - GET /: List all equipment with pagination
    - GET /{id}: Get equipment by primary key
    - GET /code/{equipment_code}: Get equipment by unique code
    - GET /active: List active equipment
    - GET /type/{equipment_type}: Filter equipment by type
    - GET /production-line/{production_line_id}: Filter by production line
    - GET /process/{process_id}: Filter by process
    - GET /needs-maintenance: Get equipment needing maintenance
    - POST /: Create new equipment
    - PUT /{id}: Update existing equipment
    - DELETE /{id}: Delete equipment

All endpoints include:
    - Comprehensive docstrings with operation descriptions
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
    - Error handling with custom exception responses
    - Dependency injection for database sessions
"""

from typing import List
from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentInDB,
)
from app.services.equipment_service import equipment_service


router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
    responses={
        404: {"description": "Equipment not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)


@router.get(
    "/",
    response_model=List[EquipmentInDB],
    summary="List all equipment",
    description="Retrieve a paginated list of all equipment ordered by equipment code (ascending)",
)
def list_equipment(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[EquipmentInDB]:
    """List all equipment with pagination.

    Retrieves a paginated list of all equipment from the database, ordered by
    equipment_code in ascending order.

    Args:
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[EquipmentInDB]: List of equipment records with database fields.
    """
    return equipment_service.list_equipment(db, skip=skip, limit=limit)


@router.get(
    "/active",
    response_model=List[EquipmentInDB],
    summary="List active equipment",
    description="Retrieve paginated list of active equipment (is_active=True)",
)
def get_active_equipment(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[EquipmentInDB]:
    """Get active equipment with pagination.

    Retrieves only equipment with is_active=True, indicating they are
    currently operational. Results are ordered by equipment_code (ascending).

    Args:
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[EquipmentInDB]: List of active equipment records.
    """
    return equipment_service.get_active_equipment(db, skip=skip, limit=limit)


@router.get(
    "/needs-maintenance",
    response_model=List[EquipmentInDB],
    summary="Get equipment needing maintenance",
    description="Retrieve equipment where next_maintenance_date has passed",
)
def get_equipment_needs_maintenance(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[EquipmentInDB]:
    """Get equipment that needs maintenance.

    Retrieves equipment where next_maintenance_date is in the past or today.
    Results are ordered by next_maintenance_date (ascending, most overdue first).

    Args:
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[EquipmentInDB]: List of equipment needing maintenance.
    """
    return equipment_service.get_equipment_needs_maintenance(db, skip=skip, limit=limit)


@router.get(
    "/type/{equipment_type}",
    response_model=List[EquipmentInDB],
    summary="Filter equipment by type",
    description="Retrieve paginated list of equipment filtered by type",
)
def get_equipment_by_type(
    equipment_type: str = Path(..., min_length=1, description="Equipment type (e.g., LASER_MARKER, SENSOR)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[EquipmentInDB]:
    """Get equipment filtered by type.

    Retrieves all equipment of a specific type (e.g., LASER_MARKER, SENSOR, ROBOT).
    Results are ordered by equipment_code (ascending).

    Args:
        equipment_type: Equipment type to filter by.
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[EquipmentInDB]: List of equipment of the specified type.
    """
    return equipment_service.get_equipment_by_type(db, equipment_type=equipment_type, skip=skip, limit=limit)


@router.get(
    "/production-line/{production_line_id}",
    response_model=List[EquipmentInDB],
    summary="Filter equipment by production line",
    description="Retrieve paginated list of equipment for a specific production line",
)
def get_equipment_by_production_line(
    production_line_id: int = Path(..., gt=0, description="Production line identifier"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[EquipmentInDB]:
    """Get equipment filtered by production line.

    Retrieves all equipment assigned to a specific production line.
    Results are ordered by equipment_code (ascending).

    Args:
        production_line_id: Production line ID to filter by.
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[EquipmentInDB]: List of equipment for the specified production line.
    """
    return equipment_service.get_equipment_by_production_line(
        db, production_line_id=production_line_id, skip=skip, limit=limit
    )


@router.get(
    "/process/{process_id}",
    response_model=List[EquipmentInDB],
    summary="Filter equipment by process",
    description="Retrieve paginated list of equipment for a specific process",
)
def get_equipment_by_process(
    process_id: int = Path(..., gt=0, description="Process identifier"),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[EquipmentInDB]:
    """Get equipment filtered by process.

    Retrieves all equipment used for a specific process.
    Results are ordered by equipment_code (ascending).

    Args:
        process_id: Process ID to filter by.
        skip: Number of records to skip (offset) for pagination.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        List[EquipmentInDB]: List of equipment for the specified process.
    """
    return equipment_service.get_equipment_by_process(db, process_id=process_id, skip=skip, limit=limit)


@router.get(
    "/code/{equipment_code}",
    response_model=EquipmentInDB,
    summary="Get equipment by code",
    description="Retrieve equipment using its unique equipment code",
    responses={404: {"description": "Equipment not found"}},
)
def get_equipment_by_code(
    equipment_code: str = Path(..., min_length=1, description="Unique equipment code identifier"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> EquipmentInDB:
    """Get equipment by unique equipment code.

    Retrieves a single equipment using its unique equipment_code identifier.

    Args:
        equipment_code: Unique equipment identifier (e.g., 'LASER-001').
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        EquipmentInDB: Equipment record with all database fields.

    Raises:
        EquipmentNotFoundException: If equipment does not exist.
    """
    return equipment_service.get_equipment_by_code(db, equipment_code=equipment_code)


@router.get(
    "/{id}",
    response_model=EquipmentInDB,
    summary="Get equipment by ID",
    description="Retrieve a specific equipment using its primary key identifier",
    responses={404: {"description": "Equipment not found"}},
)
def get_equipment(
    id: int = Path(..., gt=0, description="Primary key identifier of the equipment"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> EquipmentInDB:
    """Get equipment by primary key ID.

    Retrieves a single equipment record from the database using its unique
    primary key identifier.

    Args:
        id: Primary key identifier of the equipment to retrieve.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Returns:
        EquipmentInDB: Equipment record with all database fields.

    Raises:
        EquipmentNotFoundException: If equipment does not exist with given ID.
    """
    return equipment_service.get_equipment(db, equipment_id=id)


@router.post(
    "/",
    response_model=EquipmentInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new equipment",
    description="Create new equipment with specified parameters",
)
def create_equipment(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: EquipmentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> EquipmentInDB:
    """Create new equipment.

    Creates a new equipment record with validated data from the request body.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        obj_in: EquipmentCreate schema with validated equipment data.
        current_user: Current authenticated user (injected via dependency).

    Returns:
        EquipmentInDB: Newly created equipment record with all fields.

    Raises:
        ValidationException: If validation fails (invalid references).
        DuplicateResourceException: If duplicate equipment code exists.
    """
    return equipment_service.create_equipment(db, obj_in=obj_in)


@router.put(
    "/{id}",
    response_model=EquipmentInDB,
    summary="Update equipment",
    description="Update existing equipment with new values",
    responses={
        404: {"description": "Equipment not found"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)
def update_equipment(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0, description="Primary key identifier of the equipment"),
    obj_in: EquipmentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> EquipmentInDB:
    """Update existing equipment.

    Updates specific fields in an existing equipment record. All fields are
    optional, supporting partial updates.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        id: Primary key identifier of equipment to update.
        obj_in: EquipmentUpdate schema with field updates.
        current_user: Current authenticated user (injected via dependency).

    Returns:
        EquipmentInDB: Updated equipment record with all fields.

    Raises:
        EquipmentNotFoundException: If equipment does not exist.
        ValidationException: If validation fails (invalid references).
        DuplicateResourceException: If duplicate equipment code exists.
    """
    return equipment_service.update_equipment(db, equipment_id=id, obj_in=obj_in)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete equipment",
    description="Delete an existing equipment",
    responses={
        404: {"description": "Equipment not found"},
        409: {"description": "Cannot delete equipment with associated records"},
    },
)
def delete_equipment(
    id: int = Path(..., gt=0, description="Primary key identifier of the equipment"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete equipment by ID.

    Removes an equipment record from the database.

    Args:
        id: Primary key identifier of equipment to delete.
        db: SQLAlchemy database session (injected via dependency).
        current_user: Current authenticated user (injected via dependency).

    Raises:
        EquipmentNotFoundException: If equipment does not exist.
        ConstraintViolationException: If deletion violates constraints (has associated records).
    """
    equipment_service.delete_equipment(db, equipment_id=id)
