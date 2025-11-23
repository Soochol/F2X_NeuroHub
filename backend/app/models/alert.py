"""
Alert model for system notifications and alarms.

This module defines the Alert ORM model that represents the alerts table in the
F2X NeuroHub database. It provides notification and alarm functionality for
production managers to track critical events, defects, and process issues.

Provides:
    - Alert: SQLAlchemy ORM model for the alerts table
    - AlertType: Enumeration for alert types (DEFECT, REWORK_REQUEST, PROCESS_DELAY, etc.)
    - AlertSeverity: Enumeration for severity levels (HIGH, MEDIUM, LOW)
    - AlertStatus: Enumeration for alert states (UNREAD, READ, ARCHIVED)

Database Table: alerts
    - Primary Key: id (BIGSERIAL)
    - Foreign Keys: lot_id (optional), serial_id (optional), process_id (optional)
    - Indexes: status, severity, type, created_at, related entities
    - Audit Fields: created_at, read_at, archived_at
"""

from datetime import datetime, timezone
from typing import Optional
import enum

from sqlalchemy import (
    Index,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlertType(str, enum.Enum):
    """
    Alert type enumeration for categorizing alerts.

    Types:
        DEFECT_DETECTED: Product defect detected in quality check
        REWORK_REQUEST: Operator requesting rework approval
        PROCESS_DELAY: Process exceeding expected cycle time
        LOT_COMPLETED: LOT production completed
        LOT_CLOSED: LOT closed by manager
        EQUIPMENT_FAILURE: Equipment malfunction detected
        QUALITY_THRESHOLD: Quality metrics below threshold
        SYSTEM_ERROR: System or integration error
        MANUAL: Manually created alert by user
    """
    DEFECT_DETECTED = "DEFECT_DETECTED"
    REWORK_REQUEST = "REWORK_REQUEST"
    PROCESS_DELAY = "PROCESS_DELAY"
    LOT_COMPLETED = "LOT_COMPLETED"
    LOT_CLOSED = "LOT_CLOSED"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"
    QUALITY_THRESHOLD = "QUALITY_THRESHOLD"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    MANUAL = "MANUAL"


class AlertSeverity(str, enum.Enum):
    """
    Alert severity enumeration for prioritization.

    Severity Levels:
        HIGH: Requires immediate attention (production stoppage, critical defects)
        MEDIUM: Requires attention within shift (quality issues, delays)
        LOW: Informational (completions, minor issues)
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, enum.Enum):
    """
    Alert status enumeration for tracking alert lifecycle.

    Status Flow:
        UNREAD → READ → ARCHIVED

    States:
        UNREAD: New alert, not yet viewed by user
        READ: Alert has been viewed by user
        ARCHIVED: Alert archived for historical reference
    """
    UNREAD = "UNREAD"
    READ = "READ"
    ARCHIVED = "ARCHIVED"


class Alert(Base):
    """
    Alert model for system notifications and alarms.

    Represents a notification or alarm in the MES system that alerts production
    managers and operators about important events, defects, delays, and system
    issues requiring attention.

    Attributes:
        id: Unique identifier (auto-incrementing primary key)
        alert_type: Type of alert (DEFECT_DETECTED, REWORK_REQUEST, etc.)
        severity: Severity level (HIGH, MEDIUM, LOW)
        status: Alert status (UNREAD, READ, ARCHIVED)
        title: Alert title (max 200 characters)
        message: Detailed alert message (max 1000 characters)
        lot_id: Optional reference to related LOT
        serial_id: Optional reference to related serial
        process_id: Optional reference to related process
        equipment_id: Optional equipment identifier
        created_by_id: User who triggered/created the alert
        created_at: Alert creation timestamp
        read_at: Timestamp when alert was marked as read
        read_by_id: User who marked alert as read
        archived_at: Timestamp when alert was archived
        archived_by_id: User who archived the alert

    Table Name: alerts

    Constraints:
        - PK: pk_alerts on id
        - FK: fk_alerts_lot on lot_id → lots.id
        - FK: fk_alerts_serial on serial_id → serials.id
        - FK: fk_alerts_process on process_id → processes.id
        - FK: fk_alerts_created_by on created_by_id → users.id
        - FK: fk_alerts_read_by on read_by_id → users.id
        - FK: fk_alerts_archived_by on archived_by_id → users.id

    Indexes:
        - idx_alerts_status: (status, created_at DESC) WHERE status IN ('UNREAD', 'READ')
        - idx_alerts_severity: (severity, created_at DESC)
        - idx_alerts_type: (alert_type, created_at DESC)
        - idx_alerts_lot: (lot_id, created_at DESC) WHERE lot_id IS NOT NULL
        - idx_alerts_serial: (serial_id) WHERE serial_id IS NOT NULL
        - idx_alerts_created_at: (created_at DESC)
    """

    __tablename__ = "alerts"

    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Alert classification
    alert_type: Mapped[AlertType] = mapped_column(
        Enum(AlertType, native_enum=False, length=30),
        nullable=False
    )

    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, native_enum=False, length=10),
        nullable=False,
        default=AlertSeverity.MEDIUM
    )

    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, native_enum=False, length=10),
        nullable=False,
        default=AlertStatus.UNREAD
    )

    # Alert content
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Related entities (optional)
    lot_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("lots.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    serial_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("serials.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    process_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("processes.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    equipment_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=None
    )

    # User tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    read_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    archived_by_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP")
    )

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    # Relationships
    lot: Mapped[Optional["Lot"]] = relationship(
        "Lot",
        back_populates="alerts",
        foreign_keys=[lot_id]
    )

    serial: Mapped[Optional["Serial"]] = relationship(
        "Serial",
        back_populates="alerts",
        foreign_keys=[serial_id]
    )

    process: Mapped[Optional["Process"]] = relationship(
        "Process",
        back_populates="alerts",
        foreign_keys=[process_id]
    )

    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_id]
    )

    read_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[read_by_id]
    )

    archived_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[archived_by_id]
    )

    # Indexes
    __table_args__ = (
        Index(
            "idx_alerts_status",
            "status",
            "created_at"
        ),
        Index(
            "idx_alerts_severity",
            "severity",
            "created_at"
        ),
        Index(
            "idx_alerts_type",
            "alert_type",
            "created_at"
        ),
        Index(
            "idx_alerts_lot",
            "lot_id",
            "created_at"
        ),
        Index(
            "idx_alerts_serial",
            "serial_id"
        ),
        Index(
            "idx_alerts_created_at",
            "created_at"
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of Alert instance."""
        return (
            f"<Alert(id={self.id}, type={self.alert_type.value}, "
            f"severity={self.severity.value}, status={self.status.value})>"
        )

    def to_dict(self) -> dict:
        """
        Convert Alert instance to dictionary.

        Returns:
            Dictionary representation of alert with all fields
        """
        return {
            "id": self.id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "message": self.message,
            "lot_id": self.lot_id,
            "serial_id": self.serial_id,
            "process_id": self.process_id,
            "equipment_id": self.equipment_id,
            "created_by_id": self.created_by_id,
            "read_by_id": self.read_by_id,
            "archived_by_id": self.archived_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
        }
