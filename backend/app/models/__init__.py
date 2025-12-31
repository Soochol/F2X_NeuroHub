"""
SQLAlchemy ORM Models for F2X NeuroHub MES.

This package contains all database models following the schema defined in
database/ddl/02_tables/*.sql

Models:
    - ProductModel: Product definitions and specifications
    - Process: 8 manufacturing processes
    - User: Authentication and authorization
    - Lot: Production batch tracking (max 100 units)
    - WIPItem: Work-In-Progress tracking (processes 1-6)
    - Serial: Individual unit tracking with rework support
    - ProcessData: Process execution records with JSONB measurements
    - WIPProcessHistory: WIP process execution history
    - AuditLog: Immutable audit trail (partitioned by month)
    - Alert: System notifications and alarms
    - ProductionLine: Production line definitions and capacity
    - Equipment: Manufacturing equipment tracking and maintenance
    - ErrorLog: Centralized error logging for monitoring and debugging

Usage:
    from app.models import ProductModel, Process, User, Lot, WIPItem, Serial, ProcessData, WIPProcessHistory, AuditLog, Alert, ProductionLine, Equipment, ErrorLog
"""

from app.models.product_model import ProductModel
from app.models.process import Process
from app.models.user import User, UserRole
from app.models.production_line import ProductionLine
from app.models.equipment import Equipment
from app.models.lot import Lot, LotStatus
from app.models.wip_item import WIPItem, WIPStatus
from app.models.serial import Serial, SerialStatus
from app.models.process_data import ProcessData, DataLevel, ProcessResult
from app.models.wip_process_history import WIPProcessHistory
from app.models.audit_log import AuditLog, AuditAction
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.models.error_log import ErrorLog
from app.models.print_log import PrintLog, PrintStatus

from app.models.saved_filter import SavedFilter
from app.models.refresh_token import RefreshToken
from app.models.station import Station, StationStatus


__all__ = [
    # Models
    "ProductModel",
    "Process",
    "User",
    "Lot",
    "WIPItem",
    "Serial",
    "ProcessData",
    "WIPProcessHistory",
    "AuditLog",
    "Alert",
    "ProductionLine",
    "Equipment",
    "ErrorLog",
    "PrintLog",
    "SavedFilter",
    "RefreshToken",
    "Station",
    # Enums
    "UserRole",
    "LotStatus",
    "WIPStatus",
    "SerialStatus",
    "DataLevel",
    "ProcessResult",
    "AuditAction",
    "AlertType",
    "AlertSeverity",
    "AlertStatus",
    "PrintStatus",
    "StationStatus",
]
