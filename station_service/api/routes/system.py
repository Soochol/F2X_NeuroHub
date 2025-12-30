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
    get_config,
    get_database,
    get_sync_engine,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.schemas.result import HealthStatus, SystemInfo
from station_service.batch.manager import BatchManager
from station_service.models.config import StationConfig
from station_service.storage.database import Database
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
