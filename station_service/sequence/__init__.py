"""
Sequence module for test sequence management.

This module provides:
- Exception hierarchy for sequence-related errors
- Decorators for sequence/step/parameter definition
- Manifest models for package configuration
- Dynamic sequence loader for package discovery and loading
"""

from station_service.sequence.decorators import (
    ParameterMeta,
    SequenceMeta,
    StepMeta,
    collect_parameters,
    collect_steps,
    get_parameter_meta,
    get_sequence_meta,
    get_step_meta,
    parameter,
    sequence,
    step,
)
from station_service.sequence.exceptions import (
    CommunicationError,
    ConnectionError,
    DriverError,
    ExecutionError,
    ManifestError,
    PackageError,
    SequenceError,
    StepTimeoutError,
    TestFailure,
    TestSkipped,
)
from station_service.sequence.loader import SequenceLoader
from station_service.sequence.manifest import (
    ConfigFieldSchema,
    DependencySpec,
    EntryPoint,
    HardwareDefinition,
    ParameterDefinition,
    ParameterType,
    SequenceManifest,
)

__all__ = [
    # Exceptions
    "SequenceError",
    "PackageError",
    "ManifestError",
    "DriverError",
    "ConnectionError",
    "CommunicationError",
    "ExecutionError",
    "TestFailure",
    "TestSkipped",
    "StepTimeoutError",
    # Decorators
    "sequence",
    "step",
    "parameter",
    # Metadata
    "SequenceMeta",
    "StepMeta",
    "ParameterMeta",
    # Helper functions
    "get_sequence_meta",
    "get_step_meta",
    "get_parameter_meta",
    "collect_steps",
    "collect_parameters",
    # Manifest models
    "ParameterType",
    "ConfigFieldSchema",
    "HardwareDefinition",
    "ParameterDefinition",
    "EntryPoint",
    "DependencySpec",
    "SequenceManifest",
    # Loader
    "SequenceLoader",
]
