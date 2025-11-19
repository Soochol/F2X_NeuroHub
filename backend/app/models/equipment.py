"""
SQLAlchemy ORM model for the Equipment entity.

Represents manufacturing equipment in the F2X NeuroHub production facility.
Each piece of equipment can be associated with a process and production line,
with maintenance tracking capabilities.

Database table: equipment
Primary key: id (BIGINT)
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Equipment(Base):
    """
    SQLAlchemy ORM model for manufacturing equipment.

    Represents a piece of manufacturing equipment in the facility.
    Equipment can be linked to specific processes and production lines,
    with tracking for maintenance schedules and manufacturer information.

    Attributes:
        id: Primary key, auto-incrementing BIGINT
        equipment_code: Unique equipment identifier (e.g., 'LASER-001')
        equipment_name: Display name (e.g., '레이저마킹기-001')
        equipment_type: Type classification (e.g., 'LASER_MARKER', 'SENSOR', 'ROBOT')
        process_id: Foreign key to processes table (primary process)
        production_line_id: Foreign key to production_lines table
        location: Physical location within facility
        manufacturer: Equipment manufacturer name
        model_number: Manufacturer's model number
        serial_number: Equipment serial number
        install_date: Date equipment was installed
        last_maintenance_date: Last maintenance timestamp
        next_maintenance_date: Scheduled next maintenance timestamp
        is_active: Whether equipment is currently operational (default: True)
        created_at: Record creation timestamp
        updated_at: Last update timestamp

    Constraints:
        - equipment_code must be unique

    Indexes:
        - idx_equipment_active: On (is_active) for active equipment
        - idx_equipment_code: On (equipment_code) for lookups
        - idx_equipment_type: On (equipment_type) for filtering
        - idx_equipment_process: On (process_id) for process queries
        - idx_equipment_line: On (production_line_id) for line queries
        - idx_equipment_maintenance: On (next_maintenance_date) for scheduling
    """

    __tablename__ = "equipment"

    # Primary Key
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # Core Columns
    equipment_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique equipment identifier (e.g., 'LASER-001')",
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

    # Location and Manufacturer Information
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Physical location within facility",
    )

    manufacturer: Mapped[Optional[str]] = mapped_column(
        String(100),
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

    # Date and Maintenance Tracking
    install_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date equipment was installed",
    )

    last_maintenance_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last maintenance timestamp",
    )

    next_maintenance_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled next maintenance timestamp",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        comment="Whether equipment is currently operational",
    )

    # Timestamp Columns
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
        comment="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("NOW()"),
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

    # NOTE: process_data relationship disabled until process_data.equipment_id is enabled
    # process_data: Mapped[List["ProcessData"]] = relationship(
    #     "ProcessData",
    #     back_populates="equipment",
    # )

    # Table Arguments: Indexes
    __table_args__ = (
        Index(
            "idx_equipment_active",
            is_active,
        ),
        Index(
            "idx_equipment_code",
            equipment_code,
        ),
        Index(
            "idx_equipment_type",
            equipment_type,
        ),
        Index(
            "idx_equipment_process",
            process_id,
        ),
        Index(
            "idx_equipment_line",
            production_line_id,
        ),
        Index(
            "idx_equipment_maintenance",
            next_maintenance_date,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of Equipment instance."""
        return (
            f"<Equipment(id={self.id}, code='{self.equipment_code}', "
            f"type='{self.equipment_type}', active={self.is_active})>"
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
            "process_id": self.process_id,
            "production_line_id": self.production_line_id,
            "location": self.location,
            "manufacturer": self.manufacturer,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "install_date": self.install_date,
            "last_maintenance_date": self.last_maintenance_date,
            "next_maintenance_date": self.next_maintenance_date,
            "is_active": self.is_active,
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
        return datetime.now(self.next_maintenance_date.tzinfo) >= self.next_maintenance_date


# Type hint imports for forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.process import Process
    # from app.models.process_data import ProcessData  # Disabled until relationship is enabled
    from app.models.production_line import ProductionLine
