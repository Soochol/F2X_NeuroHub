"""
Serial model for individual unit tracking within production lots.

This module defines the Serial ORM model that represents the serials table in the
F2X NeuroHub database. Each serial represents one physical product unit within a LOT,
with lifecycle management from creation through pass/fail completion.

Provides:
    - Serial: SQLAlchemy ORM model for the serials table
    - SerialStatus: Enumeration for serial lifecycle states

Database Table: serials
    - Primary Key: id (BIGSERIAL)
    - Foreign Key: lot_id → lots(id)
    - Unique Constraints: serial_number, (lot_id, sequence_in_lot)
    - Status Enum: CREATED, IN_PROGRESS, PASSED, FAILED
    - Audit Fields: created_at, updated_at, completed_at
    - Rework Support: max 3 rework attempts
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

import enum
from sqlalchemy import (
    Index,
    String,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.lot import Lot
    from app.models.process_data import ProcessData


class SerialStatus(str, enum.Enum):
    """
    Serial lifecycle status enumeration.

    States:
        CREATED: Initial state, serial created but not yet in production
        IN_PROGRESS: Serial actively being processed in production
        PASSED: Serial completed processing successfully (terminal state)
        FAILED: Serial failed quality checks (rework may be available)
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"


class Serial(Base):
    """
    Serial model for individual unit tracking within production lots.

    Represents a single physical product unit within a LOT. Tracks the complete
    lifecycle from creation through processing to final pass/fail status. Supports
    up to 3 rework attempts for failed units.

    Attributes:
        id: Unique identifier (auto-incrementing primary key)
        serial_number: Auto-generated unique serial identifier in format: {LOT_NUMBER}-XXXX
        lot_id: Foreign key reference to parent LOT
        sequence_in_lot: Sequence number within LOT (1-100, auto-assigned)
        status: Serial lifecycle status (CREATED, IN_PROGRESS, PASSED, FAILED)
        rework_count: Number of rework attempts performed (0-3 maximum)
        failure_reason: Reason for failure (required only when status = FAILED)
        created_at: Serial creation timestamp (auto-set to current time)
        updated_at: Last update timestamp (auto-updated on changes)
        completed_at: Timestamp when serial reached PASSED or FAILED status

    Relationships:
        lot: Reference to parent Lot (many-to-one)
        process_data: List of ProcessData records for this serial (one-to-many)

    Table Name: serials

    Constraints:
        - PK: pk_serials on id
        - FK: fk_serials_lot on (lot_id) → lots(id)
        - UK: uk_serials_serial_number on serial_number
        - UK: uk_serials_lot_sequence on (lot_id, sequence_in_lot)
        - CHK: chk_serials_status (status IN ['CREATED', 'IN_PROGRESS', 'PASSED', 'FAILED'])
        - CHK: chk_serials_sequence (sequence_in_lot >= 1 AND sequence_in_lot <= 100)
        - CHK: chk_serials_rework_count (rework_count >= 0 AND rework_count <= 3)
        - CHK: chk_serials_failure_reason (failure_reason required for FAILED status)

    Indexes:
        - idx_serials_lot: (lot_id)
        - idx_serials_status: (status)
        - idx_serials_active: (lot_id, status) WHERE status IN ('CREATED', 'IN_PROGRESS')
        - idx_serials_failed: (lot_id, failure_reason) WHERE status = 'FAILED'
        - idx_serials_rework: (rework_count) WHERE rework_count > 0
        - idx_serials_completed_at: (completed_at) WHERE completed_at IS NOT NULL

    State Machine Rules:
        - CREATED → IN_PROGRESS (start processing)
        - IN_PROGRESS → PASSED or FAILED (complete processing)
        - FAILED → IN_PROGRESS (rework, max 3 attempts)
        - PASSED is final (no further transitions allowed)

    Triggers (PostgreSQL):
        - generate_serial_number: Auto-generate serial_number and sequence_in_lot
        - validate_lot_capacity: Enforce max 100 serials per LOT
        - validate_serial_status_transition: Enforce state machine rules
        - update_lot_quantities: Update parent LOT statistics
        - update_timestamp: Auto-update updated_at on changes
    """

    __tablename__ = "serials"

    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Serial identification
    serial_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=False,  # Unique constraint provides index
    )

    # LOT relationship
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lots.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False
    )

    sequence_in_lot: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Status tracking
    status: Mapped[SerialStatus] = mapped_column(
        Enum(SerialStatus, native_enum=False, length=20),
        nullable=False,
        default=SerialStatus.CREATED
    )

    rework_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    # Relationships
    lot: Mapped["Lot"] = relationship(
        "Lot",
        back_populates="serials",
        foreign_keys=[lot_id]
    )

    process_data_records: Mapped[list["ProcessData"]] = relationship(
        "ProcessData",
        back_populates="serial",
        cascade="all, delete-orphan"
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="serial",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        # Foreign key index for lot queries
        Index(
            "idx_serials_lot",
            "lot_id"
        ),
        # Status-based queries
        Index(
            "idx_serials_status",
            "status"
        ),
        # Active serials (partial index for performance)
        Index(
            "idx_serials_active",
            "lot_id",
            "status"
        ),
        # Failed serials analysis (partial index)
        Index(
            "idx_serials_failed",
            "lot_id",
            "failure_reason"),
        # Rework tracking (partial index)
        Index(
            "idx_serials_rework",
            "rework_count"),
        # Completion time analysis (partial index)
        Index(
            "idx_serials_completed_at",
            "completed_at"),
        # Check constraints
        CheckConstraint(
            "rework_count >= 0 AND rework_count <= 3",
            name="chk_serials_rework_count",
        ),
        CheckConstraint(
            "sequence_in_lot >= 1 AND sequence_in_lot <= 100",
            name="chk_serials_sequence",
        ),
        CheckConstraint(
            "status IN ('CREATED', 'IN_PROGRESS', 'PASSED', 'FAILED')",
            name="chk_serials_status",
        ),
        CheckConstraint(
            "(status = 'FAILED' AND failure_reason IS NOT NULL) OR (status != 'FAILED' AND failure_reason IS NULL)",
            name="chk_serials_failure_reason",
        ),
    )

    def __repr__(self) -> str:
        """
        Return string representation of Serial instance.

        Returns:
            String representation including ID, serial_number, status, and lot_id
        """
        return (
            f"<Serial(id={self.id}, serial_number='{self.serial_number}', "
            f"status={self.status.value}, lot_id={self.lot_id}, rework_count={self.rework_count})>"
        )

    def to_dict(self) -> dict:
        """
        Convert Serial instance to dictionary.

        Includes all columns and computed properties. Timestamps are converted
        to ISO format strings.

        Returns:
            Dictionary representation of serial with all fields

        Example:
            {
                "id": 42,
                "serial_number": "WF-KR-251110D-001-0001",
                "lot_id": 5,
                "sequence_in_lot": 1,
                "status": "IN_PROGRESS",
                "rework_count": 0,
                "failure_reason": None,
                "created_at": "2025-11-18T10:30:00+00:00",
                "updated_at": "2025-11-18T10:30:00+00:00",
                "completed_at": None
            }
        """
        return {
            "id": self.id,
            "serial_number": self.serial_number,
            "lot_id": self.lot_id,
            "sequence_in_lot": self.sequence_in_lot,
            "status": self.status.value,
            "rework_count": self.rework_count,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def can_transition_to(self, new_status: "SerialStatus") -> bool:
        """
        Check if status transition is valid according to state machine rules.

        Valid transitions:
            - CREATED → IN_PROGRESS (start processing)
            - IN_PROGRESS → PASSED or FAILED (complete processing)
            - FAILED → IN_PROGRESS (rework, max 3 attempts)
            - PASSED is final (no transitions allowed)

        Args:
            new_status: Target status for transition

        Returns:
            True if transition is valid, False otherwise

        Example:
            >>> serial.status = SerialStatus.CREATED
            >>> serial.can_transition_to(SerialStatus.IN_PROGRESS)
            True
            >>> serial.can_transition_to(SerialStatus.PASSED)
            False
        """
        if self.status == new_status:
            return True  # Allow "transition" to same status (no-op)

        current = self.status

        # CREATED can only go to IN_PROGRESS
        if current == SerialStatus.CREATED:
            return new_status == SerialStatus.IN_PROGRESS

        # IN_PROGRESS can go to PASSED or FAILED
        if current == SerialStatus.IN_PROGRESS:
            return new_status in (SerialStatus.PASSED, SerialStatus.FAILED)

        # FAILED can go back to IN_PROGRESS for rework (if under limit)
        if current == SerialStatus.FAILED:
            return new_status == SerialStatus.IN_PROGRESS and self.rework_count < 3

        # PASSED is final, no transitions allowed
        if current == SerialStatus.PASSED:
            return False

        return False

    def is_active(self) -> bool:
        """
        Check if serial is still in active processing.

        A serial is considered active if it has not yet reached a terminal state
        (PASSED or FAILED with no rework pending).

        Returns:
            True if serial status is CREATED or IN_PROGRESS, False otherwise

        Example:
            >>> serial.status = SerialStatus.IN_PROGRESS
            >>> serial.is_active()
            True
            >>> serial.status = SerialStatus.PASSED
            >>> serial.is_active()
            False
        """
        return self.status in (SerialStatus.CREATED, SerialStatus.IN_PROGRESS)

    def is_completed(self) -> bool:
        """
        Check if serial has reached a terminal state.

        A serial is completed when it has reached PASSED status or FAILED status
        with maximum rework attempts exhausted (rework_count >= 3).

        Returns:
            True if serial is in a terminal state, False otherwise

        Example:
            >>> serial.status = SerialStatus.PASSED
            >>> serial.is_completed()
            True
        """
        if self.status == SerialStatus.PASSED:
            return True
        if self.status == SerialStatus.FAILED and self.rework_count >= 3:
            return True
        return False

    def can_rework(self) -> bool:
        """
        Check if serial is eligible for rework.

        A serial can be reworked if:
            1. Current status is FAILED
            2. Rework count is less than 3 (max attempts)

        Returns:
            True if serial can be reworked, False otherwise

        Example:
            >>> serial.status = SerialStatus.FAILED
            >>> serial.rework_count = 1
            >>> serial.can_rework()
            True
            >>> serial.rework_count = 3
            >>> serial.can_rework()
            False
        """
        return self.status == SerialStatus.FAILED and self.rework_count < 3
