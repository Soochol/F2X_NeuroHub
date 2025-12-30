"""
Pydantic models for sequence manifest files.

This module defines the schema for manifest.yaml files that describe
sequence packages, their hardware requirements, and parameters.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class ParameterType(str, Enum):
    """Types of parameters supported in sequence manifests."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


class ConfigFieldSchema(BaseModel):
    """Schema for a configuration field in hardware definitions."""

    type: ParameterType
    required: bool = False
    default: Optional[Any] = None
    description: str = ""
    options: Optional[List[Union[str, int, float]]] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None


class HardwareDefinition(BaseModel):
    """Definition of a hardware component required by the sequence."""

    display_name: str
    driver: str
    class_name: str = Field(alias="class")
    description: str = ""
    config_schema: Optional[Dict[str, ConfigFieldSchema]] = None

    model_config = {"populate_by_name": True}


class ParameterDefinition(BaseModel):
    """Definition of a configurable parameter for the sequence."""

    display_name: str
    type: ParameterType
    default: Optional[Any] = None
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    options: Optional[List[Union[str, int, float, bool]]] = None
    unit: str = ""
    description: str = ""

    @model_validator(mode="after")
    def validate_default_type(self) -> "ParameterDefinition":
        """Validate that the default value matches the parameter type."""
        if self.default is not None:
            if self.type == ParameterType.STRING and not isinstance(self.default, str):
                raise ValueError(
                    f"Default value must be string for STRING type, got {type(self.default).__name__}"
                )
            elif self.type == ParameterType.INTEGER and not isinstance(
                self.default, int
            ):
                raise ValueError(
                    f"Default value must be int for INTEGER type, got {type(self.default).__name__}"
                )
            elif self.type == ParameterType.FLOAT and not isinstance(
                self.default, (int, float)
            ):
                raise ValueError(
                    f"Default value must be float for FLOAT type, got {type(self.default).__name__}"
                )
            elif self.type == ParameterType.BOOLEAN and not isinstance(
                self.default, bool
            ):
                raise ValueError(
                    f"Default value must be bool for BOOLEAN type, got {type(self.default).__name__}"
                )
        return self


class EntryPoint(BaseModel):
    """Entry point configuration for the sequence module and class."""

    module: str
    class_name: str = Field(alias="class")

    model_config = {"populate_by_name": True}

    @field_validator("module")
    @classmethod
    def validate_module(cls, v: str) -> str:
        """Validate that the module path is a valid Python module path."""
        # Allow relative paths like "sequence" or "module.submodule"
        parts = v.split(".")
        for part in parts:
            if not part.isidentifier():
                raise ValueError(
                    f"Invalid module path '{v}': '{part}' is not a valid identifier"
                )
        return v

    @field_validator("class_name")
    @classmethod
    def validate_class_name(cls, v: str) -> str:
        """Validate that the class name is a valid Python identifier."""
        if not v.isidentifier():
            raise ValueError(f"Invalid class name '{v}': must be a valid identifier")
        return v


class DependencySpec(BaseModel):
    """Specification of package dependencies."""

    python: List[str] = Field(default_factory=list)


class SequenceManifest(BaseModel):
    """
    Complete manifest for a sequence package.

    This model represents the schema for manifest.yaml files that describe
    sequence packages, including metadata, entry points, hardware requirements,
    parameters, and dependencies.
    """

    name: str
    version: str
    author: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    entry_point: EntryPoint
    hardware: Dict[str, HardwareDefinition] = Field(default_factory=dict)
    parameters: Dict[str, ParameterDefinition] = Field(default_factory=dict)
    dependencies: DependencySpec = Field(default_factory=DependencySpec)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that the name is a valid Python identifier."""
        if not v.isidentifier():
            raise ValueError(
                f"Invalid sequence name '{v}': must be a valid Python identifier"
            )
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version follows X.Y.Z pattern."""
        pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(pattern, v):
            raise ValueError(
                f"Invalid version '{v}': must follow X.Y.Z pattern (e.g., '1.0.0')"
            )
        return v

    def get_hardware_names(self) -> List[str]:
        """Get list of hardware component names defined in this manifest."""
        return list(self.hardware.keys())

    def get_parameter_names(self) -> List[str]:
        """Get list of parameter names defined in this manifest."""
        return list(self.parameters.keys())

    def get_required_packages(self) -> List[str]:
        """Get list of required Python packages from dependencies."""
        return self.dependencies.python.copy()
