"""
Sequence-related API schemas for Station Service.

This module defines request and response schemas for sequence package operations.
All responses use camelCase field names in JSON output via APIBaseModel.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from station_service.api.schemas.base import APIBaseModel


# ============================================================================
# Nested Models for Sequence Detail
# ============================================================================


class HardwareConfigSchema(APIBaseModel):
    """Schema definition for a hardware configuration field.

    Attributes:
        type: Data type (string, integer, float, boolean)
        required: Whether the field is required
        default: Default value if not specified
    """
    type: str = Field(..., description="Data type")
    required: Optional[bool] = Field(False, description="Whether the field is required")
    default: Optional[Any] = Field(None, description="Default value")


class HardwareDefinition(APIBaseModel):
    """Hardware device definition in a sequence package.

    Attributes:
        id: Hardware device identifier
        display_name: Human-readable display name
        driver: Driver module name
        class_name: Driver class name
        description: Hardware description
        config_schema: Configuration schema for this hardware
    """
    id: str = Field(..., description="Hardware device identifier")
    display_name: str = Field(..., description="Human-readable display name")
    driver: str = Field(..., description="Driver module name")
    class_name: str = Field(..., description="Driver class name")
    description: Optional[str] = Field(None, description="Hardware description")
    config_schema: Dict[str, HardwareConfigSchema] = Field(
        default_factory=dict,
        description="Configuration schema"
    )


class ParameterDefinition(APIBaseModel):
    """Parameter definition for sequence execution.

    Attributes:
        name: Parameter name
        display_name: Human-readable display name
        type: Data type (string, integer, float, boolean)
        default: Default value
        min: Minimum value (for numeric types)
        max: Maximum value (for numeric types)
        unit: Unit of measurement
        options: Available options (for enum types)
    """
    name: str = Field(..., description="Parameter name")
    display_name: str = Field(..., description="Human-readable display name")
    type: str = Field(..., description="Data type (string, integer, float, boolean)")
    default: Optional[Any] = Field(None, description="Default value")
    min: Optional[float] = Field(None, description="Minimum value")
    max: Optional[float] = Field(None, description="Maximum value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    options: Optional[List[str]] = Field(None, description="Available options for enum types")


class StepDefinition(APIBaseModel):
    """Step definition in a sequence.

    Attributes:
        order: Step execution order (1-based)
        name: Step name (unique within sequence)
        display_name: Human-readable display name
        description: Detailed description of the step
        timeout: Maximum execution time in seconds
        retry: Number of retry attempts on failure
        cleanup: Whether this is a cleanup step (always runs)
        condition: Condition expression for conditional execution
    """
    order: int = Field(..., description="Step execution order (0-based)", ge=0)
    name: str = Field(..., description="Step name")
    display_name: str = Field(..., description="Human-readable display name")
    description: Optional[str] = Field(None, description="Detailed description")
    timeout: int = Field(default=60, description="Maximum execution time in seconds", ge=0)
    retry: int = Field(default=0, description="Number of retry attempts", ge=0)
    cleanup: bool = Field(default=False, description="Whether this is a cleanup step")
    condition: Optional[str] = Field(None, description="Condition expression")


# ============================================================================
# Sequence Response Models
# ============================================================================


class SequenceSummary(APIBaseModel):
    """Summary information for a sequence in list view.

    Attributes:
        name: Sequence package name
        version: Sequence version
        display_name: Human-readable display name
        description: Brief description
        path: Path to the sequence package
        updated_at: Last update timestamp
    """
    name: str = Field(..., description="Sequence package name")
    version: str = Field(..., description="Sequence version")
    display_name: str = Field(..., description="Human-readable display name")
    description: Optional[str] = Field(None, description="Brief description")
    path: str = Field(..., description="Path to the sequence package")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SequenceDetail(APIBaseModel):
    """Detailed information for a sequence package.

    Attributes:
        name: Sequence package name
        version: Sequence version
        display_name: Human-readable display name
        description: Detailed description
        author: Author or team name
        created_at: Creation date
        updated_at: Last update date
        path: Package path
        hardware: List of hardware definitions
        parameters: List of parameter definitions
        steps: List of step definitions
    """
    name: str = Field(..., description="Sequence package name")
    version: str = Field(..., description="Sequence version")
    display_name: str = Field(..., description="Human-readable display name")
    description: Optional[str] = Field(None, description="Detailed description")
    author: Optional[str] = Field(None, description="Author or team name")
    created_at: Optional[str] = Field(None, description="Creation date")
    updated_at: Optional[str] = Field(None, description="Last update date")
    path: Optional[str] = Field(None, description="Package path")
    hardware: List[HardwareDefinition] = Field(default_factory=list, description="Hardware definitions")
    parameters: List[ParameterDefinition] = Field(default_factory=list, description="Parameter definitions")
    steps: List[StepDefinition] = Field(default_factory=list, description="Step definitions")


# ============================================================================
# Sequence Update Request/Response Models
# ============================================================================


class ParameterUpdate(APIBaseModel):
    """Parameter update in sequence modification request.

    Attributes:
        name: Parameter name to update
        default: New default value
    """
    name: str = Field(..., description="Parameter name")
    default: Optional[Any] = Field(None, description="New default value")


class StepUpdate(APIBaseModel):
    """Step update in sequence modification request.

    Attributes:
        name: Step name to update
        order: New execution order
        timeout: New timeout value
    """
    name: str = Field(..., description="Step name")
    order: Optional[int] = Field(None, description="New execution order", ge=1)
    timeout: Optional[int] = Field(None, description="New timeout value", ge=0)


class SequenceUpdateRequest(APIBaseModel):
    """Request body for updating a sequence package.

    Attributes:
        parameters: List of parameter updates
        steps: List of step updates
    """
    parameters: List[ParameterUpdate] = Field(
        default_factory=list,
        description="Parameter updates"
    )
    steps: List[StepUpdate] = Field(
        default_factory=list,
        description="Step updates"
    )


class SequenceUpdateResponse(APIBaseModel):
    """Response for sequence update action.

    Attributes:
        name: Sequence package name
        version: New version after update
        updated_at: Update timestamp
    """
    name: str = Field(..., description="Sequence package name")
    version: str = Field(..., description="New version after update")
    updated_at: datetime = Field(..., description="Update timestamp")
