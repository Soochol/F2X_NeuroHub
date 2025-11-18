"""
Process data model for PySide6 MES application.

This module provides Pydantic models for Process entity validation and serialization,
mirroring the backend FastAPI schemas. Includes process definition and quality criteria.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class ProcessBase(BaseModel):
    """
    Base schema for Process with core fields and validation.

    Attributes:
        process_number: Process sequence number (1-8)
        process_code: Unique code identifier (e.g., 'LASER_MARKING')
        process_name_ko: Process name in Korean
        process_name_en: Process name in English
        description: Detailed description (optional)
        estimated_duration_seconds: Expected duration in seconds (optional)
        quality_criteria: JSONB field with quality standards
        is_active: Whether process is currently in use
        sort_order: Display sort order for UI
    """
    process_number: int = Field(..., ge=1, le=8)
    process_code: str
    process_name_ko: str
    process_name_en: str
    description: Optional[str] = None
    estimated_duration_seconds: Optional[int] = None
    quality_criteria: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = Field(..., gt=0)

    @field_validator('process_code')
    @classmethod
    def validate_process_code(cls, v: str) -> str:
        """Validate and uppercase process code."""
        if not v:
            raise ValueError("process_code cannot be empty")
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError(
                "process_code can only contain alphanumeric characters and underscores"
            )
        return v.upper()

    @field_validator('quality_criteria')
    @classmethod
    def validate_quality_criteria(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate quality_criteria field as dict."""
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("quality_criteria must be a dictionary")
        return v


class ProcessInDB(ProcessBase):
    """
    Schema for Process database response with all fields.

    Attributes:
        id: Primary key identifier
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
