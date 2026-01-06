"""
Batch API routes for Station Service.

This module provides endpoints for batch management, including CRUD operations,
batch process control, sequence execution, and manual hardware control.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status

from station_service.api.dependencies import (
    get_batch_config_service,
    get_batch_manager,
    get_config,
    get_sequence_loader,
)
from station_service.api.routes.system import get_operator_session
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
    BatchUpdateRequest,
    BatchUpdateResponse,
    ManualControlRequest,
    ManualControlResponse,
    SequenceStartRequest,
    SequenceStartResponse,
    SequenceStopResponse,
    StepResult,
)
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.websocket import broadcast_batch_created, broadcast_batch_deleted
from station_service.batch.manager import BatchManager
from station_service.core.batch_config_service import BatchConfigService
from station_service.core.exceptions import (
    BatchAlreadyExistsError,
    BatchAlreadyRunningError,
    BatchError,
    BatchNotFoundError,
    BatchNotRunningError,
    BatchPersistenceError,
    BatchValidationError,
)
from station_service.models.config import BatchConfig, StationConfig
from station_service_sdk import SequenceLoader, collect_steps

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
                avg_duration=s.get("avgDuration", 0.0),
                last_duration=s.get("lastDuration", 0.0),
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
        stats = all_stats.get(batch_id, {"total": 0, "pass": 0, "fail": 0, "passRate": 0.0, "avgDuration": 0.0, "lastDuration": 0.0})

        return ApiResponse(
            success=True,
            data=BatchStatistics(
                total=stats.get("total", 0),
                pass_count=stats.get("pass", 0),
                fail=stats.get("fail", 0),
                pass_rate=stats.get("passRate", 0.0),
                avg_duration=stats.get("avgDuration", 0.0),
                last_duration=stats.get("lastDuration", 0.0),
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
        manifest = None
        sequence_version = "1.0.0"
        step_names: List[str] = []  # All step names from manifest

        # Load manifest for parameters and step metadata
        try:
            # Extract package name from sequence_package path (e.g., "sequences/psa_sensor_test" -> "psa_sensor_test")
            package_name = batch_config.sequence_package
            if package_name.startswith("sequences/"):
                package_name = package_name[len("sequences/"):]
            manifest = await sequence_loader.load_package(package_name)
            sequence_version = manifest.version
            # Get all step names from manifest (for displaying skipped steps)
            step_names = manifest.get_step_names()
        except Exception as e:
            logger.warning(f"Failed to load manifest for {batch_id}: {e}")

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
        elif manifest:
            # Load step metadata from sequence package
            try:
                package_path = sequence_loader.get_package_path(package_name)
                sequence_class = await sequence_loader.load_sequence_class(manifest, package_path)

                # Collect step metadata from the sequence class
                step_infos = collect_steps(sequence_class, manifest)

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

        # Merge parameters: manifest defaults + batch config overrides
        merged_parameters: Dict[str, Any] = {}
        if manifest and manifest.parameters:
            # Extract default values from manifest parameter definitions
            for param_name, param_def in manifest.parameters.items():
                if param_def.default is not None:
                    merged_parameters[param_name] = param_def.default
        # Batch config parameters override manifest defaults
        batch_params = status_data.get("parameters", {})
        merged_parameters.update(batch_params)

        # Update total_steps: prefer manifest step count, fall back to status_data or executed steps
        total_steps = len(step_names) if step_names else status_data.get("total_steps", 0)
        if total_steps == 0 and steps:
            total_steps = len(steps)

        # Build config object (merge legacy fields into config)
        batch_config_dict = dict(batch_config.config) if batch_config.config else {}
        # Legacy field migration: if not in config, add from legacy fields
        if "processId" not in batch_config_dict and batch_config.process_id:
            batch_config_dict["processId"] = batch_config.process_id
        if "headerId" not in batch_config_dict and batch_config.header_id:
            batch_config_dict["headerId"] = batch_config.header_id

        detail = BatchDetail(
            id=batch_id,
            name=status_data.get("name", ""),
            status=status_data.get("status", "idle"),
            sequence=BatchSequenceInfo(
                # Use 'or' to handle None values (not just missing keys)
                name=status_data.get("sequence_name") or batch_config.sequence_package or "",
                version=status_data.get("sequence_version") or sequence_version,
                package_path=batch_config.sequence_package or "",
            ),
            parameters=merged_parameters,
            config=batch_config_dict,
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
                step_names=step_names,  # Pass all step names for UI to display skipped steps
            ),
            last_run_passed=status_data.get("last_run_passed"),
            # Legacy fields for backward compatibility
            process_id=batch_config.get_process_id(),
            header_id=batch_config.get_header_id(),
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
    config: StationConfig = Depends(get_config),
) -> ApiResponse[SequenceStartResponse]:
    """
    Start sequence execution on a batch.
    """
    try:
        # Get batch config for parameters and process_id
        batch_config = batch_manager.get_batch_config(batch_id)

        # Merge parameters: batch config defaults + request overrides
        # Priority: batch_config.parameters < request.parameters < operator_id/process_id
        parameters: Dict[str, Any] = {}
        if batch_config and batch_config.parameters:
            parameters.update(batch_config.parameters)
        if request and request.parameters:
            parameters.update(request.parameters)

        # Check operator login and add operator_id for backend integration
        workflow = config.workflow
        if workflow.enabled:
            operator_session = get_operator_session()

            # Enforce login requirement if configured
            if workflow.require_operator_login and not operator_session["logged_in"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Operator login required. Please login via Settings page.",
                )

            # Add operator_id: prefer logged-in operator, fall back to default
            if operator_session["logged_in"] and operator_session["operator"]:
                parameters["operator_id"] = operator_session["operator"]["id"]
            elif workflow.default_operator_id:
                parameters["operator_id"] = workflow.default_operator_id

        # Add process_id from batch config for backend integration
        process_id = batch_config.get_process_id() if batch_config else None
        if process_id:
            parameters["process_id"] = process_id

        # Add header_id from batch config for backend integration
        header_id = batch_config.get_header_id() if batch_config else None
        if header_id:
            parameters["header_id"] = header_id

        # Add pre-validated wip_int_id to skip lookup in worker
        if request and request.wip_int_id:
            parameters["wip_int_id"] = request.wip_int_id

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
    except BatchError as e:
        # BatchError from worker (e.g., WIP not found, prerequisite not met)
        logger.warning(f"Batch error starting sequence on batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., 403 from operator login check)
        raise
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
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Create a new batch",
    description="""
    Create a new batch configuration.

    The batch is persisted to station.yaml and will survive server restarts.
    The batch can be started immediately after creation.
    """,
)
async def create_batch(
    request: BatchCreateRequest,
    config_service: BatchConfigService = Depends(get_batch_config_service),
) -> ApiResponse[BatchCreateResponse]:
    """
    Create a new batch configuration with YAML persistence.
    """
    try:
        # Merge config: request.config takes priority over legacy fields
        merged_config = dict(request.config) if request.config else {}
        if request.process_id and "processId" not in merged_config:
            merged_config["processId"] = request.process_id
        if request.header_id and "headerId" not in merged_config:
            merged_config["headerId"] = request.header_id

        # Create BatchConfig from request
        batch_config = BatchConfig(
            id=request.id,
            name=request.name,
            sequence_package=request.sequence_package,
            hardware=request.hardware,
            auto_start=request.auto_start,
            config=merged_config,
            parameters=request.parameters,
            process_id=request.process_id,  # Pass process_id directly for YAML persistence
        )

        # Create via service (persists to YAML + memory)
        await config_service.create_batch(batch_config)

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

    except BatchAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except BatchValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except BatchPersistenceError as e:
        logger.exception(f"Error persisting batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
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
    The batch is removed from both memory and station.yaml.
    """,
)
async def delete_batch(
    batch_id: str = Path(..., description="Unique batch identifier"),
    batch_manager: BatchManager = Depends(get_batch_manager),
    config_service: BatchConfigService = Depends(get_batch_config_service),
) -> ApiResponse[BatchDeleteResponse]:
    """
    Delete a batch configuration with YAML persistence.

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
                raise BatchAlreadyRunningError(batch_id)

        # Delete via service (removes from YAML + memory)
        await config_service.delete_batch(batch_id)

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
            detail=f"Cannot delete batch '{batch_id}' while sequence is running. Stop the sequence first.",
        )
    except BatchValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except BatchPersistenceError as e:
        logger.exception(f"Error persisting batch deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error deleting batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/{batch_id}",
    response_model=ApiResponse[BatchUpdateResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Update a batch",
    description="""
    Update a batch configuration.

    Only provided fields are updated. The batch ID cannot be changed.
    Running batches cannot be updated - stop the sequence first.
    Changes are persisted to station.yaml.
    """,
)
async def update_batch(
    batch_id: str = Path(..., description="Unique batch identifier"),
    request: BatchUpdateRequest = None,
    config_service: BatchConfigService = Depends(get_batch_config_service),
) -> ApiResponse[BatchUpdateResponse]:
    """
    Update a batch configuration with YAML persistence.
    """
    try:
        # Get updates from request (exclude None values)
        updates = request.model_dump(exclude_unset=True) if request else {}

        if not updates:
            raise BatchValidationError("No updates provided")

        # Update via service (persists to YAML + memory)
        await config_service.update_batch(batch_id, updates)

        return ApiResponse(
            success=True,
            data=BatchUpdateResponse(
                batch_id=batch_id,
                status="updated",
            ),
        )

    except BatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found",
        )
    except BatchValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except BatchPersistenceError as e:
        logger.exception(f"Error persisting batch update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error updating batch {batch_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
