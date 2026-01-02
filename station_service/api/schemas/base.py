"""
Base API schema with automatic camelCase serialization.

This module re-exports APIBaseModel from core.base for backwards compatibility.
The actual implementation is in station_service.core.base to avoid circular imports.
"""

# Re-export from core.base for backwards compatibility
from station_service.core.base import APIBaseModel

__all__ = ["APIBaseModel"]
