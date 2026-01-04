"""
System API routes package for Station Service.

This package provides modular system endpoints organized by domain:

- health: Health check and system information endpoints
- workflow: Workflow configuration for 착공/완공
- operator: Operator session management (login/logout)
- mes: MES integration endpoints (processes, headers, WIP validation)

Usage:
    from station_service.api.routes.system import router

    app.include_router(router)
"""

from fastapi import APIRouter

# Import sub-routers
from station_service.api.routes.system.health import (
    router as health_router,
    # Route handlers (for testing)
    get_system_info,
    get_health,
    get_sync_status,
    force_sync,
    # Helper functions (for testing)
    _get_disk_usage,
    _determine_health_status,
    # Constants
    SERVICE_VERSION,
)
from station_service.api.routes.system.workflow import router as workflow_router
from station_service.api.routes.system.operator import (
    router as operator_router,
    # Session management functions
    get_operator_session,
    set_operator_session,
    clear_operator_session,
    update_operator_tokens,
    # Route handlers (for testing)
    get_operator,
    operator_login,
    operator_logout,
)
from station_service.api.routes.system.mes import router as mes_router

# Import schemas for backward compatibility
from station_service.api.routes.system.schemas import (
    SyncStatus,
    UpdateStationInfoRequest,
    WorkflowConfigResponse,
    UpdateWorkflowRequest,
    OperatorInfo,
    OperatorSession,
    OperatorLoginRequest,
    ProcessInfo,
    ProcessHeaderInfo,
    ValidateWIPRequest,
    ValidateWIPResponse,
)

# Main router that combines all sub-routers
router = APIRouter(prefix="/api/system", tags=["System"])

# Include all sub-routers
router.include_router(health_router)
router.include_router(workflow_router)
router.include_router(operator_router)
router.include_router(mes_router)

__all__ = [
    # Main router
    "router",
    # Sub-routers
    "health_router",
    "workflow_router",
    "operator_router",
    "mes_router",
    # Session management functions
    "get_operator_session",
    "set_operator_session",
    "clear_operator_session",
    "update_operator_tokens",
    # Health route handlers
    "get_system_info",
    "get_health",
    "get_sync_status",
    "force_sync",
    "_get_disk_usage",
    "_determine_health_status",
    "SERVICE_VERSION",
    # Operator route handlers
    "get_operator",
    "operator_login",
    "operator_logout",
    # Schemas
    "SyncStatus",
    "UpdateStationInfoRequest",
    "WorkflowConfigResponse",
    "UpdateWorkflowRequest",
    "OperatorInfo",
    "OperatorSession",
    "OperatorLoginRequest",
    "ProcessInfo",
    "ProcessHeaderInfo",
    "ValidateWIPRequest",
    "ValidateWIPResponse",
]
