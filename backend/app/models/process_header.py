"""
SQLAlchemy 2.0 ORM model for the ProcessHeader entity.

This module provides the ProcessHeader model representing execution sessions
at the station/batch level. It enables tracking of:
- Which station and batch performed a process
- Configuration snapshots (parameters, hardware)
- Aggregated statistics (pass/fail counts)

ProcessHeader bridges the gap between station-level batch execution
and backend process tracking, providing complete traceability.

Database table: process_headers
Primary key: id (BIGSERIAL)
Foreign keys:
    - process_id -> processes.id
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    DateTime,
    CheckConstraint,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict


class HeaderStatus(str, PyEnum):
    """
    Process header status enumeration.

    Attributes:
        OPEN: Header is active, accepting new process executions
        CLOSED: Header is closed, batch execution completed normally
        CANCELLED: Header was cancelled before completion
    """
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class ProcessHeader(Base):
    """
    ORM model for process execution headers (공정 실행 헤더).

    Represents an execution session at the station/batch level, grouping
    multiple WIP/serial process executions under a single header for
    traceability and statistics aggregation.

    Table: process_headers
    Primary Key: id (BIGSERIAL)
    Foreign Keys:
        - process_id -> processes.id (required)

    Attributes:
        id: Primary key, auto-incrementing BIGSERIAL
        station_id: Station identifier from station config
        batch_id: Batch identifier from station_service
        process_id: Foreign key reference to processes table
        sequence_package: Sequence package name (e.g., sensor_inspection)
        sequence_version: Sequence version at execution time
        parameters: Batch parameters snapshot (JSONB)
        hardware_config: Hardware configuration snapshot (JSONB)
        status: Header status (OPEN, CLOSED, CANCELLED)
        opened_at: When the header was opened (batch started)
        closed_at: When the header was closed (batch ended)
        total_count: Total WIP items processed in this header
        pass_count: Number of PASS results
        fail_count: Number of FAIL results
        created_at: Record creation timestamp
        updated_at: Last update timestamp
        process: Relationship to Process (many-to-one)
        process_data_records: Relationship to ProcessData (one-to-many)
        wip_history_records: Relationship to WIPProcessHistory (one-to-many)

    Constraints:
        - status must be 'OPEN', 'CLOSED', or 'CANCELLED'
        - closed_at must be >= opened_at if both set
        - All count fields must be >= 0
        - Unique partial index: one OPEN header per station+batch+process

    Business Rules:
        - A header is created when a batch starts processing for a specific process
        - Multiple WIP items can be processed under the same header
        - Header statistics are auto-updated via database triggers
        - Only one OPEN header per station+batch+process combination
    """

    __tablename__ = "process_headers"

    # Primary Key
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # Station and Batch identification
    station_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Station identifier (from station config)",
    )

    batch_id: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Batch identifier from station_service",
    )

    # Slot ID for UI display order (1-12 per station)
    slot_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Slot ID for UI display order (1-12 per station)",
    )

    # Process reference
    process_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("processes.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="Foreign key to processes table",
    )

    # Sequence information (snapshot at header creation)
    sequence_package: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Sequence package name (e.g., sensor_inspection)",
    )

    sequence_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Sequence version at execution time",
    )

    # Configuration snapshots (JSONB for flexibility)
    parameters: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        server_default=text("'{}'"),
        comment="Batch parameters snapshot",
    )

    hardware_config: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        server_default=text("'{}'"),
        comment="Hardware configuration snapshot",
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=HeaderStatus.OPEN.value,
        server_default=text("'OPEN'"),
        comment="Header status: OPEN, CLOSED, CANCELLED",
    )

    # Timing
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="When the header was opened (batch started)",
    )

    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="When the header was closed (batch ended)",
    )

    # Aggregated statistics (denormalized for performance)
    total_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="Total WIP items processed in this header",
    )

    pass_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="Number of PASS results",
    )

    fail_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
        comment="Number of FAIL results",
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Last update timestamp",
    )

    # Relationships
    process: Mapped["Process"] = relationship(
        "Process",
        foreign_keys=[process_id],
        lazy="select",
    )

    process_data_records: Mapped[List["ProcessData"]] = relationship(
        "ProcessData",
        back_populates="header",
        foreign_keys="ProcessData.header_id",
        lazy="select",
    )

    wip_history_records: Mapped[List["WIPProcessHistory"]] = relationship(
        "WIPProcessHistory",
        back_populates="header",
        foreign_keys="WIPProcessHistory.header_id",
        lazy="select",
    )

    # Table Arguments: Constraints and Indexes
    __table_args__ = (
        # CHECK CONSTRAINTS
        CheckConstraint(
            "status IN ('OPEN', 'CLOSED', 'CANCELLED')",
            name="chk_process_headers_status",
        ),
        CheckConstraint(
            "closed_at IS NULL OR closed_at >= opened_at",
            name="chk_process_headers_timestamps",
        ),
        CheckConstraint(
            "total_count >= 0 AND pass_count >= 0 AND fail_count >= 0",
            name="chk_process_headers_counts",
        ),

        # INDEXES
        Index("idx_process_headers_station", station_id),
        Index("idx_process_headers_batch", batch_id),
        Index("idx_process_headers_process", process_id),
        Index("idx_process_headers_status", status),
        Index("idx_process_headers_opened_at", opened_at),
        Index(
            "idx_process_headers_station_batch_process",
            station_id, batch_id, process_id,
        ),
        # Unique partial index: only one OPEN header per station+batch+process
        Index(
            "uk_process_headers_open",
            station_id, batch_id, process_id,
            unique=True,
            postgresql_where=text("status = 'OPEN'"),
        ),
        # GIN indexes for JSONB
        Index(
            "idx_process_headers_parameters",
            parameters,
            postgresql_using="gin",
        ),
        Index(
            "idx_process_headers_hardware_config",
            hardware_config,
            postgresql_using="gin",
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of ProcessHeader instance."""
        return (
            f"<ProcessHeader(id={self.id}, station_id='{self.station_id}', "
            f"batch_id='{self.batch_id}', process_id={self.process_id}, "
            f"status='{self.status}')>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return (
            f"Header {self.id}: {self.station_id}/{self.batch_id} "
            f"(Process {self.process_id}, {self.status})"
        )

    @property
    def is_open(self) -> bool:
        """Check if header is currently open."""
        return self.status == HeaderStatus.OPEN.value

    @property
    def is_closed(self) -> bool:
        """Check if header is closed."""
        return self.status == HeaderStatus.CLOSED.value

    @property
    def is_cancelled(self) -> bool:
        """Check if header was cancelled."""
        return self.status == HeaderStatus.CANCELLED.value

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.pass_count / self.total_count) * 100.0

    @property
    def fail_rate(self) -> float:
        """Calculate fail rate as percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.fail_count / self.total_count) * 100.0

    @property
    def duration_seconds(self) -> Optional[int]:
        """Calculate duration in seconds if closed."""
        if self.opened_at and self.closed_at:
            delta = self.closed_at - self.opened_at
            return int(delta.total_seconds())
        return None

    def close(self) -> None:
        """Close the header with current timestamp."""
        self.status = HeaderStatus.CLOSED.value
        self.closed_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        """Cancel the header with current timestamp."""
        self.status = HeaderStatus.CANCELLED.value
        self.closed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Convert ProcessHeader instance to dictionary."""
        return {
            "id": self.id,
            "station_id": self.station_id,
            "batch_id": self.batch_id,
            "slot_id": self.slot_id,
            "process_id": self.process_id,
            "sequence_package": self.sequence_package,
            "sequence_version": self.sequence_version,
            "parameters": self.parameters,
            "hardware_config": self.hardware_config,
            "status": self.status,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "total_count": self.total_count,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "pass_rate": self.pass_rate,
            "fail_rate": self.fail_rate,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_summary_dict(self) -> dict:
        """Convert ProcessHeader to summary dictionary (less detail)."""
        return {
            "id": self.id,
            "station_id": self.station_id,
            "batch_id": self.batch_id,
            "slot_id": self.slot_id,
            "process_id": self.process_id,
            "status": self.status,
            "total_count": self.total_count,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "pass_rate": self.pass_rate,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


# Type hint imports for forward references
if TYPE_CHECKING:
    from app.models.process import Process
    from app.models.process_data import ProcessData
    from app.models.wip_process_history import WIPProcessHistory
