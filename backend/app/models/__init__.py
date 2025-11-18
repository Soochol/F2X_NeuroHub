"""
SQLAlchemy ORM Models for F2X NeuroHub MES.

This package contains all database models following the schema defined in
database/ddl/02_tables/*.sql

Models:
    - ProductModel: Product definitions and specifications
    - Process: 8 manufacturing processes
    - User: Authentication and authorization
    - Lot: Production batch tracking (max 100 units)
    - Serial: Individual unit tracking with rework support
    - ProcessData: Process execution records with JSONB measurements
    - AuditLog: Immutable audit trail (partitioned by month)
    - Alert: System notifications and alarms

Usage:
    from app.models import ProductModel, Process, User, Lot, Serial, ProcessData, AuditLog, Alert
"""

from app.models.product_model import ProductModel
from app.models.process import Process
from app.models.user import User, UserRole
from app.models.lot import Lot, LotStatus, Shift
from app.models.serial import Serial, SerialStatus
from app.models.process_data import ProcessData, DataLevel, ProcessResult
from app.models.audit_log import AuditLog, AuditAction
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus

__all__ = [
    # Models
    "ProductModel",
    "Process",
    "User",
    "Lot",
    "Serial",
    "ProcessData",
    "AuditLog",
    "Alert",
    # Enums
    "UserRole",
    "LotStatus",
    "Shift",
    "SerialStatus",
    "DataLevel",
    "ProcessResult",
    "AuditAction",
    "AlertType",
    "AlertSeverity",
    "AlertStatus",
]
