"""
Pydantic Schemas for F2X NeuroHub MES API.

This package contains all Pydantic models for request/response validation.
Each entity has 4 schemas: Base, Create, Update, InDB.

Usage:
    from app.schemas import ProductModelCreate, ProductModelInDB
"""

from app.schemas.product_model import (
    ProductModelBase,
    ProductModelCreate,
    ProductModelUpdate,
    ProductModelInDB,
)
from app.schemas.process import (
    ProcessBase,
    ProcessCreate,
    ProcessUpdate,
    ProcessInDB,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserLogin,
    UserRole,
)
from app.schemas.lot import (
    LotBase,
    LotCreate,
    LotUpdate,
    LotInDB,
)
from app.models.lot import LotStatus, Shift
from app.schemas.serial import (
    SerialBase,
    SerialCreate,
    SerialUpdate,
    SerialInDB,
)
from app.models.serial import SerialStatus
from app.schemas.process_data import (
    ProcessDataBase,
    ProcessDataCreate,
    ProcessDataUpdate,
    ProcessDataInDB,
)
from app.models.process_data import DataLevel, ProcessResult
from app.schemas.audit_log import (
    AuditLogBase,
    AuditLogInDB,
)
from app.models.audit_log import AuditAction
from app.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertUpdate,
    AlertInDB,
    AlertResponse,
    AlertListResponse,
    AlertMarkRead,
    AlertBulkMarkRead,
    AlertType,
    AlertSeverity,
    AlertStatus,
)
from app.schemas.production_line import (
    ProductionLineBase,
    ProductionLineCreate,
    ProductionLineUpdate,
    ProductionLineInDB,
    ProductionLineResponse,
)
from app.schemas.equipment import (
    EquipmentBase,
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentInDB,
    EquipmentResponse,
)

__all__ = [
    # ProductModel schemas
    "ProductModelBase",
    "ProductModelCreate",
    "ProductModelUpdate",
    "ProductModelInDB",
    # Process schemas
    "ProcessBase",
    "ProcessCreate",
    "ProcessUpdate",
    "ProcessInDB",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserLogin",
    "UserRole",
    # Lot schemas
    "LotBase",
    "LotCreate",
    "LotUpdate",
    "LotInDB",
    "LotStatus",
    "Shift",
    # Serial schemas
    "SerialBase",
    "SerialCreate",
    "SerialUpdate",
    "SerialInDB",
    "SerialStatus",
    # ProcessData schemas
    "ProcessDataBase",
    "ProcessDataCreate",
    "ProcessDataUpdate",
    "ProcessDataInDB",
    "DataLevel",
    "ProcessResult",
    # AuditLog schemas (read-only)
    "AuditLogBase",
    "AuditLogInDB",
    "AuditAction",
    # Alert schemas
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertInDB",
    "AlertResponse",
    "AlertListResponse",
    "AlertMarkRead",
    "AlertBulkMarkRead",
    "AlertType",
    "AlertSeverity",
    "AlertStatus",
    # ProductionLine schemas
    "ProductionLineBase",
    "ProductionLineCreate",
    "ProductionLineUpdate",
    "ProductionLineInDB",
    "ProductionLineResponse",
    # Equipment schemas
    "EquipmentBase",
    "EquipmentCreate",
    "EquipmentUpdate",
    "EquipmentInDB",
    "EquipmentResponse",
]
