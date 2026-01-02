"""
API v1 Routers for F2X NeuroHub MES.

This package contains all version 1 API endpoint routers.

Available routers:
    - auth: Authentication (login, logout, token refresh)
    - analytics: Dashboard metrics and reporting
    - dashboard: Dashboard-specific aggregated endpoints
    - product_models: Product model management
    - processes: Manufacturing process definitions (8 processes)
    - users: User authentication and management
    - lots: Production batch tracking
    - wip_items: Work-In-Progress tracking (processes 1-6)
    - serials: Individual unit tracking
    - process_data: Process execution records
    - audit_logs: Immutable audit trail (read-only)
    - alerts: System notifications and alarms
    - production_lines: Production line management
    - equipment: Manufacturing equipment management
    - error_logs: Error logging and monitoring (read-only)
"""

from app.api.v1 import (
    auth,
    analytics,
    dashboard,
    product_models,
    processes,
    process_operations,
    process_headers,
    users,
    lots,
    wip_items,
    serials,
    process_data,
    audit_logs,
    alerts,
    production_lines,
    equipment,
    error_logs,
    async_operations,
    search,
    stations,
)

__all__ = [
    "auth",
    "analytics",
    "dashboard",
    "product_models",
    "processes",
    "process_operations",
    "process_headers",
    "users",
    "lots",
    "wip_items",
    "serials",
    "process_data",
    "audit_logs",
    "alerts",
    "production_lines",
    "equipment",
    "error_logs",
    "async_operations",
    "search",
    "stations",
]
