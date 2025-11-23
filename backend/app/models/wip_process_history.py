"""
SQLAlchemy 2.0 ORM model for the WIP Process History entity.

This module provides the WIPProcessHistory model representing process execution
records for WIP items in the F2X NeuroHub MES. It captures measurements, test
results, operator information, and timing data for each WIP process execution
(processes 1-6 only).

Database table: wip_process_history
Primary key: id (BIGSERIAL)
Foreign keys:
    - wip_item_id -> wip_items.id
    - process_id -> processes.id
    - operator_id -> users.id
    - equipment_id -> equipment.id (nullable)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    BIGINT,
    VARCHAR,
    TEXT,
    INTEGER,
    TIMESTAMP,
    CheckConstraint,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict, JSONBList

if TYPE_CHECKING:
    from app.models.wip_item import WIPItem
    from app.models.process import Process
    from app.models.user import User
    from app.models.equipment import Equipment


class ProcessResult(str, Enum):
    """
    Process execution result enumeration.

    Attributes:
        PASS: Process execution successful, quality criteria met
        FAIL: Process failed, quality check failure detected
        REWORK: Process failed but approved for rework attempt
    """
    PASS = "PASS"
    FAIL = "FAIL"
    REWORK = "REWORK"


class WIPProcessHistory(Base):
    """
    ORM model for WIP process execution records.

    Captures actual measurements, test results, operator information, and timing
    for each WIP process execution (processes 1-6). This is similar to ProcessData
    but specifically for WIP tracking before serial conversion.

    Table: wip_process_history
    Primary Key: id (BIGSERIAL)
    Foreign Keys:
        - wip_item_id -> wip_items.id (required)
        - process_id -> processes.id (required)
        - operator_id -> users.id (required)
        - equipment_id -> equipment.id (nullable)

    Attributes:
        id: Primary key, auto-incrementing BIGSERIAL
        wip_item_id: Foreign key reference to wip_items table
        process_id: Foreign key reference to processes table
        operator_id: Foreign key reference to users table (operator who performed process)
        equipment_id: Foreign key reference to equipment table (nullable)
        result: Process result (PASS or FAIL)
        measurements: Process-specific measurement data in JSONB format
        defects: Defect information array if result=FAIL in JSONB format
        notes: Additional comments or observations from operator
        started_at: Process execution start timestamp
        completed_at: Process execution completion timestamp
        duration_seconds: Actual process duration in seconds (auto-calculated)
        created_at: Record creation timestamp
        wip_item: Relationship to WIPItem (many-to-one)
        process: Relationship to Process (many-to-one)
        operator: Relationship to User (many-to-one)
        equipment: Relationship to Equipment (many-to-one, nullable)

    Constraints:
        - result must be 'PASS' or 'FAIL'
        - duration_seconds must be >= 0 if set
        - completed_at must be >= started_at if both set
        - Unique: (wip_item_id, process_id, result='PASS') - prevent duplicate PASS for same process

    Indexes:
        - idx_wip_history_wip_item: (wip_item_id)
        - idx_wip_history_process: (process_id)
        - idx_wip_history_operator: (operator_id)
        - idx_wip_history_equipment: (equipment_id)
        - idx_wip_history_wip_process: (wip_item_id, process_id, result)
        - idx_wip_history_started_at: (started_at DESC)
        - idx_wip_history_failed: (process_id, started_at) WHERE result = 'FAIL'
        - idx_wip_history_measurements: GIN index on measurements JSONB
        - idx_wip_history_defects: GIN index on defects JSONB
    """

    __tablename__ = "wip_process_history"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Foreign Keys
    wip_item_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("wip_items.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="Foreign key reference to wip_items table",
    )

    process_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("processes.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="Foreign key reference to processes table",
    )

    operator_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="Foreign key reference to users table (operator)",
    )

    equipment_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey("equipment.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        default=None,
        comment="Foreign key reference to equipment table (nullable)",
    )

    # Core Data Columns
    result: Mapped[str] = mapped_column(
        VARCHAR(10),
        nullable=False,
        comment="Process result: PASS (successful) or FAIL (quality failure)",
    )

    # JSONB Measurement and Defect Data
    measurements: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        comment="Process-specific measurement data in JSONB format",
    )

    defects: Mapped[Optional[list]] = mapped_column(
        JSONBList,
        nullable=True,
        default=list,
        comment="Defect information array if result=FAIL in JSONB format",
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True,
        default=None,
        comment="Additional comments or observations from operator",
    )

    # Timing Columns
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        comment="Process execution start timestamp",
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        comment="Process execution completion timestamp",
    )

    duration_seconds: Mapped[Optional[int]] = mapped_column(
        INTEGER,
        nullable=True,
        default=None,
        comment="Actual process duration in seconds (auto-calculated)",
    )

    # Timestamp Columns
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Record creation timestamp",
    )

    # Relationships
    wip_item: Mapped["WIPItem"] = relationship(
        "WIPItem",
        back_populates="process_history",
        foreign_keys=[wip_item_id],
        lazy="select",
    )

    process: Mapped["Process"] = relationship(
        "Process",
        foreign_keys=[process_id],
        lazy="select",
    )

    operator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[operator_id],
        lazy="select",
    )

    equipment: Mapped[Optional["Equipment"]] = relationship(
        "Equipment",
        foreign_keys=[equipment_id],
        lazy="select",
    )

    # Table Arguments: Constraints and Indexes
    __table_args__ = (
        # CHECK CONSTRAINTS
        CheckConstraint(
            "result IN ('PASS', 'FAIL')",
            name="chk_wip_history_result",
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="chk_wip_history_duration",
        ),
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="chk_wip_history_timestamps",
        ),

        # UNIQUE CONSTRAINT: Prevent duplicate PASS for same WIP + Process
        # (Only one PASS result per WIP per process - BR-004)
        Index(
            "uk_wip_history_wip_process_pass",
            wip_item_id,
            process_id,
            unique=True,
            postgresql_where=text("result = 'PASS'"),
        ),

        # FOREIGN KEY INDEXES
        Index(
            "idx_wip_history_wip_item",
            wip_item_id,
        ),
        Index(
            "idx_wip_history_process",
            process_id,
        ),
        Index(
            "idx_wip_history_operator",
            operator_id,
        ),
        Index(
            "idx_wip_history_equipment",
            equipment_id,
        ),

        # COMPOSITE INDEXES FOR COMMON QUERIES
        Index(
            "idx_wip_history_wip_process",
            wip_item_id,
            process_id,
            result,
        ),

        # TIME-BASED INDEXES FOR ANALYTICS
        Index(
            "idx_wip_history_started_at",
            "started_at",
        ),

        # SPECIALIZED INDEXES
        Index(
            "idx_wip_history_failed",
            process_id,
            started_at,
            postgresql_where=text("result = 'FAIL'"),
        ),

        # JSONB GIN INDEXES FOR EFFICIENT JSON QUERYING
        Index(
            "idx_wip_history_measurements",
            measurements,
            postgresql_using="gin",
        ),
        Index(
            "idx_wip_history_defects",
            defects,
            postgresql_using="gin",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of WIPProcessHistory instance."""
        return (
            f"<WIPProcessHistory(id={self.id}, wip_item_id={self.wip_item_id}, "
            f"process_id={self.process_id}, result='{self.result}')>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"WIP Process History (WIP {self.wip_item_id}, Process {self.process_id}, {self.result})"

    @property
    def is_completed(self) -> bool:
        """Check if process execution is completed.

        Returns:
            True if completed_at is set, False otherwise
        """
        return self.completed_at is not None

    @property
    def is_successful(self) -> bool:
        """Check if process execution was successful.

        Returns:
            True if result is PASS, False otherwise
        """
        return self.result == ProcessResult.PASS.value

    @property
    def is_failed(self) -> bool:
        """Check if process execution failed.

        Returns:
            True if result is FAIL, False otherwise
        """
        return self.result == ProcessResult.FAIL.value

    @property
    def has_defects(self) -> bool:
        """Check if defects were recorded.

        Returns:
            True if defects list is not empty, False otherwise
        """
        return bool(self.defects)

    @property
    def defect_count(self) -> int:
        """Get count of recorded defects.

        Returns:
            Number of defects in the defects array
        """
        if not self.defects:
            return 0
        return len(self.defects) if isinstance(self.defects, list) else 0

    def calculate_duration(self) -> Optional[int]:
        """Calculate duration in seconds from timestamps.

        Returns:
            Duration in seconds if both timestamps are set, None otherwise
        """
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds())
        return None

    def to_dict(self) -> dict:
        """Convert WIPProcessHistory instance to dictionary.

        Returns:
            Dictionary representation of the process history record
        """
        return {
            "id": self.id,
            "wip_item_id": self.wip_item_id,
            "process_id": self.process_id,
            "operator_id": self.operator_id,
            "equipment_id": self.equipment_id,
            "result": self.result,
            "measurements": self.measurements,
            "defects": self.defects,
            "notes": self.notes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
