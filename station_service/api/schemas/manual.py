"""
Manual Control API Schema Definitions.

Defines request/response models for manual hardware control and
command introspection endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParameterInfo(BaseModel):
    """Parameter definition for a hardware command."""

    name: str = Field(..., description="Parameter name")
    displayName: str = Field(..., description="Display name for UI")
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


class CommandInfo(BaseModel):
    """Hardware command information."""

    name: str = Field(..., description="Command/method name")
    displayName: str = Field(..., description="Display name for UI")
    description: str = Field("", description="Command description")
    category: str = Field(
        "diagnostic",
        description="Category: measurement, control, configuration, diagnostic",
    )
    parameters: List[ParameterInfo] = Field(
        default_factory=list, description="Command parameters"
    )
    returnType: str = Field("Any", description="Return type")
    returnUnit: Optional[str] = Field(None, description="Unit of return value")
    async_: bool = Field(True, alias="async", description="Whether command is async")

    class Config:
        populate_by_name = True


class HardwareCommandsResponse(BaseModel):
    """Response containing available commands for a hardware device."""

    hardwareId: str = Field(..., description="Hardware device ID")
    driver: str = Field(..., description="Driver class name")
    connected: bool = Field(..., description="Whether device is connected")
    commands: List[CommandInfo] = Field(..., description="Available commands")


class HardwareDetailedStatus(BaseModel):
    """Detailed hardware status information."""

    id: str = Field(..., description="Hardware device ID")
    driver: str = Field(..., description="Driver class name")
    status: str = Field(..., description="Connection status")
    connected: bool = Field(..., description="Whether connected")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration")
    info: Dict[str, Any] = Field(default_factory=dict, description="Device info")
    lastError: Optional[str] = Field(None, description="Last error message")


class ManualStepConfig(BaseModel):
    """Manual mode configuration for a sequence step."""

    skippable: bool = Field(True, description="Can be skipped in manual mode")
    autoOnly: bool = Field(False, description="Only runs in automatic mode")
    prompt: Optional[str] = Field(None, description="Confirmation prompt")
    pauseBefore: bool = Field(False, description="Pause before execution")
    pauseAfter: bool = Field(False, description="Pause after execution")
    parameterOverrides: List[str] = Field(
        default_factory=list, description="Parameters that can be overridden"
    )


class ManualStepInfo(BaseModel):
    """Step information for manual sequence execution."""

    name: str = Field(..., description="Step name")
    displayName: str = Field(..., description="Display name")
    order: int = Field(..., description="Execution order")
    timeout: float = Field(60.0, description="Timeout in seconds")
    manual: ManualStepConfig = Field(
        default_factory=ManualStepConfig, description="Manual mode config"
    )
    status: str = Field("pending", description="Current status")
    result: Optional[Dict[str, Any]] = Field(None, description="Step result")
    duration: Optional[float] = Field(None, description="Execution duration")


class ManualStepRequest(BaseModel):
    """Request body for manual step execution."""

    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameter overrides for the step"
    )


class CommandPreset(BaseModel):
    """Saved command preset for quick access."""

    id: str = Field(..., description="Preset ID")
    name: str = Field(..., description="Preset name")
    hardwareId: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    createdAt: str = Field(..., description="Creation timestamp")


class CommandPresetCreate(BaseModel):
    """Request body for creating a command preset."""

    name: str = Field(..., description="Preset name")
    hardwareId: str = Field(..., description="Hardware device ID")
    command: str = Field(..., description="Command name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
