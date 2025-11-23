from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import crud
from app.models.alert import AlertType, AlertSeverity, AlertStatus
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertInDB,
    AlertResponse,
    AlertListResponse,
)
from app.core.exceptions import (
    AlertNotFoundException,
    DatabaseException,
)

class NotificationService:
    """
    Service for managing Alerts and Notifications.
    Encapsulates business logic and data access for Alerts.
    """

    def list_alerts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        lot_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> AlertListResponse:
        """Retrieve a paginated list of alerts with filtering."""
        try:
            # Get filtered alerts
            alerts = crud.alert.get_multi(
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

            # Get total count (for pagination)
            total = crud.alert.get_multi(
                db,
                skip=0,
                limit=10000,  # Get all for count
                status=status,
                severity=severity,
                alert_type=alert_type,
                lot_id=lot_id,
                start_date=start_date,
                end_date=end_date,
            )

            # Get unread count
            unread_count = crud.alert.get_unread_count(db)

            # Convert to response format with related entity names
            alert_responses = []
            for alert in alerts:
                alert_dict = {
                    **alert.to_dict(),
                    "lot_number": alert.lot.lot_number if alert.lot else None,
                    "serial_number": alert.serial.serial_number if alert.serial else None,
                    "process_name": alert.process.process_name if alert.process else None,
                }
                alert_responses.append(AlertResponse(**alert_dict))

            return AlertListResponse(
                alerts=alert_responses,
                total=len(total),
                unread_count=unread_count,
                skip=skip,
                limit=limit,
            )

        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Database error: {str(e)}")

    def get_unread_count(self, db: Session) -> Dict[str, int]:
        """Get count of unread alerts."""
        try:
            count = crud.alert.get_unread_count(db)
            return {"unread_count": count}
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Database error: {str(e)}")

    def bulk_mark_as_read(self, db: Session, alert_ids: List[int], read_by_id: int) -> Dict[str, Any]:
        """Mark multiple alerts as read in bulk."""
        try:
            updated_count = crud.alert.bulk_mark_as_read(
                db,
                alert_ids=alert_ids,
                read_by_id=read_by_id
            )
            return {
                "updated_count": updated_count,
                "alert_ids": alert_ids,
            }
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Failed to bulk mark alerts as read: {str(e)}")

    def get_alert(self, db: Session, alert_id: int) -> AlertResponse:
        """Retrieve a single alert by ID."""
        try:
            alert = crud.alert.get(db, alert_id=alert_id)
            if not alert:
                raise AlertNotFoundException(alert_id=alert_id)

            # Convert to response format with related entity names
            alert_dict = {
                **alert.to_dict(),
                "lot_number": alert.lot.lot_number if alert.lot else None,
                "serial_number": alert.serial.serial_number if alert.serial else None,
                "process_name": alert.process.process_name if alert.process else None,
            }

            return AlertResponse(**alert_dict)

        except (AlertNotFoundException, DatabaseException):
            raise
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Database error: {str(e)}")

    def create_alert(self, db: Session, alert_in: AlertCreate) -> AlertInDB:
        """Create a new alert."""
        try:
            return crud.alert.create(db, alert_in=alert_in)
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Failed to create alert: {str(e)}")

    def update_alert(self, db: Session, alert_id: int, alert_in: AlertUpdate) -> AlertInDB:
        """Update an alert."""
        try:
            alert = crud.alert.update(db, alert_id=alert_id, alert_in=alert_in)
            if not alert:
                raise AlertNotFoundException(alert_id=alert_id)
            return alert
        except (AlertNotFoundException, DatabaseException):
            raise
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Failed to update alert: {str(e)}")

    def mark_as_read(self, db: Session, alert_id: int, read_by_id: int) -> AlertInDB:
        """Mark a single alert as read."""
        try:
            alert = crud.alert.mark_as_read(
                db,
                alert_id=alert_id,
                read_by_id=read_by_id
            )
            if not alert:
                raise AlertNotFoundException(alert_id=alert_id)
            return alert
        except (AlertNotFoundException, DatabaseException):
            raise
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Failed to mark alert as read: {str(e)}")

    def delete_alert(self, db: Session, alert_id: int) -> None:
        """Delete an alert."""
        try:
            deleted = crud.alert.delete(db, alert_id=alert_id)
            if not deleted:
                raise AlertNotFoundException(alert_id=alert_id)
        except (AlertNotFoundException, DatabaseException):
            raise
        except SQLAlchemyError as e:
            raise DatabaseException(message=f"Failed to delete alert: {str(e)}")

notification_service = NotificationService()
