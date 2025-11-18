"""
LOT data model for PySide6 MES application.

This module provides Pydantic models for LOT entity validation and serialization,
mirroring the backend FastAPI schemas. Includes LOT lifecycle management, shift
tracking, and quality metrics calculation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class LotStatus(str, Enum):
    """
    LOT lifecycle status enumeration.

    Attributes:
        CREATED: Initial state after LOT creation
        IN_PROGRESS: Production is actively underway
        COMPLETED: All production units finished
        CLOSED: Final state, LOT is archived
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class Shift(str, Enum):
    """
    Production shift enumeration.

    Attributes:
        DAY: Day shift (06:00-18:00)
        NIGHT: Night shift (18:00-06:00)
    """
    DAY = "D"
    NIGHT = "N"


class LotBase(BaseModel):
    """
    Base schema for LOT with core fields and validation.

    Attributes:
        lot_number: Auto-generated LOT identifier (WF-KR-YYMMDD{D|N}-nnn)
        product_model_id: Foreign key to product_models table
        production_date: Scheduled/actual production date
        shift: Production shift (D for Day, N for Night)
        target_quantity: Target production quantity (max 100 units per LOT)
        status: LOT lifecycle status
    """
    lot_number: str = Field(..., pattern=r'^WF-KR-\d{6}[DN]-\d{3}$')
    product_model_id: int = Field(..., gt=0)
    production_date: date
    shift: Shift
    target_quantity: int = Field(..., ge=1, le=100)
    status: LotStatus = LotStatus.CREATED

    @field_validator('shift', mode='before')
    @classmethod
    def validate_shift(cls, v):
        """Convert string to Shift enum if needed."""
        if isinstance(v, str):
            if v.upper() in ('D', 'DAY'):
                return Shift.DAY
            elif v.upper() in ('N', 'NIGHT'):
                return Shift.NIGHT
        return v


class LotCreate(LotBase):
    """
    Schema for creating new LOT records.

    Inherits all validation from LotBase.
    All required fields must be provided on creation.
    """
    pass


class LotInDB(LotBase):
    """
    Schema for LOT database response with relationships and computed fields.

    Attributes:
        id: Primary key identifier
        actual_quantity: Actual units produced in this LOT
        passed_quantity: Number of units that passed all quality checks
        failed_quantity: Number of units that failed quality checks
        created_at: LOT creation timestamp
        updated_at: Last modification timestamp
        closed_at: LOT closure/completion timestamp (optional)
        defect_rate: Calculated defect rate percentage
        pass_rate: Calculated pass rate percentage
    """
    id: int
    actual_quantity: int = 0
    passed_quantity: int = 0
    failed_quantity: int = 0
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    @property
    def defect_rate(self) -> float:
        """Calculate defect rate as percentage."""
        if self.actual_quantity == 0:
            return 0.0
        return round((self.failed_quantity / self.actual_quantity) * 100, 2)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as percentage."""
        if self.actual_quantity == 0:
            return 0.0
        return round((self.passed_quantity / self.actual_quantity) * 100, 2)

    class Config:
        from_attributes = True
