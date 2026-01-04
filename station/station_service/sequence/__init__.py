"""
Backward compatibility module.

This module is DEPRECATED. Use station_service.sdk instead.

All imports from this module are re-exported from station_service.sdk.
"""

import warnings

warnings.warn(
    "station_service.sequence is deprecated. Use station_service.sdk instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from SDK for backward compatibility
from station_service_sdk import (
    # Decorators
    sequence,
    step,
    parameter,
    # Metadata
    SequenceMeta,
    ParameterMeta,
    StepMeta,
    StepInfo,
    # Helpers
    collect_steps,
    collect_steps_from_class,
    collect_steps_from_manifest,
    get_sequence_meta,
    get_step_meta,
    get_parameter_meta,
    is_step_method,
    is_parameter_method,
    # Base classes
    SequenceBase,
    StepResult,
    ExecutionContext,
    # Loader
    SequenceLoader,
    # Manifest
    SequenceManifest,
)

__all__ = [
    "sequence",
    "step",
    "parameter",
    "SequenceMeta",
    "ParameterMeta",
    "StepMeta",
    "StepInfo",
    "collect_steps",
    "collect_steps_from_class",
    "collect_steps_from_manifest",
    "get_sequence_meta",
    "get_step_meta",
    "get_parameter_meta",
    "is_step_method",
    "is_parameter_method",
    "SequenceBase",
    "StepResult",
    "ExecutionContext",
    "SequenceLoader",
    "SequenceManifest",
]
