"""
CRUD operations for the Equipment entity.

This module implements Create, Read, Update, Delete operations for equipment
management in the F2X NeuroHub Manufacturing Execution System. Provides standard CRUD
functions plus specialized queries for retrieving equipment by code, type, production
line, process, maintenance status, and active status filters.

Functions:
    get: Get a single equipment by ID
    get_multi: Get multiple equipment with pagination
    create: Create a new equipment
    update: Update an existing equipment
    delete: Delete equipment
    get_by_code: Get equipment by unique equipment code
    get_active: Get active equipment
    get_by_type: Get equipment by type
    get_by_production_line: Get equipment by production line
    get_by_process: Get equipment by process
    get_needs_maintenance: Get equipment that needs maintenance
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


def get(db: Session, equipment_id: int) -> Optional[Equipment]:
    """
    Get a single equipment by ID.

    Retrieves an equipment record from the database by its primary key.

    Args:
        db: SQLAlchemy database session
        equipment_id: Primary key ID of the equipment to retrieve

    Returns:
        Equipment instance if found, None otherwise

    Example:
        equipment = get(db, equipment_id=1)
        if equipment:
            print(f"Found equipment: {equipment.equipment_code}")
    """
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """
    Get multiple equipment with pagination.

    Retrieves a list of equipment with support for offset/limit pagination.
    Results are ordered by equipment_code (ascending).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Equipment instances matching the criteria

    Example:
        # Get first 10 equipment
        equipment_list = get_multi(db, skip=0, limit=10)

        # Get all equipment (with default limit)
        all_equipment = get_multi(db)
    """
    return (
        db.query(Equipment)
        .order_by(Equipment.equipment_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session,
    equipment_in: EquipmentCreate,
) -> Equipment:
    """
    Create a new equipment.

    Creates and saves a new equipment record in the database using validated
    Pydantic schema input.

    Args:
        db: SQLAlchemy database session
        equipment_in: EquipmentCreate schema with validated data

    Returns:
        Created Equipment instance with ID and timestamps populated

    Raises:
        IntegrityError: If creation violates unique constraints (equipment_code)
        SQLAlchemyError: For other database operation errors

    Example:
        equipment_data = EquipmentCreate(
            equipment_code="LASER-001",
            equipment_name="Laser Marker 001",
            equipment_type="LASER_MARKER",
            production_line_id=1,
            manufacturer="KEYENCE"
        )
        new_equipment = create(db, equipment_data)
    """
    db_equipment = Equipment(
        equipment_code=equipment_in.equipment_code,
        equipment_name=equipment_in.equipment_name,
        equipment_type=equipment_in.equipment_type,
        process_id=equipment_in.process_id,
        production_line_id=equipment_in.production_line_id,
        location=equipment_in.location,
        manufacturer=equipment_in.manufacturer,
        model_number=equipment_in.model_number,
        serial_number=equipment_in.serial_number,
        install_date=equipment_in.install_date,
        last_maintenance_date=equipment_in.last_maintenance_date,
        next_maintenance_date=equipment_in.next_maintenance_date,
        is_active=equipment_in.is_active,
    )

    try:
        db.add(db_equipment)
        db.commit()
        db.refresh(db_equipment)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_equipment


def update(
    db: Session,
    equipment_id: int,
    equipment_in: EquipmentUpdate,
) -> Optional[Equipment]:
    """
    Update an existing equipment.

    Updates one or more fields of an existing equipment. Only provided fields
    (those not None) are updated. The updated_at timestamp is automatically set.

    Args:
        db: SQLAlchemy database session
        equipment_id: ID of the equipment to update
        equipment_in: EquipmentUpdate schema with fields to update

    Returns:
        Updated Equipment instance if found and updated, None if not found

    Raises:
        IntegrityError: If update violates unique constraints
        SQLAlchemyError: For other database operation errors

    Example:
        update_data = EquipmentUpdate(
            last_maintenance_date=datetime.now(),
            next_maintenance_date=datetime(2025, 6, 1)
        )
        updated = update(db, equipment_id=1, equipment_in=update_data)
    """
    db_equipment = get(db, equipment_id)
    if not db_equipment:
        return None

    update_data = equipment_in.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(db_equipment, field, value)

        db.commit()
        db.refresh(db_equipment)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_equipment


def delete(db: Session, equipment_id: int) -> bool:
    """
    Delete equipment.

    Attempts to delete equipment from the database.

    Args:
        db: SQLAlchemy database session
        equipment_id: ID of the equipment to delete

    Returns:
        True if equipment was deleted, False if not found

    Raises:
        IntegrityError: If deletion violates FK constraints (has dependent records)
        SQLAlchemyError: For other database operation errors

    Example:
        try:
            deleted = delete(db, equipment_id=1)
            if deleted:
                print("Equipment deleted successfully")
            else:
                print("Equipment not found")
        except IntegrityError:
            print("Cannot delete: Equipment has associated records")
    """
    db_equipment = get(db, equipment_id)
    if not db_equipment:
        return False

    try:
        db.delete(db_equipment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_by_code(db: Session, equipment_code: str) -> Optional[Equipment]:
    """
    Get equipment by unique equipment code.

    Retrieves a single equipment by its unique equipment_code identifier.

    Args:
        db: SQLAlchemy database session
        equipment_code: Unique equipment identifier (e.g., 'LASER-001')

    Returns:
        Equipment instance if found, None otherwise

    Example:
        equipment = get_by_code(db, "LASER-001")
        if equipment:
            print(f"Found equipment: {equipment.equipment_name}")
    """
    return (
        db.query(Equipment)
        .filter(Equipment.equipment_code == equipment_code.upper())
        .first()
    )


def get_active(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """
    Get active equipment.

    Retrieves equipment that is currently operational (is_active=True).
    Results are ordered by equipment_code (ascending).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of active Equipment instances

    Example:
        # Get active equipment
        active_equipment = get_active(db)

        # Get first 50 active equipment
        active_equipment = get_active(db, skip=0, limit=50)
    """
    return (
        db.query(Equipment)
        .filter(Equipment.is_active == True)
        .order_by(Equipment.equipment_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_type(
    db: Session,
    equipment_type: str,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """
    Get equipment by type.

    Retrieves all equipment of a specific type (e.g., LASER_MARKER, SENSOR, ROBOT).
    Results are ordered by equipment_code (ascending).

    Args:
        db: SQLAlchemy database session
        equipment_type: Equipment type to filter by
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Equipment instances of the specified type

    Example:
        # Get all laser markers
        lasers = get_by_type(db, equipment_type="LASER_MARKER")
    """
    return (
        db.query(Equipment)
        .filter(Equipment.equipment_type == equipment_type.upper())
        .order_by(Equipment.equipment_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_production_line(
    db: Session,
    production_line_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """
    Get equipment by production line.

    Retrieves all equipment assigned to a specific production line.
    Results are ordered by equipment_code (ascending).

    Args:
        db: SQLAlchemy database session
        production_line_id: Production line ID to filter by
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Equipment instances assigned to the production line

    Example:
        # Get all equipment on LINE-A
        line_equipment = get_by_production_line(db, production_line_id=1)
    """
    return (
        db.query(Equipment)
        .filter(Equipment.production_line_id == production_line_id)
        .order_by(Equipment.equipment_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_process(
    db: Session,
    process_id: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """
    Get equipment by process.

    Retrieves all equipment used for a specific process.
    Results are ordered by equipment_code (ascending).

    Args:
        db: SQLAlchemy database session
        process_id: Process ID to filter by
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Equipment instances used for the process

    Example:
        # Get all equipment for LASER_MARKING process
        process_equipment = get_by_process(db, process_id=1)
    """
    return (
        db.query(Equipment)
        .filter(Equipment.process_id == process_id)
        .order_by(Equipment.equipment_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_needs_maintenance(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """
    Get equipment that needs maintenance.

    Retrieves equipment where next_maintenance_date is in the past or today.
    Results are ordered by next_maintenance_date (ascending, soonest first).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of Equipment instances that need maintenance

    Example:
        # Get equipment needing maintenance
        overdue = get_needs_maintenance(db)
    """
    now = datetime.utcnow()
    return (
        db.query(Equipment)
        .filter(and_(
            Equipment.next_maintenance_date.isnot(None),
            Equipment.next_maintenance_date <= now
        ))
        .order_by(Equipment.next_maintenance_date.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
