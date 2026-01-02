"""
Dependency injection utilities for FastAPI endpoints.

This module re-exports all dependencies from app.core.deps for backward compatibility.
All dependencies are now defined in app.core.deps.

Provides:
    - get_db: Database session injection
    - get_current_user: Get current authenticated user
    - get_current_active_user: Get current active user
    - get_current_admin_user: Get current admin user
    - get_current_manager_user: Get current manager/admin user
    - check_role_permission: Factory for role-based access control
"""

# Re-export all dependencies from core.deps
from app.core.deps import (
    get_db,
    get_async_db,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_manager_user,
    check_role_permission,
    StationAuth,
    get_station_auth,
)

__all__ = [
    "get_db",
    "get_async_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_manager_user",
    "check_role_permission",
    "StationAuth",
    "get_station_auth",
]
