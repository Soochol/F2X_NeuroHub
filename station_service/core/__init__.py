"""
Core shared utilities for Station Service.

This module provides base classes and utilities that need to be shared
across different packages without causing circular imports.
"""

from station_service.core.base import APIBaseModel

__all__ = ["APIBaseModel"]
