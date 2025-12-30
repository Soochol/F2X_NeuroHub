"""
Decorators for sequence, step, and parameter definition.

This module provides decorators to annotate sequence classes, methods,
and properties with metadata for automatic discovery and execution.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


@dataclass(frozen=True)
class SequenceMeta:
    """Metadata for a sequence class."""

    name: str
    description: str
    version: str


@dataclass(frozen=True)
class StepMeta:
    """Metadata for a step method."""

    order: int
    timeout: float = 60.0
    retry: int = 0
    cleanup: bool = False
    condition: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class ParameterMeta:
    """Metadata for a parameter property."""

    name: str
    display_name: str
    unit: str
    description: str
    default_getter: Optional[Callable[[], Any]] = field(default=None, compare=False)


class ParameterProperty(property):
    """
    A property subclass that supports custom metadata attributes.

    Python's built-in property doesn't allow setting arbitrary attributes,
    so we need this subclass to store _param_meta.
    """

    _param_meta: Optional[ParameterMeta] = None


def sequence(
    name: str,
    description: str = "",
    version: str = "1.0.0",
) -> Callable[[type[T]], type[T]]:
    """
    Class decorator to mark a class as a sequence.

    Adds _sequence_meta attribute to the class with SequenceMeta.

    Args:
        name: The name of the sequence
        description: A description of what the sequence does
        version: The version string (e.g., "1.0.0")

    Returns:
        Decorated class with _sequence_meta attribute

    Example:
        @sequence(name="power_test", description="Power supply test", version="1.0.0")
        class PowerTestSequence:
            pass
    """

    def decorator(cls: type[T]) -> type[T]:
        cls._sequence_meta = SequenceMeta(  # type: ignore[attr-defined]
            name=name,
            description=description,
            version=version,
        )
        return cls

    return decorator


def step(
    order: int,
    timeout: float = 60.0,
    retry: int = 0,
    cleanup: bool = False,
    condition: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Method decorator to mark a method as a test step.

    Adds _step_meta attribute to the method with StepMeta.

    Args:
        order: The execution order of this step (lower numbers run first)
        timeout: Maximum execution time in seconds (default: 60.0)
        retry: Number of retry attempts on failure (default: 0)
        cleanup: Whether this is a cleanup step (default: False)
        condition: Optional condition expression for conditional execution

    Returns:
        Decorated method with _step_meta attribute

    Example:
        @step(order=1, timeout=30.0, retry=2)
        async def measure_voltage(self):
            pass
    """

    def decorator(func: F) -> F:
        # Extract name and description from function
        func_name = func.__name__
        func_doc = func.__doc__ or ""
        # Get first line of docstring as description
        description = func_doc.strip().split("\n")[0] if func_doc else ""

        func._step_meta = StepMeta(  # type: ignore[attr-defined]
            order=order,
            timeout=timeout,
            retry=retry,
            cleanup=cleanup,
            condition=condition,
            name=func_name,
            description=description,
        )
        return func

    return decorator


def parameter(
    name: str,
    display_name: str = "",
    unit: str = "",
    description: str = "",
) -> Callable[[Callable[[Any], T]], ParameterProperty]:
    """
    Property decorator to mark a property as an exposed parameter.

    Adds _param_meta attribute to the property with ParameterMeta.

    Args:
        name: The internal name of the parameter
        display_name: The display name for UI (defaults to name if empty)
        unit: The unit of measurement (e.g., "V", "A", "ms")
        description: A description of the parameter

    Returns:
        ParameterProperty with _param_meta attribute

    Example:
        @parameter(name="voltage_limit", display_name="Voltage Limit", unit="V")
        def voltage_limit(self) -> float:
            return self._voltage_limit
    """

    def decorator(func: Callable[[Any], T]) -> ParameterProperty:
        # Use name as display_name if not provided
        actual_display_name = display_name if display_name else name

        # Create the metadata
        meta = ParameterMeta(
            name=name,
            display_name=actual_display_name,
            unit=unit,
            description=description,
            default_getter=func,
        )

        # Create ParameterProperty (subclass of property) and attach metadata
        prop = ParameterProperty(func)
        prop._param_meta = meta

        return prop

    return decorator


def get_sequence_meta(cls: type) -> Optional[SequenceMeta]:
    """
    Get the sequence metadata from a class.

    Args:
        cls: The class to get metadata from

    Returns:
        SequenceMeta if the class is decorated, None otherwise
    """
    return getattr(cls, "_sequence_meta", None)


def get_step_meta(method: Callable) -> Optional[StepMeta]:
    """
    Get the step metadata from a method.

    Args:
        method: The method to get metadata from

    Returns:
        StepMeta if the method is decorated, None otherwise
    """
    return getattr(method, "_step_meta", None)


def get_parameter_meta(prop: Union[property, Callable]) -> Optional[ParameterMeta]:
    """
    Get the parameter metadata from a property.

    Args:
        prop: The property to get metadata from

    Returns:
        ParameterMeta if the property is decorated, None otherwise
    """
    return getattr(prop, "_param_meta", None)


def collect_steps(cls: type) -> list[tuple[str, Callable, StepMeta]]:
    """
    Collect all step methods from a sequence class.

    Args:
        cls: The sequence class to inspect

    Returns:
        List of (method_name, method, StepMeta) tuples, sorted by order
    """
    steps: list[tuple[str, Callable, StepMeta]] = []

    for name in dir(cls):
        if name.startswith("_"):
            continue

        attr = getattr(cls, name, None)
        if attr is None:
            continue

        meta = get_step_meta(attr)
        if meta is not None:
            steps.append((name, attr, meta))

    # Sort by order
    steps.sort(key=lambda x: x[2].order)
    return steps


def collect_parameters(cls: type) -> list[tuple[str, ParameterProperty, ParameterMeta]]:
    """
    Collect all parameter properties from a sequence class.

    Args:
        cls: The sequence class to inspect

    Returns:
        List of (property_name, ParameterProperty, ParameterMeta) tuples
    """
    parameters: list[tuple[str, ParameterProperty, ParameterMeta]] = []

    for name in dir(cls):
        if name.startswith("_"):
            continue

        # Get from class dict to get the actual property object
        attr = cls.__dict__.get(name)
        if attr is None:
            continue

        if isinstance(attr, ParameterProperty):
            meta = get_parameter_meta(attr)
            if meta is not None:
                parameters.append((name, attr, meta))

    return parameters
