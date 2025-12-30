"""
Sequence package model definitions.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ParameterSchema(BaseModel):
    """Schema definition for a sequence parameter."""

    name: str
    display_name: str
    type: str  # "float", "integer", "string", "boolean"
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[str]] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class HardwareSchema(BaseModel):
    """Schema definition for hardware configuration."""

    id: str
    display_name: str
    driver: str  # Driver file path
    class_name: str  # Driver class name
    description: Optional[str] = None
    config_schema: Dict[str, Dict[str, Any]] = {}


class StepSchema(BaseModel):
    """Schema definition for a sequence step."""

    order: int
    name: str
    display_name: str
    description: str
    timeout: float = 60.0
    retry: int = 0
    cleanup: bool = False
    condition: Optional[str] = None


class SequencePackage(BaseModel):
    """Complete sequence package information."""

    name: str  # "pcb_voltage_test"
    version: str  # "1.2.0"
    display_name: str
    description: str
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    path: str  # "sequences/pcb_voltage_test"

    hardware: List[HardwareSchema] = []
    parameters: List[ParameterSchema] = []
    steps: List[StepSchema] = []


# Manifest models for sequence package definition (manifest.yaml)


class ConfigField(BaseModel):
    """Configuration field schema."""

    type: str  # "string", "integer", "float", "boolean"
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    options: Optional[List[Any]] = None
    min: Optional[float] = None
    max: Optional[float] = None


class HardwareDefinition(BaseModel):
    """Hardware definition from manifest."""

    model_config = ConfigDict(populate_by_name=True)

    display_name: str
    driver: str  # Relative path
    class_name: str = Field(alias="class")
    description: Optional[str] = None
    config_schema: Dict[str, ConfigField] = {}


class ParameterDefinition(BaseModel):
    """Parameter definition from manifest."""

    display_name: str
    type: str
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[Any]] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class EntryPoint(BaseModel):
    """Sequence entry point."""

    model_config = ConfigDict(populate_by_name=True)

    module: str  # "sequence"
    class_name: str = Field(alias="class")


class SequenceManifest(BaseModel):
    """Sequence package manifest (manifest.yaml)."""

    name: str
    version: str
    author: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    entry_point: EntryPoint
    hardware: Dict[str, HardwareDefinition] = {}
    parameters: Dict[str, ParameterDefinition] = {}
    dependencies: Optional[Dict[str, List[str]]] = None
