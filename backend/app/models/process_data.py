"""
SQLAlchemy 2.0 ORM model for the ProcessData entity.

This module provides the ProcessData model representing process execution records
in the F2X NeuroHub MES (Manufacturing Execution System). It captures measurements,
test results, operator information, and timing data for each process execution,
linking serials/LOTs to processes with detailed JSONB data storage.

ProcessData is the core transactional table that records actual manufacturing process
execution details, enabling comprehensive quality tracking and process analysis.

Database table: process_data
Primary key: id (BIGSERIAL)
Foreign keys:
    - lot_id -> lots.id
    - serial_id -> serials.id (nullable for LOT-level data)
    - process_id -> processes.id
    - operator_id -> users.id
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    BIGINT,
    VARCHAR,
    TEXT,
    INTEGER,
    TIMESTAMP,
    CheckConstraint,
    Index,
    ForeignKey,
    Enum as SQLEnum,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict, JSONBList


class DataLevel(str, Enum):
    """
    Data granularity level enumeration.

    Attributes:
        LOT: LOT-level process (serial_id is NULL)
        SERIAL: Per-unit/serial-level process (serial_id is NOT NULL)
    """
    LOT = "LOT"
    SERIAL = "SERIAL"
    WIP = "WIP"


class ProcessResult(str, Enum):
    """
    Process execution result enumeration.

    Attributes:
        PASS: Process execution successful, quality criteria met
        FAIL: Process failed, quality check failure detected
        REWORK: Retry after failure (not currently used in check constraint but documented)
    """
    PASS = "PASS"
    FAIL = "FAIL"
    REWORK = "REWORK"


class ProcessData(Base):
    """
    ORM model for process execution records (공정 실행 데이터).

    Captures actual measurements, test results, operator information, and timing
    for each process execution. This is the core transactional table linking
    serials/LOTs to processes with detailed JSONB measurement and defect data.

    Table: process_data
    Primary Key: id (BIGSERIAL)
    Foreign Keys:
        - lot_id -> lots.id (required, ON DELETE RESTRICT, ON UPDATE CASCADE)
        - serial_id -> serials.id (nullable for LOT-level, ON DELETE RESTRICT, ON UPDATE CASCADE)
        - process_id -> processes.id (required, ON DELETE RESTRICT, ON UPDATE CASCADE)
        - operator_id -> users.id (required, ON DELETE RESTRICT, ON UPDATE CASCADE)

    Attributes:
        id: Primary key, auto-incrementing BIGSERIAL
        lot_id: Foreign key reference to lots table (required)
        serial_id: Foreign key reference to serials table (NULL for LOT-level data)
        process_id: Foreign key reference to processes table
        operator_id: Foreign key reference to users table (operator who performed process)
        data_level: Data granularity: LOT (LOT-level) or SERIAL (per-unit)
        result: Process result: PASS (successful), FAIL (quality failure)
        measurements: Process-specific measurement data in JSONB format (indexed with GIN)
        defects: Defect information array if result=FAIL in JSONB format (indexed with GIN)
        notes: Additional comments or observations from operator
        started_at: Process execution start timestamp
        completed_at: Process execution completion timestamp (nullable for in-progress)
        duration_seconds: Actual process duration in seconds (auto-calculated)
        created_at: Record creation timestamp
        lot: Relationship to Lot (many-to-one)
        serial: Relationship to Serial (many-to-one, nullable)
        process: Relationship to Process (many-to-one)
        operator: Relationship to User (many-to-one, operator alias)

    Constraints:
        - Primary Key: pk_process_data (id)
        - Foreign Key: fk_process_data_lot (lot_id → lots.id)
        - Foreign Key: fk_process_data_serial (serial_id → serials.id)
        - Foreign Key: fk_process_data_process (process_id → processes.id)
        - Foreign Key: fk_process_data_operator (operator_id → users.id)
        - Check: data_level IN ('LOT', 'SERIAL')
        - Check: result IN ('PASS', 'FAIL', 'REWORK')
        - Check: serial_id consistency (LOT level → NULL, SERIAL level → NOT NULL)
        - Check: duration_seconds IS NULL OR duration_seconds >= 0
        - Check: completed_at IS NULL OR completed_at >= started_at
        - Unique (Partial): uk_process_data_serial_process (serial_id, process_id)
          WHERE serial_id IS NOT NULL AND result = 'PASS'
        - Unique (Partial): uk_process_data_lot_process (lot_id, process_id)
          WHERE serial_id IS NULL AND data_level = 'LOT' AND result = 'PASS'

    Indexes:
        - idx_process_data_lot: (lot_id)
        - idx_process_data_serial: (serial_id) WHERE serial_id IS NOT NULL
        - idx_process_data_process: (process_id)
        - idx_process_data_operator: (operator_id)
        - idx_process_data_serial_process: (serial_id, process_id, result) WHERE serial_id IS NOT NULL
        - idx_process_data_lot_process: (lot_id, process_id, result)
        - idx_process_data_process_result: (process_id, result, started_at)
        - idx_process_data_started_at: (started_at DESC)
        - idx_process_data_completed_at: (completed_at DESC) WHERE completed_at IS NOT NULL
        - idx_process_data_failed: (process_id, started_at) WHERE result = 'FAIL'
        - idx_process_data_measurements: GIN index on measurements JSONB
        - idx_process_data_defects: GIN index on defects JSONB
        - idx_process_data_data_level: (data_level, lot_id)
        - idx_process_data_operator_performance: (operator_id, process_id, result, started_at)

    Database Triggers (PostgreSQL side):
        - trg_process_data_calculate_duration: Auto-calculates duration_seconds
        - trg_process_data_validate_sequence: Enforces process sequence
        - trg_process_data_update_serial_status: Updates serial status
        - trg_process_data_audit: Audit logging
    """

    __tablename__ = "process_data"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Foreign Keys
    lot_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("lots.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    serial_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey("serials.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        default=None,
    )

    wip_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey("wip_items.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        default=None,
        comment="Foreign key reference to wip_items table (for processes 1-6)",
    )

    process_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("processes.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    operator_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    # Equipment foreign key - links process execution to specific equipment
    equipment_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey("equipment.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        default=None,
    )

    # Core Data Columns
    data_level: Mapped[str] = mapped_column(
        VARCHAR(10),
        nullable=False,
    )

    result: Mapped[str] = mapped_column(
        VARCHAR(10),
        nullable=False,
    )

    # JSONB Measurement and Defect Data
    measurements: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
    )

    defects: Mapped[Optional[list]] = mapped_column(
        JSONBList,
        nullable=True,
        default=list,
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        TEXT,
        nullable=True,
        default=None,
    )

    # Timing Columns
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
    )

    duration_seconds: Mapped[Optional[int]] = mapped_column(
        INTEGER,
        nullable=True,
        default=None,
    )

    # Timestamp Columns
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    # Relationships
    lot: Mapped["Lot"] = relationship(
        "Lot",
        back_populates="process_data_records",
        foreign_keys=[lot_id],
        lazy="select",
    )

    serial: Mapped[Optional["Serial"]] = relationship(
        "Serial",
        back_populates="process_data_records",
        foreign_keys=[serial_id],
        lazy="select",
    )

    wip_item: Mapped[Optional["WIPItem"]] = relationship(
        "WIPItem",
        foreign_keys=[wip_id],
        lazy="select",
    )

    process: Mapped["Process"] = relationship(
        "Process",
        back_populates="process_data_records",
        foreign_keys=[process_id],
        lazy="select",
    )

    operator: Mapped["User"] = relationship(
        "User",
        back_populates="process_data_records",
        foreign_keys=[operator_id],
        lazy="select",
    )

    equipment: Mapped[Optional["Equipment"]] = relationship(
        "Equipment",
        back_populates="process_data_records",
        foreign_keys=[equipment_id],
        lazy="select",
    )

    # Table Arguments: Constraints and Indexes
    __table_args__ = (
        # CHECK CONSTRAINTS
        CheckConstraint(
            "data_level IN ('LOT', 'WIP', 'SERIAL')",
            name="chk_process_data_data_level"
        ),
        CheckConstraint(
            "result IN ('PASS', 'FAIL', 'REWORK')",
            name="chk_process_data_result"
        ),
        CheckConstraint(
            "(data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR "
            "(data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR "
            "(data_level = 'SERIAL' AND serial_id IS NOT NULL)",
            name="chk_process_data_wip_serial_consistency"
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="chk_process_data_duration"
        ),
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="chk_process_data_timestamps"
        ),

        # FOREIGN KEY INDEXES
        Index(
            "idx_process_data_lot",
            lot_id,
        ),
        Index(
            "idx_process_data_serial",
            serial_id,
        ),
        Index(
            "idx_process_data_wip",
            wip_id,
        ),
        Index(
            "idx_process_data_process",
            process_id,
        ),
        Index(
            "idx_process_data_operator",
            operator_id,
        ),
        Index(
            "idx_process_data_equipment",
            equipment_id,
        ),

        # COMPOSITE INDEXES FOR COMMON QUERIES
        Index(
            "idx_process_data_serial_process",
            serial_id,
            process_id,
            result,
        ),
        Index(
            "idx_process_data_lot_process",
            lot_id,
            process_id,
            result,
        ),
        Index(
            "idx_process_data_process_result",
            process_id,
            result,
            started_at,
        ),

        # TIME-BASED INDEXES FOR ANALYTICS
        Index(
            "idx_process_data_started_at",
            "started_at"
        ),
        Index(
            "idx_process_data_completed_at",
            "completed_at"
        ),

        # SPECIALIZED INDEXES
        Index(
            "idx_process_data_failed",
            process_id,
            started_at,
        ),

        # JSONB GIN INDEXES FOR EFFICIENT JSON QUERYING
        Index(
            "idx_process_data_measurements",
            measurements,
        ),
        Index(
            "idx_process_data_defects",
            defects,
        ),

        # DATA LEVEL AND FILTERING INDEXES
        Index(
            "idx_process_data_data_level",
            data_level,
            lot_id,
        ),

        # OPERATOR PERFORMANCE INDEX
        Index(
            "idx_process_data_operator_performance",
            operator_id,
            process_id,
            result,
            started_at,
        ),

        Index(
            "idx_process_data_equipment_utilization",
            equipment_id,
            process_id,
            started_at,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of ProcessData instance."""
        serial_info = f", serial_id={self.serial_id}" if self.serial_id else ""
        return (
            f"<ProcessData(id={self.id}, lot_id={self.lot_id}{serial_info}, "
            f"process_id={self.process_id}, result='{self.result}', "
            f"data_level='{self.data_level}')>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        data_type = f"Serial {self.serial_id}" if self.data_level == "SERIAL" else f"LOT {self.lot_id}"
        return f"ProcessData(id={self.id}, {data_type}, Process {self.process_id}, {self.result})"

    @property
    def is_completed(self) -> bool:
        """
        Check if process execution is completed.

        Returns:
            True if completed_at is set, False otherwise
        """
        return self.completed_at is not None

    @property
    def is_successful(self) -> bool:
        """
        Check if process execution was successful.

        Returns:
            True if result is PASS, False otherwise
        """
        return self.result == ProcessResult.PASS.value

    @property
    def is_failed(self) -> bool:
        """
        Check if process execution failed.

        Returns:
            True if result is FAIL, False otherwise
        """
        return self.result == ProcessResult.FAIL.value

    @property
    def has_defects(self) -> bool:
        """
        Check if defects were recorded.

        Returns:
            True if defects list is not empty, False otherwise
        """
        return bool(self.defects)

    @property
    def defect_count(self) -> int:
        """
        Get count of recorded defects.

        Returns:
            Number of defects in the defects array
        """
        if not self.defects:
            return 0
        return len(self.defects) if isinstance(self.defects, list) else 0

    def to_dict(self) -> dict:
        """
        Convert ProcessData instance to dictionary.

        Returns:
            dict: Dictionary representation of the process data
        """
        return {
            "id": self.id,
            "lot_id": self.lot_id,
            "serial_id": self.serial_id,
            "process_id": self.process_id,
            "operator_id": self.operator_id,
            "equipment_id": self.equipment_id,
            "data_level": self.data_level,
            "result": self.result,
            "measurements": self.measurements,
            "defects": self.defects,
            "notes": self.notes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Type hint imports for forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.equipment import Equipment
    from app.models.lot import Lot
    from app.models.serial import Serial
    from app.models.wip_item import WIPItem
    from app.models.process import Process
    from app.models.user import User
