"""
Manual Control API Schema Definitions.

Defines request/response models for manual hardware control and
command introspection endpoints.
All responses use camelCase field names in JSON output via APIBaseModel.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from station_service.api.schemas.base import APIBaseModel


class ParameterInfo(APIBaseModel):
    """Parameter definition for a hardware command."""

    name: str = Field(..., description="Parameter name")
    display_name: str = Field(..., description="Display name for UI")
    type: str = Field(..., description="Parameter type: string, number, boolean, select")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not required")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    min: Optional[float] = Field(None, description="Minimum value for numbers")
    max: Optional[float] = Field(None, description="Maximum value for numbers")
    options: Optional[List[Dict[str, Any]]] = Field(
        None, description="Options for select type"
    )
    description: Optional[str] = Field(None, description="Parameter description")


class CommandInfo(APIBaseModel):
    """Hardware command information."""

    name: str = Field(..., description="Command/method name")
    display_name: str = Field(..., description="Display name for UI")
    description: str = Field("", description="Command description")
    category: str = Field(
        "diagnostic",
        description="Category: measurement, control, configuration, diagnostic",
    )
    parameters: List[ParameterInfo] = Field(
        default_factory=list, description="Command parameters"
    )
    return_type: str = Field("Any", description="Return type")
    return_unit: Optional[str] = Field(None, description="Unit of return value")
    is_async: bool = Field(True, serialization_alias="async", description="Whether command is async")


class HardwareCommandsResponse(APIBaseModel):
    """Response containing available commands for a hardware device."""

    hardware_id: str = Field(..., description="Hardware device ID")
    driver: str = Field(..., description="Driver class name")
    connected: bool = Field(..., description="Whether device is connected")
    commands: List[CommandInfo] = Field(..., description="Available commands")


class HardwareDetailedStatus(APIBaseModel):
    """Detailed hardware status information."""

    id: str = Field(..., description="Hardware device ID")
    driver: str = Field(..., description="Driver class name")
    status: str = Field(..., description="Connection status")
    connected: bool = Field(..., description="Whether connected")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration")
    info: Dict[str, Any] = Field(default_factory=dict, description="Device info")
    last_error: Optional[str] = Field(None, description="Last error message")


class ManualStepConfig(APIBaseModel):
    """Manual mode configuration for a sequence step."""

    skippable: bool = Field(True, description="Can be skipped in manual mode")
    auto_only: bool = Field(False, description="Only runs in automatic mode")
    prompt: Optional[str] = Field(None, description="Confirmation prompt")
    pause_before: bool = Field(False, description="Pause before execution")
    pause_after: bool = Field(False, description="Pause after execution")
    parameter_overrides: List[str] = Field(
        default_factory=list, description="Parameters that can be overridden"
    )


class ManualStepInfo(APIBaseModel):
    """Step information for manual sequence execution."""

    name: str = Field(..., description="Step name")
    display_name: str = Field(..., description="Display name")
    order: int = Field(..., description="Execution order")
    timeout: float = Field(60.0, description="Timeout in seconds")
    manual: ManualStepConfig = Field(
        default_factory=ManualStepConfig, description="Manual mode config"
    )
    status: str = Field("pending", description="Current status")
    result: Optional[Dict[str, Any]] = Field(None, description="Step result")
    duration: Optional[float] = Field(None, description="Execution duration")


class ManualStepRequest(APIBaseModel):
    """Request body for manual step execution."""

    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameter overrides for the step"
    )


class CommandPreset(APIBaseModel):
    """Saved command preset for quick access."""

    id: str = Field(..., description="Preset ID")
    name: str = Field(..., description="Preset name")
    hardware_id: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    created_at: str = Field(..., description="Creation timestamp")


class CommandPresetCreate(APIBaseModel):
    """Request body for creating a command preset."""

    name: str = Field(..., description="Preset name")
    hardware_id: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
