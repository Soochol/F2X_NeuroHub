"""
FastAPI router for AuditLog entity (READ-ONLY).

This module implements a read-only API for audit logs in the F2X NeuroHub Manufacturing
Execution System. Audit logs are immutable records created automatically by database
triggers when data changes in the system.

READ-ONLY API DESIGN:
    Audit logs are inherently immutable and cannot be created, modified, or deleted through
    the API. This design is enforced at multiple levels:

    1. Database-Level Enforcement:
        - Database trigger prevent_audit_modification() blocks ALL UPDATE/DELETE operations
        - CHECK constraints enforce data consistency (old_values, new_values nullability)
        - FK constraint with RESTRICT prevents orphaned audit records
        - Monthly range partitioning on created_at for performance

    2. Application-Level Design:
        - Only GET endpoints are implemented (no POST/PUT/PATCH/DELETE)
        - No create_audit or update_audit functions in CRUD layer
        - API schema does not expose create/update operations

    3. Compliance Requirements:
        - Immutable audit trail required for regulatory compliance
        - User accountability for all system changes
        - Cannot modify historical records for audit integrity
        - Cannot delete logs to maintain compliance trail

ENDPOINTS:
    GET /audit-logs
        List all audit logs with pagination (most recent first)
        Query parameters:
            - skip: int (default: 0) - Offset for pagination
            - limit: int (default: 100, max: 100) - Page size
        Returns:
            - List[AuditLogInDB]: Audit log entries

    GET /audit-logs/{id}
        Get a single audit log by ID
        Path parameters:
            - id: int - Audit log ID
        Returns:
            - AuditLogInDB: Audit log entry (404 if not found)

    GET /audit-logs/entity/{entity_type}/{entity_id}
        Get audit logs for a specific entity
        Path parameters:
            - entity_type: str - Entity table name (lots, serials, product_models, etc.)
            - entity_id: int - Entity record ID
        Query parameters:
            - skip: int (default: 0) - Offset for pagination
            - limit: int (default: 100) - Page size
        Returns:
            - List[AuditLogInDB]: All changes to that entity

    GET /audit-logs/user/{user_id}
        Get all audit logs for actions performed by a user
        Path parameters:
            - user_id: int - User ID
        Query parameters:
            - skip: int (default: 0) - Offset for pagination
            - limit: int (default: 100) - Page size
        Returns:
            - List[AuditLogInDB]: All actions performed by user

    GET /audit-logs/action/{action}
        Filter audit logs by action type
        Path parameters:
            - action: str - Action type (CREATE, UPDATE, DELETE)
        Query parameters:
            - skip: int (default: 0) - Offset for pagination
            - limit: int (default: 100) - Page size
        Returns:
            - List[AuditLogInDB]: All logs for the specified action

    GET /audit-logs/date-range
        Filter audit logs by date range
        Query parameters:
            - start_date: datetime - Start of range (inclusive)
            - end_date: datetime - End of range (inclusive)
            - skip: int (default: 0) - Offset for pagination
            - limit: int (default: 100) - Page size
        Returns:
            - List[AuditLogInDB]: All logs within the date range

    GET /audit-logs/entity/{entity_type}/{entity_id}/history
        Get complete change history for an entity
        Path parameters:
            - entity_type: str - Entity table name
            - entity_id: int - Entity record ID
        Query parameters:
            - skip: int (default: 0) - Offset for pagination
            - limit: int (default: 100) - Page size
        Returns:
            - List[AuditLogInDB]: Complete change history

WHY NO MUTATION ENDPOINTS:
    1. Immutability by Design:
        Audit logs must be immutable to maintain integrity and compliance. Allowing
        modifications would compromise the audit trail's purpose of providing an
        accurate record of all system changes.

    2. Database-Level Constraints:
        A database trigger (prevent_audit_modification) explicitly prevents any UPDATE
        or DELETE operations on audit_logs table. Attempting to create mutation
        endpoints would simply fail at the database layer.

    3. Compliance Requirements:
        Most regulatory frameworks (SOX, HIPAA, GDPR) require immutable audit trails
        that cannot be altered or deleted. Mutation endpoints would violate these
        requirements.

    4. Automatic Creation:
        Audit logs are created automatically by database triggers when changes occur
        to audited entities. Manual creation would bypass this mechanism and compromise
        the integrity of the audit trail.

    5. Data Consistency:
        Allowing direct modification of audit logs would break the guarantee that
        the audit trail accurately reflects what happened in the system. The audit
        trail's value depends on its immutability.

    6. Zero Trust Security:
        Audit logs are a critical security control. If users or admins could modify
        them, there would be no trusted record of system activities for investigating
        security incidents or compliance audits.

Example Usage:
    # Get most recent 10 audit logs
    GET /api/v1/audit-logs?skip=0&limit=10

    # Get all changes to lot ID 123
    GET /api/v1/audit-logs/entity/lots/123

    # Get all DELETE operations
    GET /api/v1/audit-logs/action/DELETE?limit=50

    # Get user 5's activity logs
    GET /api/v1/audit-logs/user/5?limit=25

    # Get logs from last 7 days
    GET /api/v1/audit-logs/date-range?start_date=2025-11-11T00:00:00Z&end_date=2025-11-18T23:59:59Z

    # Get complete history of serial 789
    GET /api/v1/audit-logs/entity/serials/789/history
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models import User
from app.models.audit_log import AuditAction
from app.schemas.audit_log import AuditLogInDB
from app.core.exceptions import (
    AuditLogNotFoundException,
    ValidationException,
)

# Create router with consistent prefix/tags
router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs (Read-Only)"],
)


@router.get(
    "/",
    response_model=List[AuditLogInDB],
    status_code=status.HTTP_200_OK,
    summary="List all audit logs",
    responses={
        200: {
            "description": "List of audit logs in reverse chronological order",
            "example": {
                "id": 1,
                "user_id": 1,
                "entity_type": "lots",
                "entity_id": 42,
                "action": "CREATE",
                "old_values": None,
                "new_values": {"lot_number": "LOT-001", "status": "ACTIVE"},
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "created_at": "2025-11-18T10:30:45.123456+00:00",
                "user_id": 1
            }
        }
    }
)
def list_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[AuditLogInDB]:
    """
    List all audit logs with pagination.

    Returns audit logs in reverse chronological order (most recent first).

    Query Parameters:
        - skip: Number of records to skip for pagination (default: 0)
        - limit: Maximum number of records to return (default: 100, max: 100)

    Returns:
        List of AuditLogInDB objects ordered by created_at descending

    Note:
        Audit logs are immutable and created automatically by database triggers.
        They cannot be created, modified, or deleted via API. This endpoint
        provides read-only access for compliance and audit analysis.
    """
    return crud.audit_log.get_multi(db, skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=AuditLogInDB,
    status_code=status.HTTP_200_OK,
    summary="Get audit log by ID",
    responses={
        200: {
            "description": "Audit log entry",
        },
        404: {
            "description": "Audit log not found",
            "model": dict,
            "example": {"detail": "Audit log not found"}
        }
    }
)
def get_audit_log(
    id: int = Path(..., gt=0, description="Audit log ID"),
    db: Session = Depends(deps.get_db),
) -> AuditLogInDB:
    """
    Get a single audit log entry by ID.

    Retrieves an immutable audit log record by its primary key.

    Path Parameters:
        - id: Audit log ID

    Returns:
        AuditLogInDB: The audit log entry

    Raises:
        HTTPException 404: If audit log with given ID does not exist

    Note:
        Audit logs are created automatically by database triggers.
        This is a read-only endpoint.
    """
    audit_log = crud.audit_log.get(db, id=id)
    if not audit_log:
        raise AuditLogNotFoundException(audit_log_id=id)
    return audit_log


@router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=List[AuditLogInDB],
    status_code=status.HTTP_200_OK,
    summary="Get audit logs for an entity",
    responses={
        200: {
            "description": "List of audit logs for the specified entity",
        }
    }
)
def get_entity_audit_logs(
    entity_type: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description="Entity type (table name) - e.g., 'lots', 'serials', 'product_models'"
    ),
    entity_id: int = Path(
        ...,
        gt=0,
        description="Primary key of the entity record"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
) -> List[AuditLogInDB]:
    """
    Get all audit logs for a specific entity.

    Returns all CREATE, UPDATE, and DELETE operations on the specified entity
    in reverse chronological order (most recent first).

    Query Parameters:
        - entity_type: Entity type (e.g., 'lots', 'serials', 'product_models')
        - entity_id: Primary key of the entity record
        - skip: Number of records to skip for pagination (default: 0)
        - limit: Maximum records to return (default: 100, max: 100)

    Returns:
        List of AuditLogInDB objects for the specified entity, most recent first

    Example:
        Get all changes to lot ID 123:
        GET /api/v1/audit-logs/entity/lots/123

    Note:
        This provides a complete change history for compliance analysis.
        Logs are immutable - they cannot be modified or deleted.
    """
    return crud.audit_log.get_by_entity(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/user/{user_id}",
    response_model=List[AuditLogInDB],
    status_code=status.HTTP_200_OK,
    summary="Get activity logs for a user",
    responses={
        200: {
            "description": "List of audit logs for actions performed by the user",
        }
    }
)
def get_user_activity(
    user_id: int = Path(
        ...,
        gt=0,
        description="User ID"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
) -> List[AuditLogInDB]:
    """
    Get all audit logs for actions performed by a user.

    Returns all CREATE, UPDATE, and DELETE operations performed by the specified
    user in reverse chronological order (most recent first).

    Query Parameters:
        - user_id: ID of the user
        - skip: Number of records to skip for pagination (default: 0)
        - limit: Maximum records to return (default: 100, max: 100)

    Returns:
        List of AuditLogInDB objects for actions by the user, most recent first

    Example:
        Get all actions performed by user 5:
        GET /api/v1/audit-logs/user/5?limit=50

    Note:
        Useful for user accountability analysis and security auditing.
        Logs are immutable and cannot be deleted.
    """
    return crud.audit_log.get_by_user(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/action/{action}",
    response_model=List[AuditLogInDB],
    status_code=status.HTTP_200_OK,
    summary="Filter audit logs by action type",
    responses={
        200: {
            "description": "List of audit logs for the specified action",
        },
        400: {
            "description": "Invalid action type",
            "example": {"detail": "Invalid action. Must be one of: CREATE, UPDATE, DELETE"}
        }
    }
)
def get_logs_by_action(
    action: str = Path(
        ...,
        min_length=1,
        description="Action type: CREATE, UPDATE, or DELETE"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
) -> List[AuditLogInDB]:
    """
    Get audit logs filtered by action type.

    Returns all audit logs of the specified action type (CREATE, UPDATE, or DELETE)
    in reverse chronological order (most recent first).

    Query Parameters:
        - action: Action type ('CREATE', 'UPDATE', or 'DELETE')
        - skip: Number of records to skip for pagination (default: 0)
        - limit: Maximum records to return (default: 100, max: 100)

    Returns:
        List of AuditLogInDB objects for the specified action, most recent first

    Raises:
        HTTPException 400: If action is not one of the valid types

    Example:
        Get all DELETE operations:
        GET /api/v1/audit-logs/action/DELETE?limit=50

    Note:
        Useful for analyzing specific types of changes (all deletions, all updates, etc.).
        Action values must be uppercase (CREATE, UPDATE, DELETE).
    """
    # Validate action parameter
    valid_actions = {action_enum.value for action_enum in AuditAction}
    if action.upper() not in valid_actions:
        raise ValidationException(
            message=f"Invalid action. Must be one of: {', '.join(sorted(valid_actions))}"
        )

    try:
        return crud.audit_log.get_by_action(
            db,
            action=action.upper(),
            skip=skip,
            limit=limit
        )
    except ValueError as e:
        raise ValidationException(message=str(e))


@router.get(
    "/date-range",
    response_model=List[AuditLogInDB],
    status_code=status.HTTP_200_OK,
    summary="Filter audit logs by date range",
    responses={
        200: {
            "description": "List of audit logs within the specified date range",
        },
        400: {
            "description": "Invalid date range",
            "example": {"detail": "start_date must be before end_date"}
        }
    }
)
def get_logs_by_date_range(
    start_date: datetime = Query(
        ...,
        description="Start of date range (inclusive), ISO 8601 format"
    ),
    end_date: datetime = Query(
        ...,
        description="End of date range (inclusive), ISO 8601 format"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
) -> List[AuditLogInDB]:
    """
    Get audit logs within a specific date range.

    Returns all audit logs created between start_date and end_date (inclusive)
    in reverse chronological order (most recent first).

    Query Parameters:
        - start_date: Start of range (inclusive), ISO 8601 format (e.g., 2025-11-11T00:00:00Z)
        - end_date: End of range (inclusive), ISO 8601 format (e.g., 2025-11-18T23:59:59Z)
        - skip: Number of records to skip for pagination (default: 0)
        - limit: Maximum records to return (default: 100, max: 100)

    Returns:
        List of AuditLogInDB objects within the date range, most recent first

    Raises:
        HTTPException 400: If start_date is after end_date

    Example:
        Get logs from the last 7 days:
        GET /api/v1/audit-logs/date-range?start_date=2025-11-11T00:00:00Z&end_date=2025-11-18T23:59:59Z

    Note:
        Useful for compliance reporting, incident investigation, and auditing
        specific time periods. Timestamps are in UTC.
    """
    # Validate date range
    if start_date > end_date:
        raise ValidationException(
            message="start_date must be before or equal to end_date"
        )

    return crud.audit_log.get_by_date_range(
        db,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.get(
    "/entity/{entity_type}/{entity_id}/history",
    response_model=List[AuditLogInDB],
    status_code=status.HTTP_200_OK,
    summary="Get complete change history for an entity",
    responses={
        200: {
            "description": "Complete change history including all CREATE, UPDATE, DELETE operations",
        }
    }
)
def get_entity_change_history(
    entity_type: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description="Entity type (table name) - e.g., 'lots', 'serials', 'product_models'"
    ),
    entity_id: int = Path(
        ...,
        gt=0,
        description="Primary key of the entity record"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: Session = Depends(deps.get_db),
) -> List[AuditLogInDB]:
    """
    Get the complete change history for a specific entity.

    Returns all audit log entries documenting every change made to the specified
    entity record, including CREATE, UPDATE, and DELETE operations in reverse
    chronological order (most recent first).

    This provides a comprehensive audit trail showing the full lifecycle of any
    record in the system, useful for compliance audits and understanding what
    changes have been made and when.

    Query Parameters:
        - entity_type: Entity type (e.g., 'lots', 'serials', 'product_models')
        - entity_id: Primary key of the entity record
        - skip: Number of records to skip for pagination (default: 0)
        - limit: Maximum records to return (default: 100, max: 100)

    Returns:
        List of AuditLogInDB objects representing the complete history, most recent first

    Example:
        Get complete history of serial 789:
        GET /api/v1/audit-logs/entity/serials/789/history

    Note:
        Each log entry contains:
        - action: Type of change (CREATE, UPDATE, or DELETE)
        - old_values: Record snapshot before the change (null for CREATE)
        - new_values: Record snapshot after the change (null for DELETE)
        - user: Who made the change
        - created_at: When the change occurred
        - ip_address: Client IP address for security analysis

        Useful for:
        - Compliance audits
        - Change tracking
        - Understanding record lifecycle
        - Security incident investigation
    """
    return crud.audit_log.get_entity_history(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
