"""
Backward compatibility module for legacy decorator imports.

This module is DEPRECATED. Use station_service.sdk instead.

Example migration:
    # Old (deprecated)
    from station_service.sequence.decorators import sequence, step, parameter

    # New (recommended)
    from station_service_sdk import sequence, step, parameter
"""

import warnings

warnings.warn(
    "station_service.sequence.decorators is deprecated. "
    "Use station_service.sdk instead: "
    "from station_service_sdk import sequence, step, parameter",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from SDK
from station_service.sdk.decorators import (
    # Main decorators
    sequence,
    step,
    parameter,
    # Metadata classes
    SequenceMeta,
    StepMeta,
    ParameterMeta,
    # Introspection helpers
    get_sequence_meta,
    get_step_meta,
    get_parameter_meta,
    is_step_method,
    is_parameter_method,
    collect_steps_from_decorated_class,
    collect_parameters_from_decorated_class,
)

__all__ = [
    "sequence",
    "step",
    "parameter",
    "SequenceMeta",
    "StepMeta",
    "ParameterMeta",
    "get_sequence_meta",
    "get_step_meta",
    "get_parameter_meta",
    "is_step_method",
    "is_parameter_method",
    "collect_steps_from_decorated_class",
    "collect_parameters_from_decorated_class",
]
