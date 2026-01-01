"""
Batch API routes for Station Service.

This module provides endpoints for batch management, including CRUD operations,
batch process control, sequence execution, and manual hardware control.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status

from station_service.api.dependencies import get_batch_manager, get_config, get_sequence_loader
from station_service.api.schemas.batch import (
    BatchCreateRequest,
    BatchCreateResponse,
    BatchDeleteResponse,
    BatchDetail,
    BatchExecution,
    BatchSequenceInfo,
    BatchStartResponse,
    BatchStatistics,
    BatchStopResponse,
    BatchSummary,
    ManualControlRequest,
    ManualControlResponse,
    SequenceStartRequest,
    SequenceStartResponse,
    SequenceStopResponse,
    StepResult,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.batch.manager import BatchManager
from station_service.core.exceptions import (
    BatchAlreadyRunningError,
    BatchError,
    BatchNotFoundError,
    BatchNotRunningError,
)
from station_service.models.config import BatchConfig, StationConfig
from station_service.api.websocket import broadcast_batch_created, broadcast_batch_deleted
from station_service.sequence.loader import SequenceLoader
from station_service.sequence.decorators import collect_steps

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/batches", tags=["Batches"])


@router.get(
    "",
    response_model=ApiResponse[List[BatchSummary]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="List all batches",
    description="""
    Retrieve a list of all configured batches.

    Returns summary information for each batch including:
    - Batch ID and name
    - Current status
    - Assigned sequence name and version
    - Current execution progress
    """,
)
async def list_batches(
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[List[BatchSummary]]:
    """
    List all configured batches.

    This endpoint returns a summary of all batches configured in the station,
    including their current execution status and progress.

    Returns:
        ApiResponse[List[BatchSummary]]: List of batch summaries wrapped in standard response
    """
    try:
        statuses = await batch_manager.get_all_batch_statuses()

        summaries = []
        for status_data in statuses:
            summaries.append(BatchSummary(
                id=status_data.get("id", ""),
                name=status_data.get("name", ""),
                status=status_data.get("status", "idle"),
                sequence_name=status_data.get("sequence_name", ""),
                sequence_version=status_data.get("sequence_version", ""),
                current_step=status_data.get("current_step"),
                step_index=status_data.get("step_index", 0),
                total_steps=status_data.get("total_steps", 0),
                progress=status_data.get("progress", 0.0),
                started_at=status_data.get("started_at"),
                elapsed=status_data.get("elapsed", 0.0),
            ))

        return ApiResponse(success=True, data=summaries)

    except Exception as e:
        logger.exception(f"Error listing batches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/statistics",
    response_model=ApiResponse[Dict[str, BatchStatistics]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get all batch statistics",
    description="""
    Retrieve execution statistics for all batches.

    Returns a dictionary mapping batch IDs to their statistics:
    - Total number of executions
    - Number of passed/failed executions
    - Pass rate
    """,
)
async def get_all_batch_statistics(
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[Dict[str, BatchStatistics]]:
    """
    Get execution statistics for all batches.
    """
    try:
        stats = await batch_manager.get_all_batch_statistics()
        result = {
            batch_id: BatchStatistics(
                total=s.get("total", 0),
                pass_count=s.get("pass", 0),
                fail=s.get("fail", 0),
                pass_rate=s.get("passRate", 0.0),
            )
            for batch_id, s in stats.items()
        }
        return ApiResponse(success=True, data=result)

    except Exception as e:
        logger.exception(f"Error getting batch statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{batch_id}/statistics",
    response_model=ApiResponse[BatchStatistics],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get batch statistics",
    description="""
    Retrieve execution statistics for a specific batch.

    Returns statistics including:
    - Total number of executions
    - Number of passed/failed executions
    - Pass rate
    """,
)
async def get_batch_statistics(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[BatchStatistics]:
    """
    Get execution statistics for a specific batch.
    """
    try:
        all_stats = await batch_manager.get_all_batch_statistics()
        stats = all_stats.get(batch_id, {"total": 0, "pass": 0, "fail": 0, "passRate": 0.0})

        return ApiResponse(
            success=True,
            data=BatchStatistics(
                total=stats.get("total", 0),
                pass_count=stats.get("pass", 0),
                fail=stats.get("fail", 0),
                passRate=stats.get("passRate", 0.0),
            ),
        )

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch not found: {batch_id}",
        )
    except Exception as e:
        logger.exception(f"Error getting batch statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{batch_id}",
    response_model=ApiResponse[BatchDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get batch details",
    description="""
    Retrieve detailed information for a specific batch.

    Returns comprehensive batch information including:
    - Batch configuration
    - Assigned sequence details
    - Runtime parameters
    - Hardware status
    - Current execution state and step results
    """,
)
async def get_batch(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[BatchDetail]:
    """
    Get detailed information for a specific batch.
    """
    try:
        status_data = await batch_manager.get_batch_status(batch_id)

        # Get batch config from manager (supports both static YAML and runtime-created batches)
        batch_config = batch_manager.get_batch_config(batch_id)

        if batch_config is None:
            raise BatchNotFoundError(batch_id)

        # Get hardware status
        hardware_status = await batch_manager.get_hardware_status(batch_id)

        # Build steps from status_data
        steps_data = status_data.get("steps", [])
        steps: List[StepResult] = []

        if steps_data:
            # Use steps from execution status
            steps = [
                StepResult(
                    name=s.get("name", ""),
                    status=s.get("status", "pending"),
                    duration=s.get("duration"),
                    result=s.get("result"),
                )
                for s in steps_data
            ]
        else:
            # Load step metadata from sequence package
            try:
                package_name = batch_config.sequence_package
                manifest = await sequence_loader.load_package(package_name)
                package_path = sequence_loader.get_package_path(package_name)
                sequence_class = await sequence_loader.load_sequence_class(manifest, package_path)

                # Collect step metadata from the sequence class
                step_infos = collect_steps(sequence_class)

                # Create placeholder steps with pending status
                for idx, (method_name, _, step_meta) in enumerate(step_infos):
                    step_name = step_meta.name or method_name
                    steps.append(StepResult(
                        name=step_name,
                        status="pending",
                        duration=None,
                        result=None,
                    ))
            except Exception as e:
                logger.warning(f"Failed to load sequence steps for {batch_id}: {e}")
                # Continue without step metadata

        # Update total_steps if we have steps from sequence
        total_steps = status_data.get("total_steps", 0)
        if total_steps == 0 and steps:
            total_steps = len(steps)

        detail = BatchDetail(
            id=batch_id,
            name=status_data.get("name", ""),
            status=status_data.get("status", "idle"),
            sequence=BatchSequenceInfo(
                # Use 'or' to handle None values (not just missing keys)
                name=status_data.get("sequence_name") or batch_config.sequence_package or "",
                version=status_data.get("sequence_version") or "1.0.0",
                package_path=batch_config.sequence_package or "",
            ),
            parameters=status_data.get("parameters", {}),
            hardware=hardware_status,
            execution=BatchExecution(
                status=status_data.get("status", "idle"),
                current_step=status_data.get("current_step"),
                step_index=status_data.get("step_index", 0),
                total_steps=total_steps,
                progress=status_data.get("progress", 0.0),
                started_at=status_data.get("started_at"),
                elapsed=status_data.get("elapsed", 0.0),
                steps=steps,
            ),
        )

        return ApiResponse(success=True, data=detail)

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except Exception as e:
        logger.exception(f"Error getting batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{batch_id}/start",
    response_model=ApiResponse[BatchStartResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Start batch process",
    description="""
    Start the batch process for a specific batch.

    This initializes the batch process which:
    - Loads the assigned sequence package
    - Initializes hardware connections
    - Prepares for sequence execution

    The batch must be in 'idle' status to start.
    """,
)
async def start_batch(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[BatchStartResponse]:
    """
    Start the batch process.
    """
    try:
        batch_process = await batch_manager.start_batch(batch_id)

        return ApiResponse(
            success=True,
            data=BatchStartResponse(
                batch_id=batch_id,
                status="started",
                pid=batch_process.pid or 0,
            ),
        )

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except BatchAlreadyRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is already running",
        )
    except Exception as e:
        logger.exception(f"Error starting batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{batch_id}/stop",
    response_model=ApiResponse[BatchStopResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Stop batch process",
    description="""
    Stop the batch process for a specific batch.

    This terminates the batch process:
    - Stops any running sequence execution
    - Closes hardware connections
    - Cleans up resources

    The batch must be in 'running' status to stop.
    """,
)
async def stop_batch(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[BatchStopResponse]:
    """
    Stop the batch process.
    """
    try:
        await batch_manager.stop_batch(batch_id)

        return ApiResponse(
            success=True,
            data=BatchStopResponse(
                batch_id=batch_id,
                status="stopped",
            ),
        )

    except BatchNotRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is not running",
        )
    except Exception as e:
        logger.exception(f"Error stopping batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{batch_id}/sequence/start",
    response_model=ApiResponse[SequenceStartResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Start sequence execution",
    description="""
    Start sequence execution on a specific batch.

    This triggers the execution of the assigned sequence with optional runtime parameters.
    The batch process must be running before starting sequence execution.

    Request body allows specifying runtime parameters that override sequence defaults.
    """,
)
async def start_sequence(
    batch_id: str = Path(..., description="Unique batch identifier"),
    request: Optional[SequenceStartRequest] = None,
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[SequenceStartResponse]:
    """
    Start sequence execution on a batch.
    """
    try:
        parameters = request.parameters if request else {}
        execution_id = await batch_manager.start_sequence(batch_id, parameters)

        return ApiResponse(
            success=True,
            data=SequenceStartResponse(
                batch_id=batch_id,
                execution_id=execution_id,
                status="started",
            ),
        )

    except BatchNotRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is not running. Start the batch first.",
        )
    except Exception as e:
        logger.exception(f"Error starting sequence on batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{batch_id}/sequence/stop",
    response_model=ApiResponse[SequenceStopResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Stop sequence execution",
    description="""
    Stop the currently running sequence execution on a batch.

    This interrupts the sequence execution:
    - Completes the current step if possible
    - Runs cleanup steps if defined
    - Records the execution result as 'stopped'
    """,
)
async def stop_sequence(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[SequenceStopResponse]:
    """
    Stop sequence execution on a batch.
    """
    try:
        await batch_manager.stop_sequence(batch_id)

        return ApiResponse(
            success=True,
            data=SequenceStopResponse(
                batch_id=batch_id,
                status="stopped",
            ),
        )

    except BatchNotRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is not running",
        )
    except Exception as e:
        logger.exception(f"Error stopping sequence on batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{batch_id}/manual",
    response_model=ApiResponse[ManualControlResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Execute manual control command",
    description="""
    Execute a manual control command on batch hardware.

    Allows direct control of hardware devices for testing and debugging:
    - Specify the hardware device ID
    - Provide the command to execute
    - Include any command parameters

    Note: Manual control is only available when no sequence is running.
    """,
)
async def manual_control(
    request: ManualControlRequest,
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[ManualControlResponse]:
    """
    Execute a manual control command on batch hardware.
    """
    try:
        result = await batch_manager.manual_control(
            batch_id=batch_id,
            hardware=request.hardware,
            command=request.command,
            params=request.params,
        )

        return ApiResponse(
            success=True,
            data=ManualControlResponse(
                hardware=request.hardware,
                command=request.command,
                result=result,
            ),
        )

    except BatchNotRunningError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Batch '{batch_id}' is not running",
        )
    except Exception as e:
        logger.exception(f"Error executing manual control on batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============================================================================
# Batch CRUD Endpoints
# ============================================================================


@router.post(
    "",
    response_model=ApiResponse[BatchCreateResponse],
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Create a new batch",
    description="""
    Create a new batch configuration at runtime.

    This adds a new batch to the station without modifying the YAML config.
    The batch can be started immediately after creation.

    Note: Runtime batches are not persisted and will be lost on station restart.
    """,
)
async def create_batch(
    request: BatchCreateRequest,
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[BatchCreateResponse]:
    """
    Create a new batch configuration.
    """
    try:
        # Create BatchConfig from request
        batch_config = BatchConfig(
            id=request.id,
            name=request.name,
            sequence_package=request.sequence_package,
            hardware=request.hardware,
            auto_start=request.auto_start,
            process_id=request.process_id,
        )

        # Add to manager
        batch_manager.add_batch(batch_config)

        # Broadcast batch created event via WebSocket
        await broadcast_batch_created(
            batch_id=request.id,
            name=request.name,
            sequence_package=request.sequence_package,
        )

        return ApiResponse(
            success=True,
            data=BatchCreateResponse(
                batch_id=request.id,
                name=request.name,
                status="created",
            ),
        )

    except BatchError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error creating batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/{batch_id}",
    response_model=ApiResponse[BatchDeleteResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Delete a batch",
    description="""
    Delete a batch configuration.

    If the batch process is running but idle (no active sequence),
    it will be stopped automatically before deletion.

    If the batch has an active sequence running, deletion will be rejected.
    This removes the batch from runtime configuration only.

    Note: This does not modify the YAML config file.
    """,
)
async def delete_batch(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
) -> ApiResponse[BatchDeleteResponse]:
    """
    Delete a batch configuration.

    Automatically stops idle batch processes before deletion.
    """
    try:
        # Check if batch process is running but in idle state (sequence completed)
        if batch_id in batch_manager.running_batch_ids:
            # Get the batch status to check if sequence is running
            batch_status = await batch_manager.get_batch_status(batch_id)
            execution_status = batch_status.get("status", "idle")

            # Only allow auto-stop if the batch is idle (no active sequence)
            if execution_status in ("idle", "completed", "error"):
                logger.info(f"Auto-stopping idle batch '{batch_id}' before deletion")
                await batch_manager.stop_batch(batch_id)
            else:
                # Sequence is actively running - cannot delete
                raise BatchAlreadyRunningError(
                    f"Cannot delete batch '{batch_id}' while sequence is running. Stop the sequence first."
                )

        batch_manager.remove_batch(batch_id)

        # Broadcast batch deleted event via WebSocket
        await broadcast_batch_deleted(batch_id)

        return ApiResponse(
            success=True,
            data=BatchDeleteResponse(
                batch_id=batch_id,
                status="deleted",
            ),
        )

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except BatchAlreadyRunningError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error deleting batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
