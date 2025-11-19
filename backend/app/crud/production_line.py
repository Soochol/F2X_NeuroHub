"""
CRUD operations for the ProductionLine entity.

This module implements Create, Read, Update, Delete operations for production line
management in the F2X NeuroHub Manufacturing Execution System. Provides standard CRUD
functions plus specialized queries for retrieving production lines by code, status,
and capacity filters.

Functions:
    get: Get a single production line by ID
    get_multi: Get multiple production lines with pagination
    create: Create a new production line
    update: Update an existing production line
    delete: Delete a production line
    get_by_code: Get production line by unique line code
    get_active: Get active production lines
    get_by_capacity_range: Filter production lines by capacity range
"""

from typing import List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.models.production_line import ProductionLine
from app.schemas.production_line import ProductionLineCreate, ProductionLineUpdate


def get(db: Session, production_line_id: int) -> Optional[ProductionLine]:
    """
    Get a single production line by ID.

    Retrieves a production line record from the database by its primary key.

    Args:
        db: SQLAlchemy database session
        production_line_id: Primary key ID of the production line to retrieve

    Returns:
        ProductionLine instance if found, None otherwise

    Example:
        line = get(db, production_line_id=1)
        if line:
            print(f"Found production line: {line.line_code}")
    """
    return db.query(ProductionLine).filter(ProductionLine.id == production_line_id).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[ProductionLine]:
    """
    Get multiple production lines with pagination.

    Retrieves a list of production lines with support for offset/limit pagination.
    Results are ordered by line_code (ascending).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of ProductionLine instances matching the criteria

    Example:
        # Get first 10 production lines
        lines = get_multi(db, skip=0, limit=10)

        # Get all production lines (with default limit)
        all_lines = get_multi(db)
    """
    return (
        db.query(ProductionLine)
        .order_by(ProductionLine.line_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session,
    production_line_in: ProductionLineCreate,
) -> ProductionLine:
    """
    Create a new production line.

    Creates and saves a new production line record in the database using validated
    Pydantic schema input.

    Args:
        db: SQLAlchemy database session
        production_line_in: ProductionLineCreate schema with validated data

    Returns:
        Created ProductionLine instance with ID and timestamps populated

    Raises:
        IntegrityError: If creation violates unique constraints (line_code)
        SQLAlchemyError: For other database operation errors

    Example:
        line_data = ProductionLineCreate(
            line_code="LINE-A",
            line_name="Assembly Line A",
            capacity_per_shift=500,
            location="Building 1, Zone A"
        )
        new_line = create(db, line_data)
    """
    db_production_line = ProductionLine(
        line_code=production_line_in.line_code,
        line_name=production_line_in.line_name,
        description=production_line_in.description,
        capacity_per_shift=production_line_in.capacity_per_shift,
        location=production_line_in.location,
        is_active=production_line_in.is_active,
    )

    try:
        db.add(db_production_line)
        db.commit()
        db.refresh(db_production_line)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_production_line


def update(
    db: Session,
    production_line_id: int,
    production_line_in: ProductionLineUpdate,
) -> Optional[ProductionLine]:
    """
    Update an existing production line.

    Updates one or more fields of an existing production line. Only provided fields
    (those not None) are updated. The updated_at timestamp is automatically set.

    Args:
        db: SQLAlchemy database session
        production_line_id: ID of the production line to update
        production_line_in: ProductionLineUpdate schema with fields to update

    Returns:
        Updated ProductionLine instance if found and updated, None if not found

    Raises:
        IntegrityError: If update violates unique constraints
        SQLAlchemyError: For other database operation errors

    Example:
        update_data = ProductionLineUpdate(
            capacity_per_shift=600,
            is_active=False
        )
        updated = update(db, production_line_id=1, production_line_in=update_data)
    """
    db_production_line = get(db, production_line_id)
    if not db_production_line:
        return None

    update_data = production_line_in.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(db_production_line, field, value)

        db.commit()
        db.refresh(db_production_line)
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_production_line


def delete(db: Session, production_line_id: int) -> bool:
    """
    Delete a production line.

    Attempts to delete a production line from the database.

    Args:
        db: SQLAlchemy database session
        production_line_id: ID of the production line to delete

    Returns:
        True if production line was deleted, False if not found

    Raises:
        IntegrityError: If deletion violates FK constraints (has dependent records)
        SQLAlchemyError: For other database operation errors

    Example:
        try:
            deleted = delete(db, production_line_id=1)
            if deleted:
                print("Production line deleted successfully")
            else:
                print("Production line not found")
        except IntegrityError:
            print("Cannot delete: Production line has associated records")
    """
    db_production_line = get(db, production_line_id)
    if not db_production_line:
        return False

    try:
        db.delete(db_production_line)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def get_by_code(db: Session, line_code: str) -> Optional[ProductionLine]:
    """
    Get a production line by unique line code.

    Retrieves a single production line by its unique line_code identifier.

    Args:
        db: SQLAlchemy database session
        line_code: Unique line identifier (e.g., 'LINE-A')

    Returns:
        ProductionLine instance if found, None otherwise

    Example:
        line = get_by_code(db, "LINE-A")
        if line:
            print(f"Found production line: {line.line_name}")
    """
    return (
        db.query(ProductionLine)
        .filter(ProductionLine.line_code == line_code.upper())
        .first()
    )


def get_active(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[ProductionLine]:
    """
    Get active production lines.

    Retrieves production lines that are currently operational (is_active=True).
    Results are ordered by line_code (ascending).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of active ProductionLine instances

    Example:
        # Get active production lines
        active_lines = get_active(db)

        # Get first 50 active production lines
        active_lines = get_active(db, skip=0, limit=50)
    """
    return (
        db.query(ProductionLine)
        .filter(ProductionLine.is_active == True)
        .order_by(ProductionLine.line_code.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_capacity_range(
    db: Session,
    min_capacity: int,
    max_capacity: int,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[ProductionLine]:
    """
    Get production lines by capacity range.

    Retrieves production lines with capacity_per_shift between min and max values
    (inclusive). Results are ordered by capacity_per_shift (descending).

    Args:
        db: SQLAlchemy database session
        min_capacity: Minimum capacity per shift (inclusive)
        max_capacity: Maximum capacity per shift (inclusive)
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of ProductionLine instances within the capacity range

    Example:
        # Get production lines with capacity between 400-600 units
        lines = get_by_capacity_range(db, min_capacity=400, max_capacity=600)
    """
    return (
        db.query(ProductionLine)
        .filter(and_(
            ProductionLine.capacity_per_shift >= min_capacity,
            ProductionLine.capacity_per_shift <= max_capacity
        ))
        .order_by(desc(ProductionLine.capacity_per_shift))
        .offset(skip)
        .limit(limit)
        .all()
    )
