"""
SQLAlchemy ORM model for PrintLog entity.

Tracks all label printing operations including success/failure status,
printer information, and associated process data.

Database table: print_logs
Primary key: id (INTEGER AUTOINCREMENT)
"""

from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from sqlalchemy import (
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PrintStatus(str, Enum):
    """Print job status"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PrintLog(Base):
    """
    SQLAlchemy ORM model for print logs.
    
    Tracks all label printing operations with detailed information
    about the print job, printer, and results.
    
    Attributes:
        id: Primary key
        label_type: Type of label (WIP_LABEL, SERIAL_LABEL, LOT_LABEL)
        label_id: ID of the printed label (e.g., WIP-XXX-001)
        process_id: Associated process ID (optional)
        process_data_id: Associated process data ID (optional)
        printer_ip: IP address of the printer
        printer_port: Port number of the printer
        status: Print job status (SUCCESS/FAILED)
        error_message: Error message if failed
        operator_id: User who triggered the print (optional)
        created_at: Timestamp of print operation
    """
    
    __tablename__ = "print_logs"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Label Information
    label_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Label template type (WIP_LABEL, SERIAL_LABEL, LOT_LABEL)"
    )
    
    label_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="ID of the printed label"
    )
    
    # Process Information
    process_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("processes.id"),
        nullable=True,
        comment="Associated process ID"
    )
    
    process_data_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("process_data.id"),
        nullable=True,
        comment="Associated process data ID"
    )
    
    # Printer Information
    printer_ip: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Printer IP address"
    )
    
    printer_port: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Printer port number"
    )
    
    # Result
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Print status (SUCCESS/FAILED)"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if print failed"
    )
    
    # Metadata
    operator_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="User who triggered the print"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Print timestamp"
    )
    
    # Relationships
    process: Mapped[Optional["Process"]] = relationship(
        "Process",
        foreign_keys=[process_id]
    )
    
    process_data: Mapped[Optional["ProcessData"]] = relationship(
        "ProcessData",
        foreign_keys=[process_data_id]
    )
    
    operator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[operator_id]
    )
    
    # Table Arguments: Indexes
    __table_args__ = (
        Index("idx_print_logs_label_type", label_type),
        Index("idx_print_logs_created_at", created_at),
        Index("idx_print_logs_status", status),
    )
    
    def __repr__(self) -> str:
        """Return string representation of PrintLog instance."""
        return (
            f"<PrintLog(id={self.id}, type='{self.label_type}', "
            f"label_id='{self.label_id}', status='{self.status}')>"
        )
    
    def to_dict(self) -> dict:
        """
        Convert PrintLog instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the print log
        """
        return {
            "id": self.id,
            "label_type": self.label_type,
            "label_id": self.label_id,
            "process_id": self.process_id,
            "process_data_id": self.process_data_id,
            "printer_ip": self.printer_ip,
            "printer_port": self.printer_port,
            "status": self.status,
            "error_message": self.error_message,
            "operator_id": self.operator_id,
            "created_at": self.created_at,
        }
