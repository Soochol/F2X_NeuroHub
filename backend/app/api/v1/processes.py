"""FastAPI router for Process entity endpoints.

This module provides RESTful API endpoints for managing manufacturing processes
in the F2X NeuroHub MES system. It implements standard CRUD operations plus
additional specialized query endpoints for retrieving processes by unique
identifiers and in specific sequences.

Provides:
    - GET /: List all processes with pagination
    - GET /{id}: Get process by primary key
    - GET /number/{process_number}: Get process by process number (1-100)
    - GET /code/{process_code}: Get process by unique process code
    - GET /active: List active processes ordered by sort_order
    - GET /sequence: Get all processes in sequential order (1-100)
    - POST /: Create new process
    - PUT /{id}: Update existing process
    - DELETE /{id}: Delete process (deletion protected by database trigger)

All endpoints include:
    - Comprehensive docstrings with operation descriptions
    - Pydantic schema validation for request/response
    - OpenAPI documentation metadata
    - Proper HTTP status codes
    - Error handling with descriptive HTTPException responses
    - Dependency injection for database sessions
"""

from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.schemas.process import (
    ProcessCreate,
    ProcessUpdate,
    ProcessInDB,
)
from app.services.process_service import process_service


router = APIRouter(
    prefix="/processes",
    tags=["Processes"],
    responses={
        404: {"description": "Process not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., duplicate process number or code)"},
        423: {"description": "Process deletion locked (has dependent data)"},
    },
)


@router.get(
    "/",
    response_model=List[ProcessInDB],
    summary="List all processes",
    description="Retrieve a paginated list of all manufacturing processes ordered by sort_order",
)
def list_processes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProcessInDB]:
    """List all manufacturing processes with pagination.

    Retrieves a paginated list of all processes from the database, ordered
    by sort_order for consistent UI display. Supports configurable offset
    and limit for pagination control.

    Args:
        skip: Number of records to skip (offset) for pagination.
            Defaults to 0. Must be non-negative.
        limit: Maximum number of records to return.
            Defaults to 100. Must be positive (1-100).
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[ProcessInDB]: List of process records with database fields.
            Empty list if no records match criteria.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.
    """
    return process_service.list_processes(db, skip=skip, limit=limit)


@router.get(
    "/number/{process_number}",
    response_model=ProcessInDB,
    summary="Get process by process number",
    description="Retrieve a specific process using its unique sequence number (1-8)",
    responses={404: {"description": "Process not found"}},
)
def get_process_by_number(
    process_number: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessInDB:
    """Get process by unique process number.

    Retrieves a process using its unique sequence number in the manufacturing
    workflow (1-100). Each process has exactly one process_number that defines
    its position in the production sequence.

    Args:
        process_number: Process sequence number (1-100).
            Defines the position of the process in the manufacturing workflow.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        ProcessInDB: Process record with all database fields.

    Raises:
        HTTPException: 404 Not Found if process does not exist with given number.
    """
    return process_service.get_process_by_number(db, process_number=process_number)


@router.get(
    "/code/{process_code}",
    response_model=ProcessInDB,
    summary="Get process by process code",
    description="Retrieve a specific process using its unique code identifier",
    responses={404: {"description": "Process not found"}},
)
def get_process_by_code(
    process_code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessInDB:
    """Get process by unique process code.

    Retrieves a process using its globally unique code identifier
    (e.g., "LASER_MARKING"). Process codes are case-insensitive but stored
    in uppercase and provide an alternative way to retrieve processes.

    Args:
        process_code: Unique process code identifier (e.g., "LASER_MARKING").
            Will be converted to uppercase. Must be 1-50 characters.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        ProcessInDB: Process record with all database fields.

    Raises:
        HTTPException: 404 Not Found if process does not exist with given code.
    """
    return process_service.get_process_by_code(db, process_code=process_code)


@router.get(
    "/active",
    response_model=List[ProcessInDB],
    summary="List active processes",
    description="Retrieve list of all active processes ordered by sort_order",
)
def get_active_processes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProcessInDB]:
    """Get all active processes ordered by sort_order.

    Retrieves all processes where is_active is True, ordered by sort_order
    for proper display sequence in the UI. Useful for populating dropdowns
    and process selection interfaces in the manufacturing workflow.

    Args:
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[ProcessInDB]: List of active process records ordered by sort_order.
            Empty list if no active processes exist.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.
    """
    return process_service.get_active_processes(db)


@router.get(
    "/sequence",
    response_model=List[ProcessInDB],
    summary="Get manufacturing process sequence",
    description="Retrieve all 8 manufacturing processes in sequential order (1-8)",
)
def get_process_sequence(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[ProcessInDB]:
    """Get all 8 manufacturing processes in sequential order (1-8).

    Retrieves all active processes ordered by process_number to display
    the complete manufacturing workflow sequence. Returns processes representing
    the full production line when all are active.

    This endpoint is essential for workflow visualization, process chain
    management, and understanding the complete production sequence from
    start to finish.

    Args:
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        List[ProcessInDB]: List of process records ordered by process_number (1-8).
            Expected to return up to 8 processes (one for each sequence position).
            May return fewer if some processes are inactive.

    Raises:
        HTTPException: May raise 500 Internal Server Error on unexpected database errors.
    """
    return process_service.get_process_sequence(db)


@router.get(
    "/{id}",
    response_model=ProcessInDB,
    summary="Get process by ID",
    description="Retrieve a specific process using its primary key identifier",
    responses={404: {"description": "Process not found"}},
)
def get_process(
    id: int = Path(..., gt=0, description="Primary key identifier of the process"),
    db: Session = Depends(deps.get_db),
) -> ProcessInDB:
    """Get process by primary key ID.

    Retrieves a single process record from the database using its unique
    primary key identifier.

    Args:
        id: Primary key identifier of the process to retrieve.
            Must be a positive integer.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        ProcessInDB: Process record with all database fields.

    Raises:
        HTTPException: 404 Not Found if process does not exist with given ID.
    """
    return process_service.get_process(db, process_id=id)


@router.post(
    "/",
    response_model=ProcessInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new process",
    description="Create a new manufacturing process with provided specifications",
    responses={409: {"description": "Process number or code already exists"}},
)
def create_process(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: ProcessCreate,
) -> ProcessInDB:
    """Create new manufacturing process.

    Creates a new Process record with validated data from the request body.
    The process_number (1-8) and process_code must be globally unique;
    duplicate values will result in a 409 Conflict error. Database-generated
    fields (id, created_at, updated_at) are automatically populated.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        obj_in: ProcessCreate schema with validated process data.
            Required: process_number (1-8), process_code, process_name_ko,
                     process_name_en, sort_order.
            Optional: description, estimated_duration_seconds, quality_criteria, is_active.

    Returns:
        ProcessInDB: Newly created process record with all fields
            including database-generated values.

    Raises:
        HTTPException: 409 Conflict if process_number or process_code already exists.
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 500 Internal Server Error on unexpected database errors.
    """
    return process_service.create_process(db, obj_in=obj_in)


@router.put(
    "/{id}",
    response_model=ProcessInDB,
    summary="Update process",
    description="Update existing process with new values",
    responses={
        404: {"description": "Process not found"},
        409: {"description": "Conflict (e.g., duplicate process number or code)"},
    },
)
def update_process(
    *,
    db: Session = Depends(deps.get_db),
    id: int = Path(..., gt=0, description="Primary key identifier of process to update"),
    obj_in: ProcessUpdate,
) -> ProcessInDB:
    """Update existing manufacturing process.

    Updates specific fields in an existing Process record. All fields are
    optional, supporting partial updates. Only provided fields are modified;
    unspecified fields retain their current values. Note: process_number and
    process_code are unique identifiers - updating these requires careful
    coordination to avoid constraint violations.

    Args:
        db: SQLAlchemy database session (injected via dependency).
        id: Primary key identifier of process to update.
        obj_in: ProcessUpdate schema with field updates.
            All fields are optional. Only provided fields are updated.

    Returns:
        ProcessInDB: Updated process record with all fields.

    Raises:
        HTTPException: 404 Not Found if process does not exist.
        HTTPException: 409 Conflict if update violates unique constraints.
        HTTPException: 400 Bad Request if validation fails.
        HTTPException: 500 Internal Server Error on unexpected database errors.
    """
    return process_service.update_process(db, process_id=id, obj_in=obj_in)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete process",
    description="Delete an existing manufacturing process",
    responses={
        204: {"description": "Process deleted successfully"},
        404: {"description": "Process not found"},
        423: {"description": "Process deletion locked (has dependent data)"},
    },
)
def delete_process(
    id: int = Path(..., gt=0, description="Primary key identifier of process to delete"),
    db: Session = Depends(deps.get_db),
) -> None:
    """Delete manufacturing process by ID.

    Removes a Process record from the database. Returns the deleted record
    for confirmation. Note: Process deletion is protected by a database trigger
    to prevent deletion of processes that have associated lot_processes data.
    If the process has dependent records, deletion will fail with a constraint
    violation error (423 Locked).

    Args:
        id: Primary key identifier of process to delete.
        db: SQLAlchemy database session (injected via dependency).

    Returns:
        ProcessInDB: Deleted process record (as it was before deletion).

    Raises:
        HTTPException: 404 Not Found if process does not exist.
        HTTPException: 423 Locked if deletion violates foreign key constraint
                       (has dependent lot_processes data).
        HTTPException: 500 Internal Server Error on unexpected database errors.
    """
    process_service.delete_process(db, process_id=id)
