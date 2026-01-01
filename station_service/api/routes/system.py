"""
System API routes for Station Service.

This module provides endpoints for system information and health checks.
"""

import logging
import os
import shutil
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from station_service.api.dependencies import (
    get_batch_manager,
    get_backend_client,
    get_config,
    get_config_path,
    get_database,
    get_sync_engine,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.schemas.result import HealthStatus, SystemInfo
from station_service.models.config import StationInfo, WorkflowConfig
from station_service.batch.manager import BatchManager
from station_service.models.config import StationConfig
from station_service.storage.database import Database
from station_service.sync.backend_client import BackendClient
from station_service.sync.engine import SyncEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["System"])

# Track service start time for uptime calculation
_service_start_time: float = time.time()

# Service version
SERVICE_VERSION = "1.0.0"


class SyncStatus(BaseModel):
    """Sync queue status response."""

    pending_count: int = Field(..., description="Number of pending sync items")
    failed_count: int = Field(..., description="Number of failed sync items")
    last_sync_at: Optional[datetime] = Field(None, description="Last successful sync timestamp")
    backend_connected: bool = Field(..., description="Whether backend is reachable")
    backend_url: str = Field(..., description="Backend URL")


@router.get(
    "/info",
    response_model=ApiResponse[SystemInfo],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get system information",
    description="""
    Retrieve Station Service system information.

    Returns details about the station including:
    - Station ID and name
    - Service version
    - Uptime in seconds
    - Backend connection status
    """,
)
async def get_system_info(
    config: StationConfig = Depends(get_config),
    sync_engine: SyncEngine = Depends(get_sync_engine),
) -> ApiResponse[SystemInfo]:
    """
    Get Station Service system information.

    This endpoint returns general information about the station service
    including its identifier, name, version, uptime, and backend connection status.

    Returns:
        ApiResponse[SystemInfo]: Station system information wrapped in standard response

    Raises:
        HTTPException: 500 if there's an internal error retrieving system info
    """
    try:
        uptime_seconds = int(time.time() - _service_start_time)

        system_info = SystemInfo(
            station_id=config.station.id,
            station_name=config.station.name,
            description=config.station.description,
            version=SERVICE_VERSION,
            uptime=uptime_seconds,
            backend_connected=sync_engine.is_connected if sync_engine.is_running else False,
        )

        return ApiResponse(
            success=True,
            data=system_info,
        )
    except Exception as e:
        logger.exception("Failed to get system info")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system info: {str(e)}",
        )


class UpdateStationInfoRequest(BaseModel):
    """Request body for updating station information."""

    id: str = Field(..., min_length=1, max_length=100, description="Station ID")
    name: str = Field(..., min_length=1, max_length=200, description="Station name")
    description: str = Field("", max_length=500, description="Station description")


@router.put(
    "/station-info",
    response_model=ApiResponse[SystemInfo],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Update station information",
    description="""
    Update the station identification information.

    Updates the following fields in the configuration:
    - Station ID
    - Station Name
    - Description

    The configuration file is updated atomically with a backup created.
    Note: The service must be restarted for all changes to take full effect.
    """,
)
async def update_station_info(
    request: UpdateStationInfoRequest,
    config: StationConfig = Depends(get_config),
    sync_engine: SyncEngine = Depends(get_sync_engine),
    config_path: str = Depends(get_config_path),
) -> ApiResponse[SystemInfo]:
    """
    Update station information in the configuration file.

    Args:
        request: The new station information
        config: Current station configuration
        sync_engine: Sync engine for connection status
        config_path: Path to the config file

    Returns:
        ApiResponse[SystemInfo]: Updated system information

    Raises:
        HTTPException: 400 if validation fails, 500 if update fails
    """
    from pathlib import Path
    from station_service.core.config_writer import update_station_info as write_station_info

    try:
        # Create StationInfo from request
        station_info = StationInfo(
            id=request.id,
            name=request.name,
            description=request.description,
        )

        # Update the config file
        updated_config = await write_station_info(Path(config_path), station_info)

        # Update the in-memory config
        config.station = updated_config.station

        # Return updated system info
        uptime_seconds = int(time.time() - _service_start_time)

        system_info = SystemInfo(
            station_id=updated_config.station.id,
            station_name=updated_config.station.name,
            description=updated_config.station.description,
            version=SERVICE_VERSION,
            uptime=uptime_seconds,
            backend_connected=sync_engine.is_connected if sync_engine.is_running else False,
        )

        return ApiResponse(
            success=True,
            data=system_info,
            message="Station information updated successfully",
        )

    except FileNotFoundError as e:
        logger.error(f"Config file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration file not found",
        )
    except Exception as e:
        logger.exception("Failed to update station info")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update station info: {str(e)}",
        )


@router.get(
    "/health",
    response_model=ApiResponse[HealthStatus],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Health check",
    description="""
    Perform a health check on the Station Service.

    Returns the current health status including:
    - Overall health status (healthy, degraded, unhealthy)
    - Number of running batches
    - Backend connection status
    - Disk usage percentage
    """,
)
async def get_health(
    batch_manager: BatchManager = Depends(get_batch_manager),
    sync_engine: SyncEngine = Depends(get_sync_engine),
    database: Database = Depends(get_database),
) -> ApiResponse[HealthStatus]:
    """
    Perform a health check on the Station Service.

    This endpoint returns the current operational status of the station service,
    useful for monitoring and alerting systems.

    Returns:
        ApiResponse[HealthStatus]: Health status information wrapped in standard response

    Raises:
        HTTPException: 500 if there's an internal error during health check
    """
    try:
        # Count running batches
        batches_running = len(batch_manager.running_batch_ids)

        # Check backend connection status
        backend_connected = sync_engine.is_connected if sync_engine.is_running else False
        backend_status = "connected" if backend_connected else "disconnected"

        # Get disk usage
        disk_usage = _get_disk_usage()

        # Determine overall health status
        health_status = _determine_health_status(
            database_connected=database.is_connected,
            backend_connected=backend_connected,
            disk_usage=disk_usage,
        )

        health = HealthStatus(
            status=health_status,
            batches_running=batches_running,
            backend_status=backend_status,
            disk_usage=disk_usage,
        )

        return ApiResponse(
            success=True,
            data=health,
        )
    except Exception as e:
        logger.exception("Failed to perform health check")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}",
        )


@router.get(
    "/sync-status",
    response_model=ApiResponse[SyncStatus],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get sync queue status",
    description="""
    Get the current status of the sync queue.

    Returns information about:
    - Number of pending sync items
    - Number of failed sync items
    - Last successful sync timestamp
    - Backend connection status
    """,
)
async def get_sync_status(
    sync_engine: SyncEngine = Depends(get_sync_engine),
    database: Database = Depends(get_database),
) -> ApiResponse[SyncStatus]:
    """
    Get sync queue status.

    Returns:
        ApiResponse[SyncStatus]: Sync status information
    """
    try:
        from station_service.storage.repositories.sync_repository import SyncRepository

        sync_repo = SyncRepository(database)

        # Get counts
        pending_count = await sync_repo.count_pending()
        failed_count = await sync_repo.count_failed()

        sync_status = SyncStatus(
            pending_count=pending_count,
            failed_count=failed_count,
            last_sync_at=None,  # TODO: Track this in SyncEngine
            backend_connected=sync_engine.is_connected if sync_engine.is_running else False,
            backend_url=sync_engine.backend_url if sync_engine.is_running else "",
        )

        return ApiResponse(
            success=True,
            data=sync_status,
        )
    except Exception as e:
        logger.exception("Failed to get sync status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync status: {str(e)}",
        )


@router.post(
    "/sync/force",
    response_model=ApiResponse[Dict[str, int]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Force sync",
    description="Force synchronization of all pending items in the queue.",
)
async def force_sync(
    sync_engine: SyncEngine = Depends(get_sync_engine),
) -> ApiResponse[Dict[str, int]]:
    """
    Force sync all pending items.

    Returns:
        ApiResponse with success/failure counts
    """
    try:
        if not sync_engine.is_running:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sync engine not running",
            )

        result = await sync_engine.force_sync()

        return ApiResponse(
            success=True,
            data=result,
            message=f"Synced {result['success']} items, {result['failed']} failed",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to force sync")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to force sync: {str(e)}",
        )


def _get_disk_usage() -> float:
    """Get disk usage percentage for the data directory."""
    try:
        # Check disk usage of current working directory
        total, used, free = shutil.disk_usage(".")
        return round((used / total) * 100, 2)
    except Exception:
        return 0.0


def _determine_health_status(
    database_connected: bool,
    backend_connected: bool,
    disk_usage: float,
) -> str:
    """
    Determine overall health status based on component states.

    Returns:
        "healthy", "degraded", or "unhealthy"
    """
    # Critical: database must be connected
    if not database_connected:
        return "unhealthy"

    # Warning conditions
    warnings = []

    if not backend_connected:
        warnings.append("backend_disconnected")

    if disk_usage > 90:
        return "unhealthy"
    elif disk_usage > 80:
        warnings.append("disk_high")

    if warnings:
        return "degraded"

    return "healthy"


# ============================================================================
# Workflow Configuration API
# ============================================================================


class WorkflowConfigResponse(BaseModel):
    """Workflow configuration response."""

    enabled: bool = Field(..., description="Whether workflow is enabled")
    input_mode: str = Field(..., description="WIP ID input mode: 'popup' or 'barcode'")
    auto_sequence_start: bool = Field(..., description="Auto-start sequence after barcode scan")
    require_operator_login: bool = Field(..., description="Require backend login")


class UpdateWorkflowRequest(BaseModel):
    """Request body for updating workflow configuration."""

    enabled: Optional[bool] = Field(None, description="Enable/disable workflow")
    input_mode: Optional[str] = Field(None, description="Input mode: 'popup' or 'barcode'")
    auto_sequence_start: Optional[bool] = Field(None, description="Auto-start sequence")
    require_operator_login: Optional[bool] = Field(None, description="Require login")


@router.get(
    "/workflow",
    response_model=ApiResponse[WorkflowConfigResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get workflow configuration",
    description="""
    Get the current workflow configuration for 착공/완공 (process start/complete).

    Returns:
    - enabled: Whether WIP process tracking is enabled
    - input_mode: How WIP ID is provided ('popup' for manual entry, 'barcode' for scanner)
    - auto_sequence_start: Whether to auto-start sequence after barcode scan
    - require_operator_login: Whether backend login is required
    """,
)
async def get_workflow_config(
    config: StationConfig = Depends(get_config),
) -> ApiResponse[WorkflowConfigResponse]:
    """
    Get workflow configuration.

    Returns:
        ApiResponse[WorkflowConfigResponse]: Current workflow configuration
    """
    try:
        workflow = config.workflow

        response = WorkflowConfigResponse(
            enabled=workflow.enabled,
            input_mode=workflow.input_mode,
            auto_sequence_start=workflow.auto_sequence_start,
            require_operator_login=workflow.require_operator_login,
        )

        return ApiResponse(
            success=True,
            data=response,
        )
    except Exception as e:
        logger.exception("Failed to get workflow config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow config: {str(e)}",
        )


@router.put(
    "/workflow",
    response_model=ApiResponse[WorkflowConfigResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Update workflow configuration",
    description="""
    Update the workflow configuration for 착공/완공 (process start/complete).

    Only provided fields will be updated. Omitted fields remain unchanged.
    The configuration is persisted to station.yaml.
    """,
)
async def update_workflow_config(
    request: UpdateWorkflowRequest,
    config: StationConfig = Depends(get_config),
    config_path: str = Depends(get_config_path),
) -> ApiResponse[WorkflowConfigResponse]:
    """
    Update workflow configuration.

    Args:
        request: Fields to update
        config: Current station configuration
        config_path: Path to config file

    Returns:
        ApiResponse[WorkflowConfigResponse]: Updated workflow configuration
    """
    from pathlib import Path
    from station_service.core.config_writer import update_workflow_config as write_workflow_config

    try:
        # Validate input_mode if provided
        if request.input_mode is not None and request.input_mode not in ("popup", "barcode"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="input_mode must be 'popup' or 'barcode'",
            )

        # Build updated workflow config
        updated_workflow = WorkflowConfig(
            enabled=request.enabled if request.enabled is not None else config.workflow.enabled,
            input_mode=request.input_mode if request.input_mode is not None else config.workflow.input_mode,
            auto_sequence_start=request.auto_sequence_start if request.auto_sequence_start is not None else config.workflow.auto_sequence_start,
            require_operator_login=request.require_operator_login if request.require_operator_login is not None else config.workflow.require_operator_login,
        )

        # Update the config file
        updated_config = await write_workflow_config(Path(config_path), updated_workflow)

        # Update the in-memory config
        config.workflow = updated_config.workflow

        response = WorkflowConfigResponse(
            enabled=updated_config.workflow.enabled,
            input_mode=updated_config.workflow.input_mode,
            auto_sequence_start=updated_config.workflow.auto_sequence_start,
            require_operator_login=updated_config.workflow.require_operator_login,
        )

        return ApiResponse(
            success=True,
            data=response,
            message="Workflow configuration updated successfully",
        )

    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration file not found",
        )
    except Exception as e:
        logger.exception("Failed to update workflow config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow config: {str(e)}",
        )


# ============================================================================
# Operator Session API
# ============================================================================


class OperatorInfo(BaseModel):
    """Operator information from backend."""

    id: int = Field(..., description="Operator ID")
    username: str = Field(..., description="Operator username")
    name: str = Field("", description="Operator display name")
    role: str = Field("", description="Operator role")


class OperatorSession(BaseModel):
    """Current operator session state."""

    logged_in: bool = Field(..., description="Whether an operator is logged in")
    operator: Optional[OperatorInfo] = Field(None, description="Logged in operator info")
    access_token: Optional[str] = Field(None, description="JWT access token")
    logged_in_at: Optional[datetime] = Field(None, description="Login timestamp")


class OperatorLoginRequest(BaseModel):
    """Request body for operator login."""

    username: str = Field(..., min_length=1, description="Operator username")
    password: str = Field(..., min_length=1, description="Operator password")


# In-memory operator session state (single station)
_operator_session: Dict[str, Any] = {
    "logged_in": False,
    "operator": None,
    "access_token": None,
    "logged_in_at": None,
}


def get_operator_session() -> Dict[str, Any]:
    """Get the current operator session state."""
    return _operator_session


def set_operator_session(
    operator: Optional[Dict[str, Any]] = None,
    access_token: Optional[str] = None,
) -> None:
    """Set the operator session state."""
    global _operator_session
    if operator and access_token:
        _operator_session = {
            "logged_in": True,
            "operator": operator,
            "access_token": access_token,
            "logged_in_at": datetime.now(),
        }
    else:
        _operator_session = {
            "logged_in": False,
            "operator": None,
            "access_token": None,
            "logged_in_at": None,
        }


def clear_operator_session() -> None:
    """Clear the operator session state."""
    set_operator_session(None, None)


@router.get(
    "/operator",
    response_model=ApiResponse[OperatorSession],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get current operator session",
    description="""
    Get the current operator session state.

    Returns:
    - logged_in: Whether an operator is logged in
    - operator: Operator info if logged in (id, username, name, role)
    - logged_in_at: Login timestamp if logged in
    """,
)
async def get_operator(
    config: StationConfig = Depends(get_config),
) -> ApiResponse[OperatorSession]:
    """
    Get current operator session.

    Returns:
        ApiResponse[OperatorSession]: Current operator session state
    """
    try:
        session = get_operator_session()

        operator_info = None
        if session["operator"]:
            operator_info = OperatorInfo(
                id=session["operator"].get("id", 0),
                username=session["operator"].get("username", ""),
                name=session["operator"].get("name", session["operator"].get("username", "")),
                role=session["operator"].get("role", ""),
            )

        response = OperatorSession(
            logged_in=session["logged_in"],
            operator=operator_info,
            access_token=None,  # Don't expose token in response
            logged_in_at=session["logged_in_at"],
        )

        return ApiResponse(
            success=True,
            data=response,
        )
    except Exception as e:
        logger.exception("Failed to get operator session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get operator session: {str(e)}",
        )


@router.post(
    "/operator-login",
    response_model=ApiResponse[OperatorSession],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Operator login",
    description="""
    Login an operator using backend authentication.

    Authenticates with the backend server and stores the session.
    The operator info is used for 착공/완공 process tracking.
    """,
)
async def operator_login(
    request: OperatorLoginRequest,
    config: StationConfig = Depends(get_config),
    backend_client: BackendClient = Depends(get_backend_client),
) -> ApiResponse[OperatorSession]:
    """
    Login operator via backend.

    Args:
        request: Login credentials
        config: Station configuration
        backend_client: Backend API client

    Returns:
        ApiResponse[OperatorSession]: Operator session with login result
    """
    from station_service.core.exceptions import BackendConnectionError, BackendError

    try:
        # Check if backend is configured
        if not config.backend.url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend not configured. Set backend URL in station.yaml.",
            )

        # Ensure client is connected
        if not backend_client.is_connected:
            await backend_client.connect()

        # Authenticate with backend
        login_response = await backend_client.login(
            username=request.username,
            password=request.password,
        )

        # Extract user info
        access_token = login_response.get("access_token", "")
        user_info = login_response.get("user", {})

        if not access_token or not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login response from backend",
            )

        # Store session
        set_operator_session(
            operator={
                "id": user_info.get("id", 0),
                "username": user_info.get("username", request.username),
                "name": user_info.get("name", user_info.get("username", "")),
                "role": user_info.get("role", ""),
            },
            access_token=access_token,
        )

        session = get_operator_session()
        operator_info = OperatorInfo(
            id=session["operator"]["id"],
            username=session["operator"]["username"],
            name=session["operator"]["name"],
            role=session["operator"]["role"],
        )

        logger.info(f"Operator logged in: {operator_info.username} (ID: {operator_info.id})")

        return ApiResponse(
            success=True,
            data=OperatorSession(
                logged_in=True,
                operator=operator_info,
                access_token=None,  # Don't expose token
                logged_in_at=session["logged_in_at"],
            ),
            message=f"Welcome, {operator_info.name or operator_info.username}!",
        )

    except BackendConnectionError as e:
        logger.error(f"Backend connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to backend: {str(e)}",
        )
    except BackendError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message) if hasattr(e, "message") else "Login failed",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to login operator")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login: {str(e)}",
        )


@router.post(
    "/operator-logout",
    response_model=ApiResponse[OperatorSession],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Operator logout",
    description="""
    Logout the current operator.

    Clears the operator session from the station service.
    """,
)
async def operator_logout() -> ApiResponse[OperatorSession]:
    """
    Logout current operator.

    Returns:
        ApiResponse[OperatorSession]: Empty session state
    """
    try:
        session = get_operator_session()
        username = session["operator"]["username"] if session["operator"] else "unknown"

        clear_operator_session()

        logger.info(f"Operator logged out: {username}")

        return ApiResponse(
            success=True,
            data=OperatorSession(
                logged_in=False,
                operator=None,
                access_token=None,
                logged_in_at=None,
            ),
            message="Logged out successfully",
        )
    except Exception as e:
        logger.exception("Failed to logout operator")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}",
        )
