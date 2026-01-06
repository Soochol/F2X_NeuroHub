"""
SQLAlchemy 2.0 ORM model for the WIP Item entity.

This module provides the WIPItem model representing Work-In-Progress identifiers
in the F2X NeuroHub MES. WIP IDs are temporary identifiers assigned to units
during production processes 1-6, before they receive permanent serial numbers
in process 7.

WIP ID Format: WIP-{LOT}-{SEQ} = WIP- + 11 chars LOT + - + 3 digits sequence
Example: WIP-KR01PSA2511-001 (19 characters total)
    - Prefix: "WIP-" (4 chars)
    - LOT: KR01PSA2511 (11 chars)
    - Separator: "-" (1 char)
    - Sequence: 001 (3 chars, 001-999)

Database table: wip_items
Primary key: id (BIGSERIAL)
Foreign keys:
    - lot_id -> lots.id
    - current_process_id -> processes.id (nullable)
    - serial_id -> serials.id (nullable, set when converted)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    BIGINT,
    VARCHAR,
    INTEGER,
    TIMESTAMP,
    CheckConstraint,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.lot import Lot
    from app.models.process import Process
    from app.models.serial import Serial
    from app.models.wip_process_history import WIPProcessHistory


class WIPStatus(str, Enum):
    """
    WIP lifecycle status enumeration.

    Attributes:
        CREATED: Initial state after WIP creation
        IN_PROGRESS: Currently being processed in a production process
        COMPLETED: All processes (1-6) completed, ready for serial conversion
        FAILED: Failed quality check, cannot proceed
        CONVERTED: Successfully converted to serial number (terminal state)
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CONVERTED = "CONVERTED"


class WIPItem(Base):
    """
    ORM model for Work-In-Progress (WIP) identifiers.

    Represents temporary identifiers assigned to units during production
    processes 1-6. Each WIP tracks its progress through manufacturing
    processes until conversion to a permanent serial number at process 7.

    Table: wip_items
    Primary Key: id (BIGSERIAL)
    Foreign Keys:
        - lot_id -> lots.id (required)
        - current_process_id -> processes.id (nullable)
        - serial_id -> serials.id (nullable, set after conversion)

    Attributes:
        id: Primary key, auto-incrementing BIGSERIAL
        wip_id: Unique WIP identifier (format: WIP-{LOT}-{SEQ}, 19 chars)
        lot_id: Foreign key reference to lots table
        sequence_in_lot: Sequence number within LOT (1-100)
        status: WIP lifecycle status (CREATED, IN_PROGRESS, COMPLETED, FAILED, CONVERTED)
        current_process_id: Current process being executed (nullable)
        serial_id: Final serial number after conversion (nullable, process 7)
        created_at: WIP creation timestamp
        updated_at: Last modification timestamp
        completed_at: All processes completed timestamp (nullable)
        converted_at: Serial conversion timestamp (nullable)
        lot: Relationship to Lot (many-to-one)
        current_process: Relationship to Process (many-to-one, nullable)
        serial: Relationship to Serial (one-to-one, nullable)
        process_history: Relationship to WIPProcessHistory (one-to-many)

    Constraints:
        - wip_id must be unique
        - (lot_id, sequence_in_lot) must be unique
        - sequence_in_lot must be 1-100
        - status must be valid WIPStatus value
        - wip_id format: WIP-{11 chars LOT}-{3 digit SEQ}

    Indexes:
        - idx_wip_items_lot: (lot_id)
        - idx_wip_items_status: (status)
        - idx_wip_items_active: (lot_id, status) WHERE status IN ('CREATED', 'IN_PROGRESS')
        - idx_wip_items_current_process: (current_process_id) WHERE current_process_id IS NOT NULL
        - idx_wip_items_serial: (serial_id) WHERE serial_id IS NOT NULL
        - idx_wip_items_completed_at: (completed_at) WHERE completed_at IS NOT NULL
        - idx_wip_items_converted_at: (converted_at) WHERE converted_at IS NOT NULL
    """

    __tablename__ = "wip_items"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # WIP Identification
    wip_id: Mapped[str] = mapped_column(
        VARCHAR(50),
        nullable=False,
        unique=True,
        comment="Unique WIP identifier (format: WIP-{LOT}-{SEQ})",
    )

    # LOT relationship
    lot_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("lots.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="Foreign key reference to lots table",
    )

    sequence_in_lot: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        comment="Sequence number within LOT (1-100)",
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        VARCHAR(20),
        nullable=False,
        default=WIPStatus.CREATED.value,
        comment="WIP lifecycle status",
    )

    # Process tracking
    current_process_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey("processes.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        default=None,
        comment="Current process being executed (nullable)",
    )

    # Serial conversion
    serial_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey("serials.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        default=None,
        comment="Final serial number after conversion (process 7)",
    )

    converted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        comment="Serial conversion timestamp (process 7)",
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        comment="All processes (1-6) completed timestamp",
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="WIP creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Last modification timestamp",
    )

    # Relationships
    lot: Mapped["Lot"] = relationship(
        "Lot",
        foreign_keys=[lot_id],
        back_populates="wip_items",
        lazy="select",
    )

    current_process: Mapped[Optional["Process"]] = relationship(
        "Process",
        foreign_keys=[current_process_id],
        lazy="select",
    )

    serial: Mapped[Optional["Serial"]] = relationship(
        "Serial",
        foreign_keys=[serial_id],
        lazy="select",
    )

    process_history: Mapped[List["WIPProcessHistory"]] = relationship(
        "WIPProcessHistory",
        back_populates="wip_item",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Table Arguments: Constraints and Indexes
    __table_args__ = (
        # CHECK CONSTRAINTS
        CheckConstraint(
            "sequence_in_lot >= 1 AND sequence_in_lot <= 100",
            name="chk_wip_items_sequence",
        ),
        CheckConstraint(
            "status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CONVERTED')",
            name="chk_wip_items_status",
        ),
        CheckConstraint(
            "wip_id LIKE 'WIP-%'",
            name="chk_wip_items_format",
        ),

        # UNIQUE CONSTRAINTS
        Index(
            "uk_wip_items_lot_sequence",
            lot_id,
            sequence_in_lot,
            unique=True,
        ),

        # FOREIGN KEY INDEXES
        Index(
            "idx_wip_items_lot",
            lot_id,
        ),
        Index(
            "idx_wip_items_current_process",
            current_process_id,
        ),
        Index(
            "idx_wip_items_serial",
            serial_id,
        ),

        # STATUS-BASED INDEXES
        Index(
            "idx_wip_items_status",
            status,
        ),
        Index(
            "idx_wip_items_active",
            lot_id,
            status,
        ),

        # TIME-BASED INDEXES
        Index(
            "idx_wip_items_completed_at",
            completed_at,
        ),
        Index(
            "idx_wip_items_converted_at",
            converted_at,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of WIPItem instance."""
        return (
            f"<WIPItem(id={self.id}, wip_id='{self.wip_id}', "
            f"lot_id={self.lot_id}, status='{self.status}')>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"WIP {self.wip_id} ({self.status})"

    @property
    def is_active(self) -> bool:
        """Check if WIP is still in active production.

        Returns:
            True if status is CREATED or IN_PROGRESS, False otherwise
        """
        return self.status in (WIPStatus.CREATED.value, WIPStatus.IN_PROGRESS.value)

    @property
    def is_completed(self) -> bool:
        """Check if WIP completed all processes (1-6).

        Returns:
            True if status is COMPLETED, False otherwise
        """
        return self.status == WIPStatus.COMPLETED.value

    @property
    def is_converted(self) -> bool:
        """Check if WIP has been converted to serial number.

        Returns:
            True if status is CONVERTED and serial_id is set, False otherwise
        """
        return self.status == WIPStatus.CONVERTED.value and self.serial_id is not None

    @property
    def is_failed(self) -> bool:
        """Check if WIP has failed quality check.

        Returns:
            True if status is FAILED, False otherwise
        """
        return self.status == WIPStatus.FAILED.value

    def can_start_process(self, process_number: int) -> bool:
        """Check if WIP can start a specific process.

        Business Rule BR-003: Process can only start if:
        - First process: WIP must be CREATED, IN_PROGRESS, or FAILED (re-work)
        - Subsequent processes: Previous process must be PASS

        Note: Actual process count is determined dynamically by active MANUFACTURING
        processes in the database. This method only performs basic status checks.
        FAILED status is allowed for re-work (착공 재시도).

        Args:
            process_number: Process number to check (must be >= 1)

        Returns:
            True if WIP can start the process, False otherwise
        """
        if process_number < 1:
            return False

        # Only CONVERTED status blocks new processes
        if self.status == WIPStatus.CONVERTED.value:
            return False

        # First process can start if WIP is CREATED, IN_PROGRESS, or FAILED (re-work)
        if process_number == 1:
            return self.status in (WIPStatus.CREATED.value, WIPStatus.IN_PROGRESS.value, WIPStatus.FAILED.value)

        # For subsequent processes, check if WIP is IN_PROGRESS or FAILED (re-work)
        # Detailed validation (previous process PASS) is done in the service layer
        return self.status in (WIPStatus.IN_PROGRESS.value, WIPStatus.FAILED.value)

    def can_convert_to_serial(self) -> bool:
        """Check if WIP can be converted to serial number.

        Business Rule BR-005: WIP can only be converted if all MANUFACTURING
        processes are PASS. The actual process count is determined dynamically
        in the service layer based on active MANUFACTURING processes.

        Returns:
            True if WIP status allows conversion, False otherwise
        """
        return self.status == WIPStatus.COMPLETED.value

    def to_dict(self) -> dict:
        """Convert WIPItem instance to dictionary.

        Returns:
            Dictionary representation of WIP item with all fields
        """
        return {
            "id": self.id,
            "wip_id": self.wip_id,
            "lot_id": self.lot_id,
            "sequence_in_lot": self.sequence_in_lot,
            "status": self.status,
            "current_process_id": self.current_process_id,
            "serial_id": self.serial_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
        }
