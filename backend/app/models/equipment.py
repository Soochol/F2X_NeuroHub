"""
SQLAlchemy ORM model for the Equipment entity.

Represents manufacturing equipment in the F2X NeuroHub production facility.
Each piece of equipment can be associated with a process and production line,
with maintenance tracking capabilities.

Database table: equipment
Primary key: id (BIGINT)
"""

from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict


class Equipment(Base):
    """
    SQLAlchemy ORM model for manufacturing equipment.

    Represents a piece of manufacturing equipment in the facility.
    Equipment can be linked to specific processes and production lines,
    with tracking for maintenance schedules and manufacturer information.

    Attributes:
        id: Primary key, auto-incrementing BIGINT
        equipment_code: Unique equipment identifier (e.g., 'EQ_LASER_001')
        equipment_name: Display name (e.g., '레이저마킹기-001')
        equipment_type: Type classification (e.g., 'LASER_MARKER', 'SENSOR', 'ROBOT')
        description: Equipment description and details
        process_id: Foreign key to processes table (primary process)
        production_line_id: Foreign key to production_lines table
        manufacturer: Equipment manufacturer name
        model_number: Manufacturer's model number
        serial_number: Equipment serial number
        status: Equipment status (AVAILABLE, IN_USE, MAINTENANCE, OUT_OF_SERVICE, RETIRED)
        is_active: Whether equipment is currently operational (default: True)
        last_maintenance_date: Last maintenance date
        next_maintenance_date: Scheduled next maintenance date
        total_operation_hours: Total hours of operation
        specifications: Technical specifications in JSONB format
        maintenance_schedule: Maintenance schedule and procedures in JSONB format
        created_at: Record creation timestamp
        updated_at: Last update timestamp

    Constraints:
        - equipment_code must be unique
        - status must be one of: AVAILABLE, IN_USE, MAINTENANCE, OUT_OF_SERVICE, RETIRED
        - total_operation_hours must be non-negative
        - next_maintenance_date must be after last_maintenance_date

    Indexes:
        - idx_equipment_active: On (is_active, status) for active equipment
        - idx_equipment_process: On (process_id) for process queries
        - idx_equipment_production_line: On (production_line_id) for line queries
        - idx_equipment_status: On (status) for status filtering
        - idx_equipment_type: On (equipment_type) for type filtering
        - idx_equipment_maintenance_schedule: On (next_maintenance_date) for scheduling
        - idx_equipment_utilization: Composite index for utilization analysis
        - idx_equipment_specifications: GIN index for JSONB specifications
        - idx_equipment_maintenance_schedule_json: GIN index for JSONB maintenance_schedule
    """

    __tablename__ = "equipment"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Core Columns
    equipment_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique equipment identifier (e.g., 'EQ_LASER_001')",
    )

    equipment_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Display name (e.g., '레이저마킹기-001')",
    )

    equipment_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type classification (e.g., 'LASER_MARKER', 'SENSOR', 'ROBOT')",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Equipment description and details",
    )

    # Foreign Keys
    process_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("processes.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="Primary process this equipment is used for",
    )

    production_line_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("production_lines.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="Production line where equipment is located",
    )

    # Manufacturer Information
    manufacturer: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Equipment manufacturer name",
    )

    model_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Manufacturer's model number",
    )

    serial_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Equipment serial number",
    )

    # Status and Availability
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="AVAILABLE",
        server_default=text("'AVAILABLE'"),
        comment="Equipment status: AVAILABLE, IN_USE, MAINTENANCE, OUT_OF_SERVICE, RETIRED",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("TRUE"),
        comment="Whether equipment is currently operational",
    )

    # Maintenance Tracking (DATE type, not DateTime)
    last_maintenance_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Last maintenance date",
    )

    next_maintenance_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Scheduled next maintenance date",
    )

    # Utilization Tracking
    total_operation_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=0,
        server_default=text("0"),
        comment="Total hours of operation",
    )

    # Configuration (JSONB)
    specifications: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        server_default=text("'{}'"),
        comment="Technical specifications in JSONB format",
    )

    maintenance_schedule: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        server_default=text("'{}'"),
        comment="Maintenance schedule and procedures in JSONB format",
    )

    # Timestamp Columns
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
    process: Mapped[Optional["Process"]] = relationship(
        "Process",
        foreign_keys=[process_id],
    )

    production_line: Mapped[Optional["ProductionLine"]] = relationship(
        "ProductionLine",
        back_populates="equipment",
        foreign_keys=[production_line_id],
    )

    process_data_records: Mapped[list["ProcessData"]] = relationship(
        "ProcessData",
        back_populates="equipment",
        foreign_keys="ProcessData.equipment_id",
    )

    # Table Arguments: Indexes
    # Note: Most indexes are created in DDL, but we define key ones here for reference
    __table_args__ = (
        Index(
            "idx_equipment_code",
            equipment_code,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of Equipment instance."""
        return (
            f"<Equipment(id={self.id}, code='{self.equipment_code}', "
            f"type='{self.equipment_type}', status='{self.status}', active={self.is_active})>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.equipment_code}: {self.equipment_name}"

    def to_dict(self) -> dict:
        """
        Convert Equipment instance to dictionary.

        Returns:
            dict: Dictionary representation of the equipment
        """
        return {
            "id": self.id,
            "equipment_code": self.equipment_code,
            "equipment_name": self.equipment_name,
            "equipment_type": self.equipment_type,
            "description": self.description,
            "process_id": self.process_id,
            "production_line_id": self.production_line_id,
            "manufacturer": self.manufacturer,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "status": self.status,
            "is_active": self.is_active,
            "last_maintenance_date": self.last_maintenance_date,
            "next_maintenance_date": self.next_maintenance_date,
            "total_operation_hours": float(self.total_operation_hours) if self.total_operation_hours else None,
            "specifications": self.specifications,
            "maintenance_schedule": self.maintenance_schedule,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @property
    def needs_maintenance(self) -> bool:
        """Check if equipment needs maintenance.

        Returns:
            True if next_maintenance_date is in the past, False otherwise
        """
        if self.next_maintenance_date is None:
            return False
        return date.today() >= self.next_maintenance_date


# Type hint imports for forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.process import Process
    from app.models.process_data import ProcessData
    from app.models.production_line import ProductionLine
