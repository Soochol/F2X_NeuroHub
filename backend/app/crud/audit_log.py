"""
CRUD operations for the AuditLog entity (READ-ONLY).

This module implements read-only operations for audit logs in the F2X NeuroHub
system. Audit logs are immutable records created automatically by database triggers
and cannot be modified or deleted through the application layer.

The audit_logs table is partitioned monthly by created_at using RANGE partitioning
with partition names following the format: audit_logs_yYYYYmMM (e.g., audit_logs_y2025m11).

IMPORTANT: This module contains ONLY read operations (get, get_multi, and specialized
queries). No create, update, or delete functions are provided because:

1. Audit logs are automatically created by database triggers when data changes
2. Audit logs are immutable - modification is prevented by database-level constraints
3. The database trigger prevent_audit_modification() explicitly prevents UPDATE/DELETE
4. Application-level functions for audit creation would violate audit integrity
5. Compliance and security requirements mandate immutable audit trails

Database Enforcement:
    - CREATE trigger prevent_audit_modification() prevents all UPDATE/DELETE operations
    - CHECK constraint chk_audit_logs_old_values ensures old_values logic
    - CHECK constraint chk_audit_logs_new_values ensures new_values logic
    - FK constraint fk_audit_logs_user with RESTRICT prevents orphaned audit records

Functions:
    get: Get a single audit log by ID
    get_multi: Get multiple audit logs with pagination (most recent first)
    get_by_entity: Filter audit logs by entity type and ID
    get_by_user: Filter audit logs by user who performed the action
    get_by_action: Filter audit logs by action type (CREATE/UPDATE/DELETE)
    get_by_date_range: Filter audit logs by date range
    get_entity_history: Get complete change history for a specific entity
    get_user_activity: Get activity log for a specific user
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog, AuditAction


def get(db: Session, id: int) -> Optional[AuditLog]:
    """
    Get a single audit log entry by ID.

    Retrieves an immutable audit log record from the database by its primary key.
    This is the basic lookup operation for individual audit entries.

    Args:
        db: SQLAlchemy database session
        id: Primary key ID of the audit log entry to retrieve

    Returns:
        AuditLog instance if found, None otherwise

    Example:
        >>> audit_log = get(db, id=42)
        >>> if audit_log:
        ...     print(f"Action: {audit_log.action} on {audit_log.entity_type}")
    """
    return db.query(AuditLog).filter(AuditLog.id == id).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get multiple audit log entries with pagination (most recent first).

    Retrieves a list of audit logs ordered by creation timestamp in descending
    order (most recent first). Supports offset/limit pagination for efficient
    retrieval of large audit datasets.

    Args:
        db: SQLAlchemy database session
        skip: Number of records to skip (offset for pagination, default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)

    Returns:
        List of AuditLog instances ordered by created_at descending

    Example:
        >>> # Get the 10 most recent audit logs
        >>> recent_logs = get_multi(db, skip=0, limit=10)
        >>> for log in recent_logs:
        ...     print(f"{log.created_at}: {log.action} by user {log.user_id}")

        >>> # Get the next 10 (pagination)
        >>> next_logs = get_multi(db, skip=10, limit=10)
    """
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_entity(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get audit logs for a specific entity type and ID.

    Filters audit logs by entity type (e.g., 'lots', 'serials', 'product_models')
    and entity ID to retrieve all actions performed on a specific record.
    Results are ordered by creation time descending (most recent first).

    Args:
        db: SQLAlchemy database session
        entity_type: Type of entity being audited (e.g., 'lots', 'serials')
        entity_id: Primary key of the specific entity record
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of AuditLog instances for the specified entity, ordered by created_at desc

    Example:
        >>> # Get all actions on lot ID 123
        >>> logs = get_by_entity(db, entity_type="lots", entity_id=123)
        >>> for log in logs:
        ...     print(f"{log.created_at}: {log.action}")

        >>> # Get actions on a specific serial
        >>> serial_logs = get_by_entity(
        ...     db,
        ...     entity_type="serials",
        ...     entity_id=456,
        ...     skip=0,
        ...     limit=50
        ... )
    """
    return (
        db.query(AuditLog)
        .filter(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
        )
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_user(
    db: Session,
    *,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get audit logs for actions performed by a specific user.

    Filters audit logs by the user_id of who performed the action. Useful for
    tracking user activity, accountability, and security analysis. Results are
    ordered by creation time descending (most recent first).

    Args:
        db: SQLAlchemy database session
        user_id: ID of the user who performed the actions
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of AuditLog instances for the specified user, ordered by created_at desc

    Example:
        >>> # Get all actions performed by user 5
        >>> user_logs = get_by_user(db, user_id=5)
        >>> for log in user_logs:
        ...     print(f"{log.created_at}: {log.action} on {log.entity_type}#{log.entity_id}")

        >>> # Get user's actions with pagination
        >>> page_1 = get_by_user(db, user_id=5, skip=0, limit=50)
        >>> page_2 = get_by_user(db, user_id=5, skip=50, limit=50)
    """
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_action(
    db: Session,
    *,
    action: str,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get audit logs filtered by action type.

    Filters audit logs by the type of operation performed: CREATE (new record),
    UPDATE (record modification), or DELETE (record removal). Useful for analyzing
    specific types of changes in the system. Results ordered by creation time
    descending (most recent first).

    Args:
        db: SQLAlchemy database session
        action: Type of action to filter: 'CREATE', 'UPDATE', or 'DELETE'
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of AuditLog instances matching the action type, ordered by created_at desc

    Raises:
        ValueError: If action is not one of the valid AuditAction values

    Example:
        >>> # Get all CREATE operations
        >>> creations = get_by_action(db, action="CREATE")
        >>> print(f"Total new records created: {len(creations)}")

        >>> # Get all DELETE operations
        >>> deletions = get_by_action(db, action="DELETE", limit=50)
        >>> for log in deletions:
        ...     print(f"Deleted {log.entity_type}#{log.entity_id} at {log.created_at}")

        >>> # Get all UPDATE operations
        >>> updates = get_by_action(db, action="UPDATE")
    """
    # Validate action is a valid AuditAction
    valid_actions = {action_enum.value for action_enum in AuditAction}
    if action not in valid_actions:
        raise ValueError(
            f"Invalid action '{action}'. Must be one of: {', '.join(valid_actions)}"
        )

    return (
        db.query(AuditLog)
        .filter(AuditLog.action == action)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_date_range(
    db: Session,
    *,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get audit logs within a specific date range.

    Filters audit logs by creation timestamp, returning all logs created between
    start_date (inclusive) and end_date (inclusive). Useful for compliance reports,
    incident investigation, and auditing specific time periods. Results ordered
    by creation time descending (most recent first).

    Args:
        db: SQLAlchemy database session
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of AuditLog instances within the date range, ordered by created_at desc

    Example:
        >>> from datetime import datetime, timedelta
        >>> # Get logs from the last 7 days
        >>> today = datetime.now(timezone.utc)
        >>> week_ago = today - timedelta(days=7)
        >>> week_logs = get_by_date_range(db, start_date=week_ago, end_date=today)

        >>> # Get logs for a specific day
        >>> target_date = datetime(2025, 11, 18, tzinfo=timezone.utc)
        >>> next_day = target_date + timedelta(days=1)
        >>> day_logs = get_by_date_range(
        ...     db,
        ...     start_date=target_date,
        ...     end_date=next_day
        ... )
    """
    return (
        db.query(AuditLog)
        .filter(
            and_(
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date,
            )
        )
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_entity_history(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get the complete change history for a specific entity.

    Retrieves all audit log entries documenting every change made to a specific
    entity record (identified by entity_type and entity_id). This provides a
    comprehensive audit trail showing CREATE, UPDATE, and DELETE operations in
    chronological order. Useful for understanding the full lifecycle of any
    record in the system.

    Results are ordered by creation time descending (most recent first), allowing
    easy visualization of the change history from most recent backwards.

    Args:
        db: SQLAlchemy database session
        entity_type: Type of entity being audited (e.g., 'lots', 'serials', 'product_models')
        entity_id: Primary key of the entity
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of AuditLog instances representing the complete history for the entity,
        ordered by created_at descending (most recent first)

    Example:
        >>> # Get complete history of lot ID 123
        >>> history = get_entity_history(db, entity_type="lots", entity_id=123)
        >>> for log in history:
        ...     action = log.action
        ...     timestamp = log.created_at
        ...     user = log.user.username if log.user else "Unknown"
        ...     print(f"{timestamp} - {action} by {user}")

        >>> # Get history for a serial with pagination
        >>> serial_history = get_entity_history(
        ...     db,
        ...     entity_type="serials",
        ...     entity_id=456,
        ...     skip=0,
        ...     limit=50
        ... )

        >>> # Analyze what changed in the last update
        >>> if serial_history and serial_history[0].is_update:
        ...     last_update = serial_history[0]
        ...     changed_fields = last_update.get_changed_fields()
        ...     print(f"Fields changed: {changed_fields}")
    """
    return (
        db.query(AuditLog)
        .filter(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
        )
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_activity(
    db: Session,
    *,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[AuditLog]:
    """
    Get the activity log for a specific user.

    Retrieves all audit log entries documenting every action (CREATE, UPDATE, DELETE)
    performed by a specific user. Useful for user accountability, tracking user
    behavior, and security auditing. Results are ordered by creation time descending
    (most recent first).

    This function is semantically equivalent to get_by_user() but with naming that
    emphasizes the "activity log" aspect for user-focused queries.

    Args:
        db: SQLAlchemy database session
        user_id: ID of the user whose activity should be retrieved
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)

    Returns:
        List of AuditLog instances representing all actions by the user,
        ordered by created_at descending (most recent first)

    Example:
        >>> # Get complete activity log for user 5
        >>> activity = get_user_activity(db, user_id=5)
        >>> for log in activity:
        ...     print(f"{log.created_at}: {log.action} on {log.entity_type}#{log.entity_id}")

        >>> # Get user's recent activity (last 25 actions)
        >>> recent = get_user_activity(db, user_id=5, skip=0, limit=25)
        >>> for log in recent:
        ...     if log.is_delete:
        ...         print(f"WARNING: User deleted {log.entity_type} at {log.created_at}")

        >>> # Get user's activity for a specific time period
        >>> from datetime import datetime, timedelta, timezone
        >>> today = datetime.now(timezone.utc)
        >>> yesterday = today - timedelta(days=1)
        >>> user_activity = get_user_activity(db, user_id=5, limit=100)
        >>> recent_activity = [
        ...     log for log in user_activity
        ...     if yesterday <= log.created_at <= today
        ... ]
    """
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
