"""
CRUD operations for the Alert entity.

This module implements Create, Read, Update, Delete operations for alert management
in the F2X NeuroHub MES system. Provides functions for creating alerts, retrieving
alerts with filters (status, severity, type, date range), and updating alert status.

Functions:
    get: Get a single alert by ID
    get_multi: Get multiple alerts with pagination and filtering
    create: Create a new alert
    update: Update an alert (primarily for status changes)
    delete: Delete an alert
    mark_as_read: Mark a single alert as read
    bulk_mark_as_read: Mark multiple alerts as read
    get_unread_count: Get count of unread alerts
    get_by_status: Get alerts filtered by status
    get_by_severity: Get alerts filtered by severity
    get_by_type: Get alerts filtered by type
    get_by_lot: Get alerts related to a specific LOT
    get_by_serial: Get alerts related to a specific serial
"""

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.models.lot import Lot
from app.models.serial import Serial
from app.models.process import Process
from app.schemas.alert import AlertCreate, AlertUpdate


def get(db: Session, alert_id: int) -> Optional[Alert]:
    """
    Get a single alert by ID.

    Retrieves an alert record with related entities (lot, serial, process)
    eagerly loaded for efficient access.

    Args:
        db: SQLAlchemy database session
        alert_id: Primary key ID of the alert to retrieve

    Returns:
        Alert instance if found, None otherwise

    Example:
        alert = get(db, alert_id=1)
        if alert:
            print(f"Alert: {alert.title}")
    """
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.lot),
            joinedload(Alert.serial),
            joinedload(Alert.process)
        )
        .filter(Alert.id == alert_id)
        .first()
    )


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    lot_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Alert]:
    """
    Get multiple alerts with pagination and filtering.

    Retrieves a paginated list of alerts with optional filters for status,
    severity, type, lot, and date range. Results are ordered by creation
    timestamp (newest first).

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 50)
        status: Optional filter by AlertStatus (UNREAD, READ, ARCHIVED)
        severity: Optional filter by AlertSeverity (HIGH, MEDIUM, LOW)
        alert_type: Optional filter by AlertType
        lot_id: Optional filter by related LOT ID
        start_date: Optional filter by creation date (from)
        end_date: Optional filter by creation date (to)

    Returns:
        List of Alert instances matching the criteria

    Example:
        # Get unread high-severity alerts
        alerts = get_multi(
            db,
            skip=0,
            limit=10,
            status=AlertStatus.UNREAD,
            severity=AlertSeverity.HIGH
        )

        # Get alerts for a specific date range
        from datetime import date
        alerts = get_multi(
            db,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
    """
    query = db.query(Alert).options(
        joinedload(Alert.lot),
        joinedload(Alert.serial),
        joinedload(Alert.process)
    )

    # Apply filters
    if status is not None:
        query = query.filter(Alert.status == status)

    if severity is not None:
        query = query.filter(Alert.severity == severity)

    if alert_type is not None:
        query = query.filter(Alert.alert_type == alert_type)

    if lot_id is not None:
        query = query.filter(Alert.lot_id == lot_id)

    if start_date is not None:
        query = query.filter(Alert.created_at >= start_date)

    if end_date is not None:
        # Include the entire end_date day
        query = query.filter(Alert.created_at < datetime.combine(end_date, datetime.max.time()))

    # Order by creation timestamp (newest first)
    return (
        query
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session,
    alert_in: AlertCreate,
) -> Alert:
    """
    Create a new alert.

    Creates and saves a new alert record in the database. Alerts are created
    automatically by the system (defect detection, process delays) or manually
    by users.

    Args:
        db: SQLAlchemy database session
        alert_in: AlertCreate schema with alert data

    Returns:
        Created Alert instance with ID and timestamps populated

    Raises:
        SQLAlchemyError: For database operation errors

    Example:
        from app.schemas.alert import AlertCreate, AlertType, AlertSeverity

        alert_data = AlertCreate(
            alert_type=AlertType.DEFECT_DETECTED,
            severity=AlertSeverity.HIGH,
            title="불량 발생",
            message="LOT WF-KR-251118D-001, 공정 3에서 불량 발생",
            lot_id=1,
            serial_id=5,
            process_id=3,
            equipment_id="SENSOR-CHECK-01"
        )
        new_alert = create(db, alert_data)
    """
    db_alert = Alert(
        alert_type=alert_in.alert_type,
        severity=alert_in.severity,
        status=AlertStatus.UNREAD,  # Always start as UNREAD
        title=alert_in.title,
        message=alert_in.message,
        lot_id=alert_in.lot_id,
        serial_id=alert_in.serial_id,
        process_id=alert_in.process_id,
        equipment_id=alert_in.equipment_id,
        created_by_id=alert_in.created_by_id,
        created_at=datetime.utcnow(),
    )

    try:
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_alert


def update(
    db: Session,
    alert_id: int,
    alert_in: AlertUpdate,
) -> Optional[Alert]:
    """
    Update an alert.

    Updates alert status and tracking fields (read_by_id, archived_by_id).
    Primarily used for marking alerts as read or archived.

    Args:
        db: SQLAlchemy database session
        alert_id: ID of the alert to update
        alert_in: AlertUpdate schema with fields to update

    Returns:
        Updated Alert instance if found, None if not found

    Raises:
        SQLAlchemyError: For database operation errors

    Example:
        alert_update = AlertUpdate(
            status=AlertStatus.READ,
            read_by_id=1
        )
        updated = update(db, alert_id=5, alert_in=alert_update)
    """
    db_alert = get(db, alert_id)
    if not db_alert:
        return None

    update_data = alert_in.model_dump(exclude_unset=True)

    try:
        for field, value in update_data.items():
            setattr(db_alert, field, value)

        # Set timestamps based on status change
        if "status" in update_data:
            if update_data["status"] == AlertStatus.READ and db_alert.read_at is None:
                db_alert.read_at = datetime.utcnow()
            elif update_data["status"] == AlertStatus.ARCHIVED and db_alert.archived_at is None:
                db_alert.archived_at = datetime.utcnow()

        db.commit()
        db.refresh(db_alert)
    except SQLAlchemyError:
        db.rollback()
        raise

    return db_alert


def delete(db: Session, alert_id: int) -> bool:
    """
    Delete an alert.

    Permanently deletes an alert from the database. Consider archiving
    instead of deleting for audit compliance.

    Args:
        db: SQLAlchemy database session
        alert_id: ID of the alert to delete

    Returns:
        True if alert was deleted, False if not found

    Raises:
        SQLAlchemyError: For database operation errors

    Example:
        deleted = delete(db, alert_id=1)
        if deleted:
            print("Alert deleted successfully")
    """
    db_alert = get(db, alert_id)
    if not db_alert:
        return False

    try:
        db.delete(db_alert)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def mark_as_read(
    db: Session,
    alert_id: int,
    read_by_id: int
) -> Optional[Alert]:
    """
    Mark a single alert as read.

    Updates alert status to READ and sets read_at timestamp and read_by_id.

    Args:
        db: SQLAlchemy database session
        alert_id: ID of the alert to mark as read
        read_by_id: ID of the user marking the alert as read

    Returns:
        Updated Alert instance if found, None if not found

    Example:
        alert = mark_as_read(db, alert_id=5, read_by_id=1)
        if alert:
            print(f"Alert {alert.id} marked as read")
    """
    db_alert = get(db, alert_id)
    if not db_alert:
        return None

    # Only update if currently UNREAD
    if db_alert.status == AlertStatus.UNREAD:
        try:
            db_alert.status = AlertStatus.READ
            db_alert.read_by_id = read_by_id
            db_alert.read_at = datetime.utcnow()

            db.commit()
            db.refresh(db_alert)
        except SQLAlchemyError:
            db.rollback()
            raise

    return db_alert


def bulk_mark_as_read(
    db: Session,
    alert_ids: List[int],
    read_by_id: int
) -> int:
    """
    Mark multiple alerts as read in bulk.

    Updates multiple alerts to READ status in a single transaction.
    More efficient than calling mark_as_read multiple times.

    Args:
        db: SQLAlchemy database session
        alert_ids: List of alert IDs to mark as read
        read_by_id: ID of the user marking the alerts as read

    Returns:
        Number of alerts successfully marked as read

    Raises:
        SQLAlchemyError: For database operation errors

    Example:
        count = bulk_mark_as_read(
            db,
            alert_ids=[1, 2, 3, 4, 5],
            read_by_id=1
        )
        print(f"Marked {count} alerts as read")
    """
    try:
        updated_count = (
            db.query(Alert)
            .filter(
                and_(
                    Alert.id.in_(alert_ids),
                    Alert.status == AlertStatus.UNREAD
                )
            )
            .update(
                {
                    Alert.status: AlertStatus.READ,
                    Alert.read_by_id: read_by_id,
                    Alert.read_at: datetime.utcnow()
                },
                synchronize_session=False
            )
        )

        db.commit()
        return updated_count

    except SQLAlchemyError:
        db.rollback()
        raise


def get_unread_count(db: Session) -> int:
    """
    Get count of unread alerts.

    Returns the total number of alerts with UNREAD status.
    Useful for displaying notification badges.

    Args:
        db: SQLAlchemy database session

    Returns:
        Count of unread alerts

    Example:
        count = get_unread_count(db)
        print(f"You have {count} unread alerts")
    """
    return (
        db.query(func.count(Alert.id))
        .filter(Alert.status == AlertStatus.UNREAD)
        .scalar() or 0
    )


def get_by_status(
    db: Session,
    status: AlertStatus,
    *,
    skip: int = 0,
    limit: int = 50,
) -> List[Alert]:
    """
    Get alerts filtered by status.

    Args:
        db: SQLAlchemy database session
        status: AlertStatus to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Alert instances with specified status

    Example:
        unread_alerts = get_by_status(db, AlertStatus.UNREAD)
    """
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.lot),
            joinedload(Alert.serial),
            joinedload(Alert.process)
        )
        .filter(Alert.status == status)
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_severity(
    db: Session,
    severity: AlertSeverity,
    *,
    skip: int = 0,
    limit: int = 50,
) -> List[Alert]:
    """
    Get alerts filtered by severity.

    Args:
        db: SQLAlchemy database session
        severity: AlertSeverity to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Alert instances with specified severity

    Example:
        high_alerts = get_by_severity(db, AlertSeverity.HIGH)
    """
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.lot),
            joinedload(Alert.serial),
            joinedload(Alert.process)
        )
        .filter(Alert.severity == severity)
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_type(
    db: Session,
    alert_type: AlertType,
    *,
    skip: int = 0,
    limit: int = 50,
) -> List[Alert]:
    """
    Get alerts filtered by type.

    Args:
        db: SQLAlchemy database session
        alert_type: AlertType to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Alert instances with specified type

    Example:
        defect_alerts = get_by_type(db, AlertType.DEFECT_DETECTED)
    """
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.lot),
            joinedload(Alert.serial),
            joinedload(Alert.process)
        )
        .filter(Alert.alert_type == alert_type)
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_lot(
    db: Session,
    lot_id: int,
    *,
    skip: int = 0,
    limit: int = 50,
) -> List[Alert]:
    """
    Get alerts related to a specific LOT.

    Args:
        db: SQLAlchemy database session
        lot_id: LOT ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Alert instances related to the specified LOT

    Example:
        lot_alerts = get_by_lot(db, lot_id=1)
    """
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.lot),
            joinedload(Alert.serial),
            joinedload(Alert.process)
        )
        .filter(Alert.lot_id == lot_id)
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_serial(
    db: Session,
    serial_id: int,
    *,
    skip: int = 0,
    limit: int = 50,
) -> List[Alert]:
    """
    Get alerts related to a specific serial.

    Args:
        db: SQLAlchemy database session
        serial_id: Serial ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Alert instances related to the specified serial

    Example:
        serial_alerts = get_by_serial(db, serial_id=5)
    """
    return (
        db.query(Alert)
        .options(
            joinedload(Alert.lot),
            joinedload(Alert.serial),
            joinedload(Alert.process)
        )
        .filter(Alert.serial_id == serial_id)
        .order_by(desc(Alert.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
