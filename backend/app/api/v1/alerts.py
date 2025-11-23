"""
FastAPI router for Alert entity endpoints.

This module implements RESTful API endpoints for alert management including:
    - Standard CRUD operations (GET, POST, PUT, DELETE)
    - Alert filtering by status, severity, type, date range
    - Mark single or multiple alerts as read
    - Unread count for notification badges

Endpoints:
    GET    /alerts/              - List all alerts with pagination and filters
    GET    /alerts/{id}          - Get alert by ID
    GET    /alerts/unread/count  - Get count of unread alerts
    POST   /alerts/              - Create new alert
    PUT    /alerts/{id}          - Update alert (status change)
    PUT    /alerts/{id}/read     - Mark single alert as read
    PUT    /alerts/bulk-read     - Mark multiple alerts as read
    DELETE /alerts/{id}          - Delete alert
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.models.alert import AlertType, AlertSeverity, AlertStatus
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertInDB,
    AlertResponse,
    AlertListResponse,
    AlertMarkRead,
    AlertBulkMarkRead,
)
from app.services.notification_service import notification_service


# Create APIRouter
router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get(
    "/",
    response_model=AlertListResponse,
    summary="List all alerts",
    description="Retrieve a paginated list of alerts with optional filtering by status, severity, type, and date range.",
)
def list_alerts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Maximum number of records to return (max: 200)",
    ),
    status: Optional[AlertStatus] = Query(
        None,
        description="Filter by alert status (UNREAD, READ, ARCHIVED)",
    ),
    severity: Optional[AlertSeverity] = Query(
        None,
        description="Filter by severity (HIGH, MEDIUM, LOW)",
    ),
    alert_type: Optional[AlertType] = Query(
        None,
        description="Filter by alert type",
    ),
    lot_id: Optional[int] = Query(
        None,
        description="Filter by related LOT ID",
    ),
    start_date: Optional[date] = Query(
        None,
        description="Filter by creation date (from)",
    ),
    end_date: Optional[date] = Query(
        None,
        description="Filter by creation date (to)",
    ),
):
    """
    Retrieve a paginated list of alerts.

    Query parameters allow filtering by status, severity, type, lot, and date range.
    Results are ordered by creation timestamp (newest first).

    Returns:
        AlertListResponse with alerts list, total count, and unread count
    """
    return notification_service.list_alerts(
        db,
        skip=skip,
        limit=limit,
        status=status,
        severity=severity,
        alert_type=alert_type,
        lot_id=lot_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/unread/count",
    response_model=dict,
    summary="Get unread alert count",
    description="Retrieve the count of unread alerts for notification badges.",
)
def get_unread_count(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get count of unread alerts.

    Returns:
        Dictionary with unread_count field
    """
    return notification_service.get_unread_count(db)


@router.put(
    "/bulk-read",
    response_model=dict,
    summary="Mark multiple alerts as read",
    description="Mark multiple alerts as read in bulk (more efficient than single updates).",
)
def bulk_mark_alerts_as_read(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    bulk_read: AlertBulkMarkRead,
):
    """
    Mark multiple alerts as read in bulk.

    More efficient than calling mark_as_read multiple times. Updates all
    specified alerts in a single database transaction.

    Request body should contain:
        - alert_ids: List of alert IDs to mark as read
        - read_by_id: User ID marking the alerts

    Returns:
        Dictionary with count of updated alerts

    Raises:
        500: Database error
    """
    return notification_service.bulk_mark_as_read(
        db,
        alert_ids=bulk_read.alert_ids,
        read_by_id=bulk_read.read_by_id
    )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get alert by ID",
    description="Retrieve a single alert by its ID with related entity information.",
)
def get_alert(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    alert_id: int = Path(..., description="Alert ID"),
):
    """
    Retrieve a single alert by ID.

    Args:
        alert_id: Alert ID to retrieve

    Returns:
        AlertResponse with alert details and related entity names

    Raises:
        404: Alert not found
    """
    return notification_service.get_alert(db, alert_id=alert_id)


@router.post(
    "/",
    response_model=AlertInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new alert",
    description="Create a new alert (manually or via system automation).",
)
def create_alert(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    alert_in: AlertCreate,
):
    """
    Create a new alert.

    Request body should contain alert details including type, severity, title,
    message, and optional references to lot, serial, or process.

    Returns:
        Created alert with ID and timestamps

    Raises:
        500: Database error
    """
    return notification_service.create_alert(db, alert_in=alert_in)


@router.put(
    "/{alert_id}",
    response_model=AlertInDB,
    summary="Update alert",
    description="Update alert status or other fields.",
)
def update_alert(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    alert_id: int = Path(..., description="Alert ID"),
    alert_in: AlertUpdate,
):
    """
    Update an alert.

    Primarily used for updating alert status (UNREAD → READ → ARCHIVED).

    Args:
        alert_id: Alert ID to update
        alert_in: Fields to update

    Returns:
        Updated alert

    Raises:
        404: Alert not found
        500: Database error
    """
    return notification_service.update_alert(db, alert_id=alert_id, alert_in=alert_in)


@router.put(
    "/{alert_id}/read",
    response_model=AlertInDB,
    summary="Mark alert as read",
    description="Mark a single alert as read.",
)
def mark_alert_as_read(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    alert_id: int = Path(..., description="Alert ID"),
    mark_read: AlertMarkRead,
):
    """
    Mark a single alert as read.

    Updates alert status to READ and sets read_at timestamp.

    Args:
        alert_id: Alert ID to mark as read
        mark_read: Contains read_by_id (user ID)

    Returns:
        Updated alert

    Raises:
        404: Alert not found
        500: Database error
    """
    return notification_service.mark_as_read(
        db,
        alert_id=alert_id,
        read_by_id=mark_read.read_by_id
    )


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete alert",
    description="Delete an alert permanently. Consider archiving instead for audit compliance.",
)
def delete_alert(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    alert_id: int = Path(..., description="Alert ID"),
):
    """
    Delete an alert.

    Permanently deletes an alert from the database. Consider using
    archive (status=ARCHIVED) instead for audit trail compliance.

    Args:
        alert_id: Alert ID to delete

    Returns:
        204 No Content on success

    Raises:
        404: Alert not found
        500: Database error
    """
    notification_service.delete_alert(db, alert_id=alert_id)
