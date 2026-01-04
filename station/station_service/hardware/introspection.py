"""
Hardware Driver Introspection Module

Provides utilities for discovering available commands from hardware drivers
for the enhanced manual control interface.
"""

import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, get_type_hints


class ParameterDefinition:
    """Definition of a command parameter."""

    def __init__(
        self,
        name: str,
        param_type: str = "string",
        required: bool = False,
        default: Any = None,
        unit: Optional[str] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.param_type = param_type
        self.required = required
        self.default = default
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.options = options
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "displayName": _to_display_name(self.name),
            "type": self.param_type,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.unit:
            result["unit"] = self.unit
        if self.min_val is not None:
            result["min"] = self.min_val
        if self.max_val is not None:
            result["max"] = self.max_val
        if self.options:
            result["options"] = self.options
        if self.description:
            result["description"] = self.description
        return result


class CommandDefinition:
    """Definition of a hardware command."""

    def __init__(
        self,
        name: str,
        display_name: Optional[str] = None,
        description: str = "",
        category: str = "diagnostic",
        parameters: Optional[List[ParameterDefinition]] = None,
        return_type: str = "Any",
        return_unit: Optional[str] = None,
        is_async: bool = True,
    ):
        self.name = name
        self.display_name = display_name or _to_display_name(name)
        self.description = description
        self.category = category
        self.parameters = parameters or []
        self.return_type = return_type
        self.return_unit = return_unit
        self.is_async = is_async

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "category": self.category,
            "parameters": [p.to_dict() for p in self.parameters],
            "returnType": self.return_type,
            "returnUnit": self.return_unit,
            "async": self.is_async,
        }


def _to_display_name(name: str) -> str:
    """Convert snake_case to Title Case display name."""
    return name.replace("_", " ").title()


def _infer_param_type(type_hint: Any) -> str:
    """Infer parameter type from type hint."""
    if type_hint is None:
        return "string"

    type_str = str(type_hint).lower()

    if "int" in type_str:
        return "number"
    elif "float" in type_str:
        return "number"
    elif "bool" in type_str:
        return "boolean"
    elif "str" in type_str:
        return "string"
    else:
        return "string"


def _infer_category(method_name: str) -> str:
    """Infer command category from method name."""
    name_lower = method_name.lower()

    if any(kw in name_lower for kw in ["measure", "read", "get", "query", "fetch"]):
        return "measurement"
    elif any(kw in name_lower for kw in ["set", "write", "move", "trigger", "start", "stop"]):
        return "control"
    elif any(kw in name_lower for kw in ["config", "range", "mode", "setup", "init"]):
        return "configuration"
    else:
        return "diagnostic"


def _parse_docstring(docstring: Optional[str]) -> Tuple[str, Dict[str, str]]:
    """
    Parse docstring to extract description and parameter descriptions.

    Returns:
        Tuple of (description, {param_name: param_description})
    """
    if not docstring:
        return "", {}

    lines = docstring.strip().split("\n")
    description = lines[0] if lines else ""
    param_docs = {}

    in_args = False
    current_param = None

    for line in lines[1:]:
        line = line.strip()

        if line.lower().startswith("args:"):
            in_args = True
            continue
        elif line.lower().startswith(("returns:", "raises:", "example:")):
            in_args = False
            continue

        if in_args and line:
            # Parse parameter documentation
            if ":" in line and not line.startswith(" "):
                parts = line.split(":", 1)
                current_param = parts[0].strip()
                param_docs[current_param] = parts[1].strip() if len(parts) > 1 else ""
            elif current_param and line.startswith(" "):
                param_docs[current_param] += " " + line.strip()

    return description, param_docs


def discover_driver_commands(
    driver_instance: Any,
    include_private: bool = False,
) -> List[CommandDefinition]:
    """
    Introspect driver instance to discover available commands.

    Uses type hints, docstrings, and method signatures for metadata extraction.

    Args:
        driver_instance: The hardware driver instance to introspect
        include_private: Whether to include methods starting with '_'

    Returns:
        List of CommandDefinition objects
    """
    commands = []
    driver_class = driver_instance.__class__

    # Get all methods from the class
    for name in dir(driver_instance):
        # Skip private/dunder methods
        if name.startswith("__"):
            continue
        if not include_private and name.startswith("_"):
            continue

        attr = getattr(driver_instance, name, None)
        if attr is None or not callable(attr):
            continue

        # Skip properties
        if isinstance(getattr(driver_class, name, None), property):
            continue

        method = attr

        try:
            # Get type hints
            hints = {}
            try:
                hints = get_type_hints(method)
            except Exception:
                pass

            # Get signature
            sig = inspect.signature(method)

            # Parse docstring
            doc = inspect.getdoc(method) or ""
            description, param_docs = _parse_docstring(doc)

            # Build parameters
            params = []
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                param_type = _infer_param_type(hints.get(param_name))
                required = param.default is inspect.Parameter.empty
                default = None if required else param.default

                params.append(ParameterDefinition(
                    name=param_name,
                    param_type=param_type,
                    required=required,
                    default=default,
                    description=param_docs.get(param_name),
                ))

            # Determine return type
            return_hint = hints.get("return")
            return_type = str(return_hint) if return_hint else "Any"

            commands.append(CommandDefinition(
                name=name,
                description=description,
                category=_infer_category(name),
                parameters=params,
                return_type=return_type,
                is_async=asyncio.iscoroutinefunction(method),
            ))

        except Exception:
            # Skip methods that can't be introspected
            continue

    # Sort by category then name
    category_order = {"measurement": 0, "control": 1, "configuration": 2, "diagnostic": 3}
    commands.sort(key=lambda c: (category_order.get(c.category, 99), c.name))

    return commands


def get_driver_info(driver_instance: Any) -> Dict[str, Any]:
    """
    Get information about a driver instance.

    Args:
        driver_instance: The hardware driver instance

    Returns:
        Dictionary with driver information
    """
    driver_class = driver_instance.__class__

    info = {
        "className": driver_class.__name__,
        "moduleName": driver_class.__module__,
        "name": getattr(driver_instance, "name", driver_class.__name__),
        "connected": False,
        "config": {},
    }

    # Check connection status
    if hasattr(driver_instance, "_connected"):
        info["connected"] = driver_instance._connected
    elif hasattr(driver_instance, "is_connected"):
        try:
            if asyncio.iscoroutinefunction(driver_instance.is_connected):
                # Can't call async in sync context, assume connected if method exists
                info["connected"] = True
            else:
                info["connected"] = driver_instance.is_connected()
        except Exception:
            pass

    # Get config
    if hasattr(driver_instance, "config"):
        info["config"] = driver_instance.config

    return info
