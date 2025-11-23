"""
SQLAlchemy ORM model for the Process entity.

Represents manufacturing processes in the F2X NeuroHub production line.
Each process is a step in the manufacturing workflow (8 total processes).

Database table: processes
Primary key: id (BIGSERIAL)
"""

from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Index,
    String,
    Integer,
    Boolean,
    Text,
    DateTime,
    text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict, is_postgresql


class LabelTemplateType(str, Enum):
    """라벨 템플릿 종류"""
    WIP_LABEL = "WIP_LABEL"          # WIP 라벨 (60x30mm, QR코드)
    SERIAL_LABEL = "SERIAL_LABEL"    # Serial 라벨 (60x30mm, QR코드)
    LOT_LABEL = "LOT_LABEL"          # LOT 라벨 (60x30mm, QR코드)


class Process(Base):
    """
    SQLAlchemy ORM model for manufacturing processes.

    Represents one of the 8 manufacturing processes in the F2X production line.
    Each process has a unique sequence number (1-8), a code identifier, and
    quality criteria in JSONB format.

    Attributes:
        id: Primary key, auto-incrementing BIGSERIAL
        process_number: Process sequence number (1-8), unique and required
        process_code: Unique code identifier (e.g., 'LASER_MARKING')
        process_name_ko: Process name in Korean
        process_name_en: Process name in English
        description: Detailed description of the process
        estimated_duration_seconds: Expected duration in seconds (optional, positive if set)
        quality_criteria: JSONB field storing quality standards and acceptance criteria
        is_active: Whether this process is currently in use (default: True)
        sort_order: Display order (required, must be > 0)
        created_at: Record creation timestamp
        updated_at: Last update timestamp

    Constraints:
        - process_number must be between 1 and 8 (inclusive)
        - process_code must be unique
        - process_number must be unique
        - estimated_duration_seconds must be positive (if specified)
        - sort_order must be positive (> 0)

    Indexes:
        - idx_processes_active: On (is_active, sort_order) for active processes
        - idx_processes_quality_criteria: GIN index on quality_criteria JSONB
        - idx_processes_sort_order: On sort_order for UI display
    """

    __tablename__ = "processes"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Core Columns
    process_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
    )

    process_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    process_name_ko: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    process_name_en: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    estimated_duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    quality_criteria: Mapped[dict] = mapped_column(
        JSONBDict,
        nullable=False,
        default=dict,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Auto Print Label Settings
    auto_print_label: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
        comment="완공 시 자동 라벨 출력 여부"
    )

    label_template_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        comment="출력할 라벨 템플릿 종류 (WIP_LABEL, SERIAL_LABEL, LOT_LABEL)"
    )

    # Timestamp Columns
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    # Relationships
    process_data_records: Mapped[List["ProcessData"]] = relationship(
        "ProcessData",
        back_populates="process",
        cascade="all, delete-orphan"
    )

    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="process",
        cascade="all, delete-orphan"
    )

    # Table Arguments: Constraints and Indexes
    __table_args__ = (
        # CHECK CONSTRAINTS
        CheckConstraint(
            "process_number >= 1 AND process_number <= 8",
            name="chk_processes_process_number",
        ),
        CheckConstraint(
            "estimated_duration_seconds IS NULL OR estimated_duration_seconds > 0",
            name="chk_processes_duration",
        ),
        CheckConstraint(
            "sort_order > 0",
            name="chk_processes_sort_order",
        ),
        # INDEXES
        Index(
            "idx_processes_active",
            is_active,
            sort_order
        ),
        Index(
            "idx_processes_quality_criteria",
            quality_criteria
        ),
        Index(
            "idx_processes_sort_order",
            sort_order
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of Process instance."""
        return (
            f"<Process(id={self.id}, number={self.process_number}, "
            f"code='{self.process_code}', name_en='{self.process_name_en}')>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.process_number}. {self.process_name_en} ({self.process_code})"

    def to_dict(self) -> dict:
        """
        Convert Process instance to dictionary.

        Returns:
            dict: Dictionary representation of the process
        """
        return {
            "id": self.id,
            "process_number": self.process_number,
            "process_code": self.process_code,
            "process_name_ko": self.process_name_ko,
            "process_name_en": self.process_name_en,
            "description": self.description,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "quality_criteria": self.quality_criteria,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "auto_print_label": self.auto_print_label,
            "label_template_type": self.label_template_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

