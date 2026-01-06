"""
Health and system information routes.

Provides endpoints for:
- System information (/info)
- Health check (/health)
- Sync status (/sync-status)
- Force sync (/sync/force)
- Station info update (/station-info)
"""

import logging
import shutil
import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from station_service.api.dependencies import (
    get_batch_manager,
    get_config,
    get_config_path,
    get_database,
    get_sync_engine,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.schemas.result import HealthStatus, SystemInfo
from station_service.api.routes.system.schemas import (
    BackendConfigResponse,
    SyncStatus,
    UpdateBackendConfigRequest,
    UpdateStationInfoRequest,
)
from station_service.batch.manager import BatchManager
from station_service.models.config import BackendConfig, StationConfig, StationInfo
from station_service.storage.database import Database
from station_service.sync.engine import SyncEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Track service start time for uptime calculation
_service_start_time: float = time.time()

# Service version
SERVICE_VERSION = "1.0.0"


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

    Returns:
        ApiResponse[SystemInfo]: Station system information wrapped in standard response
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
            sequences_dir=config.paths.sequences_dir,
            data_dir=config.paths.data_dir,
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


@router.put(
    "/station-info",
    response_model=ApiResponse[SystemInfo],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Update station information",
)
async def update_station_info(
    request: UpdateStationInfoRequest,
    config: StationConfig = Depends(get_config),
    sync_engine: SyncEngine = Depends(get_sync_engine),
    config_path: str = Depends(get_config_path),
) -> ApiResponse[SystemInfo]:
    """Update station information in the configuration file."""
    from pathlib import Path
    from station_service.core.config_writer import update_station_info as write_station_info

    try:
        station_info = StationInfo(
            id=request.id,
            name=request.name,
            description=request.description,
        )

        updated_config = await write_station_info(Path(config_path), station_info)
        config.station = updated_config.station

        uptime_seconds = int(time.time() - _service_start_time)

        system_info = SystemInfo(
            station_id=updated_config.station.id,
            station_name=updated_config.station.name,
            description=updated_config.station.description,
            version=SERVICE_VERSION,
            uptime=uptime_seconds,
            backend_connected=sync_engine.is_connected if sync_engine.is_running else False,
            sequences_dir=config.paths.sequences_dir,
            data_dir=config.paths.data_dir,
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
)
async def get_health(
    batch_manager: BatchManager = Depends(get_batch_manager),
    sync_engine: SyncEngine = Depends(get_sync_engine),
    database: Database = Depends(get_database),
) -> ApiResponse[HealthStatus]:
    """Perform a health check on the Station Service."""
    try:
        batches_running = len(batch_manager.running_batch_ids)
        backend_connected = sync_engine.is_connected if sync_engine.is_running else False
        backend_status = "connected" if backend_connected else "disconnected"
        disk_usage = _get_disk_usage()

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
)
async def get_sync_status(
    sync_engine: SyncEngine = Depends(get_sync_engine),
    database: Database = Depends(get_database),
) -> ApiResponse[SyncStatus]:
    """Get sync queue status."""
    try:
        from station_service.storage.repositories.sync_repository import SyncRepository

        sync_repo = SyncRepository(database)

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
)
async def force_sync(
    sync_engine: SyncEngine = Depends(get_sync_engine),
) -> ApiResponse[Dict[str, int]]:
    """Force sync all pending items."""
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
        total, used, free = shutil.disk_usage(".")
        return round((used / total) * 100, 2)
    except Exception:
        return 0.0


def _determine_health_status(
    database_connected: bool,
    backend_connected: bool,
    disk_usage: float,
) -> str:
    """Determine overall health status based on component states."""
    if not database_connected:
        return "unhealthy"

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


def _mask_api_key(api_key: str) -> str:
    """Mask API key for display, showing only first 4 characters."""
    if not api_key or len(api_key) < 8:
        return "***"
    return f"{api_key[:4]}...***"


@router.get(
    "/backend-config",
    response_model=ApiResponse[BackendConfigResponse],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get backend configuration",
    description="Retrieve current backend connection configuration. API key is masked for security.",
)
async def get_backend_config(
    config: StationConfig = Depends(get_config),
) -> ApiResponse[BackendConfigResponse]:
    """Get backend configuration (API key masked)."""
    try:
        backend_response = BackendConfigResponse(
            url=config.backend.url,
            api_key_masked=_mask_api_key(config.backend.api_key),
            sync_interval=config.backend.sync_interval,
            station_id=config.backend.station_id,
            timeout=config.backend.timeout,
            max_retries=config.backend.max_retries,
        )

        return ApiResponse(
            success=True,
            data=backend_response,
        )
    except Exception as e:
        logger.exception("Failed to get backend config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backend config: {str(e)}",
        )


@router.put(
    "/backend-config",
    response_model=ApiResponse[BackendConfigResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Update backend configuration",
    description="Update backend connection settings. API key cannot be modified through this endpoint.",
)
async def update_backend_config(
    request: UpdateBackendConfigRequest,
    config: StationConfig = Depends(get_config),
    config_path: str = Depends(get_config_path),
) -> ApiResponse[BackendConfigResponse]:
    """Update backend configuration (API key is preserved)."""
    from pathlib import Path
    from station_service.core.config_writer import update_backend_config as write_backend_config

    try:
        # Merge request with current config (partial update)
        updated_backend = BackendConfig(
            url=request.url if request.url is not None else config.backend.url,
            api_key=config.backend.api_key,  # Always preserve existing API key
            sync_interval=request.sync_interval if request.sync_interval is not None else config.backend.sync_interval,
            station_id=request.station_id if request.station_id is not None else config.backend.station_id,
            timeout=request.timeout if request.timeout is not None else config.backend.timeout,
            max_retries=request.max_retries if request.max_retries is not None else config.backend.max_retries,
        )

        # Write to config file
        updated_config = await write_backend_config(Path(config_path), updated_backend)

        # Update in-memory config
        config.backend = updated_config.backend

        backend_response = BackendConfigResponse(
            url=updated_config.backend.url,
            api_key_masked=_mask_api_key(updated_config.backend.api_key),
            sync_interval=updated_config.backend.sync_interval,
            station_id=updated_config.backend.station_id,
            timeout=updated_config.backend.timeout,
            max_retries=updated_config.backend.max_retries,
        )

        return ApiResponse(
            success=True,
            data=backend_response,
            message="Backend configuration updated successfully",
        )

    except FileNotFoundError as e:
        logger.error(f"Config file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration file not found",
        )
    except Exception as e:
        logger.exception("Failed to update backend config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update backend config: {str(e)}",
        )
