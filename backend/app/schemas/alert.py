"""
Alert schemas for request/response validation.

This module defines Pydantic schemas for alert-related operations,
including alert creation, updates, filtering, and API responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class AlertType(str, Enum):
    """Alert type enumeration."""

    DEFECT_DETECTED = "DEFECT_DETECTED"
    REWORK_REQUEST = "REWORK_REQUEST"
    PROCESS_DELAY = "PROCESS_DELAY"
    LOT_COMPLETED = "LOT_COMPLETED"
    LOT_CLOSED = "LOT_CLOSED"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"
    QUALITY_THRESHOLD = "QUALITY_THRESHOLD"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    MANUAL = "MANUAL"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, Enum):
    """Alert status enumeration."""

    UNREAD = "UNREAD"
    READ = "READ"
    ARCHIVED = "ARCHIVED"


class AlertBase(BaseModel):
    """Base alert schema with common fields."""

    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(
        AlertSeverity.MEDIUM,
        description="Severity level"
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Alert title"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Detailed alert message"
    )
    lot_id: Optional[int] = Field(
        None,
        description="Related LOT ID"
    )
    serial_id: Optional[int] = Field(
        None,
        description="Related serial ID"
    )
    process_id: Optional[int] = Field(
        None,
        description="Related process ID"
    )
    equipment_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Equipment identifier"
    )


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""

    created_by_id: Optional[int] = Field(
        None,
        description="User ID who created the alert"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_type": "DEFECT_DETECTED",
                "severity": "HIGH",
                "title": "불량 발생",
                "message": "LOT WF-KR-251118D-001, 공정 3 (센서 검사)에서 불량 발생",
                "lot_id": 1,
                "serial_id": 5,
                "process_id": 3,
                "equipment_id": "SENSOR-CHECK-01",
                "created_by_id": None
            }
        }
    )


class AlertUpdate(BaseModel):
    """Schema for updating alert status."""

    status: Optional[AlertStatus] = Field(
        None,
        description="Alert status"
    )
    read_by_id: Optional[int] = Field(
        None,
        description="User ID who marked as read"
    )
    archived_by_id: Optional[int] = Field(
        None,
        description="User ID who archived the alert"
    )


class AlertMarkRead(BaseModel):
    """Schema for marking alert(s) as read."""

    read_by_id: int = Field(
        ...,
        description="User ID who is marking the alert as read"
    )


class AlertBulkMarkRead(BaseModel):
    """Schema for bulk marking alerts as read."""

    alert_ids: List[int] = Field(
        ...,
        min_length=1,
        description="List of alert IDs to mark as read"
    )
    read_by_id: int = Field(
        ...,
        description="User ID who is marking the alerts as read"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alert_ids": [1, 2, 3, 4, 5],
                "read_by_id": 1
            }
        }
    )


class AlertInDB(AlertBase):
    """Schema for alert data retrieved from database."""

    id: int = Field(..., description="Alert ID")
    status: AlertStatus = Field(..., description="Alert status")
    created_by_id: Optional[int] = Field(
        None,
        description="User ID who created the alert"
    )
    read_by_id: Optional[int] = Field(
        None,
        description="User ID who marked as read"
    )
    archived_by_id: Optional[int] = Field(
        None,
        description="User ID who archived the alert"
    )
    created_at: datetime = Field(..., description="Alert creation timestamp")
    read_at: Optional[datetime] = Field(
        None,
        description="Timestamp when marked as read"
    )
    archived_at: Optional[datetime] = Field(
        None,
        description="Timestamp when archived"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "alert_type": "DEFECT_DETECTED",
                "severity": "HIGH",
                "status": "UNREAD",
                "title": "불량 발생",
                "message": "LOT WF-KR-251118D-001, 공정 3 (센서 검사)에서 불량 발생",
                "lot_id": 1,
                "serial_id": 5,
                "process_id": 3,
                "equipment_id": "SENSOR-CHECK-01",
                "created_by_id": None,
                "read_by_id": None,
                "archived_by_id": None,
                "created_at": "2025-01-18T10:30:00Z",
                "read_at": None,
                "archived_at": None
            }
        }
    )


class AlertResponse(AlertInDB):
    """Schema for alert API response with additional context."""

    # Optional: Include related entity names for frontend display
    lot_number: Optional[str] = Field(
        None,
        description="LOT number if lot_id is set"
    )
    serial_number: Optional[str] = Field(
        None,
        description="Serial number if serial_id is set"
    )
    process_name: Optional[str] = Field(
        None,
        description="Process name if process_id is set"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "alert_type": "DEFECT_DETECTED",
                "severity": "HIGH",
                "status": "UNREAD",
                "title": "불량 발생",
                "message": "LOT WF-KR-251118D-001, 공정 3 (센서 검사)에서 불량 발생",
                "lot_id": 1,
                "lot_number": "WF-KR-251118D-001",
                "serial_id": 5,
                "serial_number": "WF-KR-251118D-001-0005",
                "process_id": 3,
                "process_name": "센서 검사",
                "equipment_id": "SENSOR-CHECK-01",
                "created_by_id": None,
                "read_by_id": None,
                "archived_by_id": None,
                "created_at": "2025-01-18T10:30:00Z",
                "read_at": None,
                "archived_at": None
            }
        }
    )


class AlertListResponse(BaseModel):
    """Schema for paginated alert list response."""

    alerts: List[AlertResponse] = Field(
        ...,
        description="List of alerts"
    )
    total: int = Field(..., description="Total number of alerts matching filters")
    unread_count: int = Field(..., description="Number of unread alerts")
    skip: int = Field(..., description="Number of alerts skipped (offset)")
    limit: int = Field(..., description="Maximum number of alerts returned")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alerts": [
                    {
                        "id": 1,
                        "alert_type": "DEFECT_DETECTED",
                        "severity": "HIGH",
                        "status": "UNREAD",
                        "title": "불량 발생",
                        "message": "LOT WF-KR-251118D-001에서 불량 발생",
                        "lot_id": 1,
                        "lot_number": "WF-KR-251118D-001",
                        "created_at": "2025-01-18T10:30:00Z"
                    }
                ],
                "total": 25,
                "unread_count": 12,
                "skip": 0,
                "limit": 10
            }
        }
    )
