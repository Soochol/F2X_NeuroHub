"""
Manual Control API Routes for Station Service.

This module provides endpoints for enhanced manual hardware control,
including command discovery, step-by-step execution, and presets.
"""

import logging
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, status

from station_service.api.dependencies import get_batch_manager
from station_service.api.schemas.manual import (
    CommandInfo,
    CommandPreset,
    CommandPresetCreate,
    HardwareCommandsResponse,
    HardwareDetailedStatus,
    ManualStepInfo,
    ManualStepRequest,
    ParameterInfo,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.batch.manager import BatchManager
from station_service.core.exceptions import BatchNotFoundError, BatchNotRunningError
from station_service.hardware.introspection import (
    discover_driver_commands,
    get_driver_info,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/manual", tags=["Manual Control"])

# In-memory preset storage (in production, use database)
_presets: Dict[str, CommandPreset] = {}


@router.get(
    "/batches/{batch_id}/hardware",
    response_model=ApiResponse[List[HardwareDetailedStatus]],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Get all hardware devices for a batch",
    description="""
    Get detailed status of all hardware devices for a batch.
    The batch must be started (running) to access hardware.
    """,
)
async def get_batch_hardware(
    batch_id: str = Path(..., description="Batch ID"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[List[HardwareDetailedStatus]]:
    """Get all hardware devices for a batch."""
    try:
        hardware_status = await batch_manager.get_hardware_status(batch_id)

        devices = []
        for hw_id, hw_status in hardware_status.items():
            devices.append(HardwareDetailedStatus(
                id=hw_id,
                driver=hw_status.get("driver", "Unknown"),
                status=hw_status.get("status", "disconnected"),
                connected=hw_status.get("status") == "connected",
                config=hw_status.get("config", {}),
                info=hw_status.get("info", {}),
                last_error=hw_status.get("last_error") or hw_status.get("lastError"),
            ))

        return ApiResponse(success=True, data=devices)

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except Exception as e:
        logger.exception(f"Error getting hardware status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/batches/{batch_id}/hardware/{hardware_id}/commands",
    response_model=ApiResponse[HardwareCommandsResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Get available commands for a hardware device",
    description="""
    Discover available commands for a specific hardware device.
    Uses introspection to extract method signatures and documentation.
    The batch must be started (running) to access hardware.
    """,
)
async def get_hardware_commands(
    batch_id: str = Path(..., description="Batch ID"),
    hardware_id: str = Path(..., description="Hardware device ID"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[HardwareCommandsResponse]:
    """Get available commands for a hardware device."""
    try:
        # Get the driver instance from the batch worker
        driver = await batch_manager.get_driver_instance(batch_id, hardware_id)

        if driver is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hardware '{hardware_id}' not found in batch '{batch_id}'",
            )

        # Discover commands using introspection
        command_defs = discover_driver_commands(driver)
        driver_info = get_driver_info(driver)

        commands = [
            CommandInfo(
                name=cmd.name,
                display_name=cmd.display_name,
                description=cmd.description,
                category=cmd.category,
                parameters=[
                    ParameterInfo(**p.to_dict())
                    for p in cmd.parameters
                ],
                return_type=cmd.return_type,
                return_unit=cmd.return_unit,
                is_async=cmd.is_async,
            )
            for cmd in command_defs
        ]

        return ApiResponse(
            success=True,
            data=HardwareCommandsResponse(
                hardware_id=hardware_id,
                driver=driver_info["className"],
                connected=driver_info["connected"],
                commands=commands,
            ),
        )

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except BatchNotRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is not running. Start the batch first.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error discovering commands: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/batches/{batch_id}/sequence/steps",
    response_model=ApiResponse[List[ManualStepInfo]],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Get sequence steps for manual execution",
    description="""
    Get the list of steps available for manual execution.
    Returns step metadata including skip/retry options and parameter overrides.
    """,
)
async def get_manual_steps(
    batch_id: str = Path(..., description="Batch ID"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[List[ManualStepInfo]]:
    """Get sequence steps for manual execution."""
    try:
        steps = await batch_manager.get_manual_steps(batch_id)

        step_infos = []
        for idx, step in enumerate(steps):
            step_infos.append(ManualStepInfo(
                name=step.get("name", f"step_{idx}"),
                display_name=step.get("display_name") or step.get("displayName") or step.get("name", f"Step {idx + 1}"),
                order=step.get("order", idx + 1),
                timeout=step.get("timeout", 60.0),
                status=step.get("status", "pending"),
                result=step.get("result"),
                duration=step.get("duration"),
            ))

        return ApiResponse(success=True, data=step_infos)

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except Exception as e:
        logger.exception(f"Error getting manual steps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/batches/{batch_id}/sequence/steps/{step_name}/run",
    response_model=ApiResponse[Dict],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Execute a single step manually",
    description="""
    Execute a single step in manual mode with optional parameter overrides.
    """,
)
async def run_manual_step(
    batch_id: str = Path(..., description="Batch ID"),
    step_name: str = Path(..., description="Step name"),
    request: ManualStepRequest = None,
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[Dict]:
    """Execute a single step manually."""
    try:
        result = await batch_manager.run_manual_step(
            batch_id=batch_id,
            step_name=step_name,
            parameter_overrides=request.parameters if request else None,
        )

        return ApiResponse(success=True, data=result)

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except BatchNotRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is not running",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error running manual step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/batches/{batch_id}/sequence/steps/{step_name}/skip",
    response_model=ApiResponse[Dict],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    },
    summary="Skip a step in manual mode",
    description="""
    Skip a step in manual mode. Only works for steps marked as skippable.
    """,
)
async def skip_manual_step(
    batch_id: str = Path(..., description="Batch ID"),
    step_name: str = Path(..., description="Step name"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[Dict]:
    """Skip a step in manual mode."""
    try:
        result = await batch_manager.skip_manual_step(batch_id, step_name)
        return ApiResponse(success=True, data=result)

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error skipping step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/batches/{batch_id}/sequence/reset",
    response_model=ApiResponse[Dict],
    summary="Reset manual sequence execution",
    description="""
    Reset manual sequence execution state.
    Clears all step results and resets to initial state.
    """,
)
async def reset_manual_sequence(
    batch_id: str = Path(..., description="Batch ID"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[Dict]:
    """Reset manual sequence execution."""
    try:
        await batch_manager.reset_manual_sequence(batch_id)
        return ApiResponse(success=True, data={"status": "reset"})

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except Exception as e:
        logger.exception(f"Error resetting sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============================================================================
# Command Presets
# ============================================================================


@router.get(
    "/presets",
    response_model=ApiResponse[List[CommandPreset]],
    summary="List all command presets",
)
async def list_presets() -> ApiResponse[List[CommandPreset]]:
    """List all saved command presets."""
    return ApiResponse(success=True, data=list(_presets.values()))


@router.post(
    "/presets",
    response_model=ApiResponse[CommandPreset],
    summary="Create a command preset",
)
async def create_preset(
    request: CommandPresetCreate,
) -> ApiResponse[CommandPreset]:
    """Create a new command preset."""
    preset_id = str(uuid4())[:8]
    preset = CommandPreset(
        id=preset_id,
        name=request.name,
        hardware_id=request.hardware_id,
        command=request.command,
        params=request.params,
        created_at=datetime.now().isoformat(),
    )
    _presets[preset_id] = preset
    return ApiResponse(success=True, data=preset)


@router.delete(
    "/presets/{preset_id}",
    response_model=ApiResponse[Dict],
    summary="Delete a command preset",
)
async def delete_preset(
    preset_id: str = Path(..., description="Preset ID"),
) -> ApiResponse[Dict]:
    """Delete a command preset."""
    if preset_id not in _presets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_id}' not found",
        )
    del _presets[preset_id]
    return ApiResponse(success=True, data={"status": "deleted"})
