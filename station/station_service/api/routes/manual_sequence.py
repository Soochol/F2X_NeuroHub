"""
Manual Sequence API Routes for Station Service.

This module provides endpoints for manual step-by-step sequence execution
with real hardware, without requiring a Batch.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field

from station_service.api.dependencies import get_sequence_loader
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service_sdk import (
    SequenceLoader,
    ManualSequenceExecutor,
    ManualSession,
    ManualSessionStatus,
    ManualStepState,
    ManualStepStatus,
    HardwareState,
    CommandResult,
    DriverLoadError,
    DriverConnectionError,
    PackageError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/manual-sequence", tags=["Manual Sequence"])


# ============================================================================
# Executor Singleton
# ============================================================================

_executor: Optional[ManualSequenceExecutor] = None


def get_manual_executor(
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ManualSequenceExecutor:
    """Get or create the manual sequence executor singleton."""
    global _executor
    if _executor is None:
        _executor = ManualSequenceExecutor(sequence_loader, sequences_dir="sequences")
    return _executor


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateManualSessionRequest(BaseModel):
    """Request to create a manual test session."""

    sequence_name: str = Field(..., description="Name of the sequence to execute")
    hardware_config: Optional[Dict[str, Dict[str, Any]]] = Field(
        None, description="Hardware configuration per hardware ID"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameter overrides"
    )


class RunStepRequest(BaseModel):
    """Request to run a step."""

    parameter_overrides: Optional[Dict[str, Any]] = Field(
        None, description="Parameter overrides for this step"
    )


class ExecuteCommandRequest(BaseModel):
    """Request to execute a hardware command."""

    command: str = Field(..., description="Command name to execute")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Command parameters"
    )


class HardwareStateResponse(BaseModel):
    """Hardware state response."""

    id: str
    display_name: str = Field(..., alias="displayName")
    connected: bool
    driver_class: Optional[str] = Field(None, alias="driverClass")
    config: Dict[str, Any] = Field(default_factory=dict)
    commands: List[str] = Field(default_factory=list)
    error: Optional[str] = None

    model_config = {"populate_by_name": True}


class ManualStepResponse(BaseModel):
    """Manual step state response."""

    name: str
    display_name: str = Field(..., alias="displayName")
    order: int
    skippable: bool
    status: str
    started_at: Optional[str] = Field(None, alias="startedAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")
    duration: float
    result: Optional[Dict[str, Any]] = None
    measurements: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    parameter_overrides: List[str] = Field(default_factory=list, alias="parameterOverrides")

    model_config = {"populate_by_name": True}


class ManualSessionSummary(BaseModel):
    """Summary of a manual test session."""

    id: str
    sequence_name: str = Field(..., alias="sequenceName")
    sequence_version: str = Field(..., alias="sequenceVersion")
    status: str
    created_at: str = Field(..., alias="createdAt")
    started_at: Optional[str] = Field(None, alias="startedAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")
    current_step_index: int = Field(..., alias="currentStepIndex")
    total_steps: int = Field(..., alias="totalSteps")
    passed_steps: int = Field(..., alias="passedSteps")
    failed_steps: int = Field(..., alias="failedSteps")
    hardware_connected: int = Field(..., alias="hardwareConnected")
    hardware_total: int = Field(..., alias="hardwareTotal")
    overall_pass: bool = Field(..., alias="overallPass")

    model_config = {"populate_by_name": True}


class ManualSessionDetail(BaseModel):
    """Detailed manual session information."""

    id: str
    sequence_name: str = Field(..., alias="sequenceName")
    sequence_version: str = Field(..., alias="sequenceVersion")
    status: str
    created_at: str = Field(..., alias="createdAt")
    started_at: Optional[str] = Field(None, alias="startedAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")
    current_step_index: int = Field(..., alias="currentStepIndex")
    steps: List[ManualStepResponse]
    hardware: List[HardwareStateResponse]
    parameters: Dict[str, Any]
    hardware_config: Dict[str, Dict[str, Any]] = Field(..., alias="hardwareConfig")
    overall_pass: bool = Field(..., alias="overallPass")
    error: Optional[str] = None

    model_config = {"populate_by_name": True}


class CommandResultResponse(BaseModel):
    """Hardware command execution result."""

    success: bool
    hardware_id: str = Field(..., alias="hardwareId")
    command: str
    result: Optional[Any] = None
    error: Optional[str] = None
    duration: float

    model_config = {"populate_by_name": True}


class CommandDefinition(BaseModel):
    """Hardware command definition."""

    name: str
    display_name: str = Field(..., alias="displayName")
    description: Optional[str] = None
    category: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    returns: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}


# ============================================================================
# Helper Functions
# ============================================================================


def session_to_summary(session: ManualSession) -> ManualSessionSummary:
    """Convert session to summary."""
    passed = sum(1 for s in session.steps if s.status == ManualStepStatus.PASSED)
    failed = sum(1 for s in session.steps if s.status == ManualStepStatus.FAILED)
    hw_connected = sum(1 for h in session.hardware if h.connected)

    return ManualSessionSummary(
        id=session.id,
        sequenceName=session.sequence_name,
        sequenceVersion=session.sequence_version,
        status=session.status.value,
        createdAt=session.created_at.isoformat(),
        startedAt=session.started_at.isoformat() if session.started_at else None,
        completedAt=session.completed_at.isoformat() if session.completed_at else None,
        currentStepIndex=session.current_step_index,
        totalSteps=len(session.steps),
        passedSteps=passed,
        failedSteps=failed,
        hardwareConnected=hw_connected,
        hardwareTotal=len(session.hardware),
        overallPass=session.overall_pass,
    )


def step_to_response(step: ManualStepState) -> ManualStepResponse:
    """Convert step state to response."""
    return ManualStepResponse(
        name=step.name,
        displayName=step.display_name,
        order=step.order,
        skippable=step.skippable,
        status=step.status.value,
        startedAt=step.started_at.isoformat() if step.started_at else None,
        completedAt=step.completed_at.isoformat() if step.completed_at else None,
        duration=step.duration,
        result=step.result,
        measurements=step.measurements,
        error=step.error,
        parameterOverrides=step.parameter_overrides,
    )


def hw_to_response(hw: HardwareState) -> HardwareStateResponse:
    """Convert hardware state to response."""
    return HardwareStateResponse(
        id=hw.id,
        displayName=hw.display_name,
        connected=hw.connected,
        driverClass=hw.driver_class,
        config=hw.config,
        commands=hw.commands,
        error=hw.error,
    )


def session_to_detail(session: ManualSession) -> ManualSessionDetail:
    """Convert session to detail."""
    return ManualSessionDetail(
        id=session.id,
        sequenceName=session.sequence_name,
        sequenceVersion=session.sequence_version,
        status=session.status.value,
        createdAt=session.created_at.isoformat(),
        startedAt=session.started_at.isoformat() if session.started_at else None,
        completedAt=session.completed_at.isoformat() if session.completed_at else None,
        currentStepIndex=session.current_step_index,
        steps=[step_to_response(s) for s in session.steps],
        hardware=[hw_to_response(h) for h in session.hardware],
        parameters=session.parameters,
        hardwareConfig=session.hardware_config,
        overallPass=session.overall_pass,
        error=session.error,
    )


def cmd_to_response(cmd: CommandResult) -> CommandResultResponse:
    """Convert command result to response."""
    return CommandResultResponse(
        success=cmd.success,
        hardwareId=cmd.hardware_id,
        command=cmd.command,
        result=cmd.result,
        error=cmd.error,
        duration=cmd.duration,
    )


# ============================================================================
# Session Management Endpoints
# ============================================================================


@router.post(
    "/sessions",
    response_model=ApiResponse[ManualSessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Create manual test session",
    description="""
    Create a new manual test session for a sequence.

    The session is created in 'created' state with hardware not yet connected.
    Call /sessions/{id}/initialize to connect hardware and run setup.

    **Warning**: This uses real hardware. Ensure proper configuration before initializing.
    """,
)
async def create_session(
    request: CreateManualSessionRequest,
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualSessionDetail]:
    """Create a new manual test session."""
    try:
        session = await executor.create_session(
            sequence_name=request.sequence_name,
            hardware_config=request.hardware_config,
            parameters=request.parameters,
        )

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Created manual session {session.id}",
        )

    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence not found: {e}",
        )
    except Exception as e:
        logger.exception(f"Failed to create manual session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/sessions",
    response_model=ApiResponse[List[ManualSessionSummary]],
    summary="List manual test sessions",
    description="List all active manual test sessions.",
)
async def list_sessions(
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[List[ManualSessionSummary]]:
    """List all manual test sessions."""
    sessions = executor.list_sessions()
    summaries = [session_to_summary(s) for s in sessions]

    return ApiResponse(
        success=True,
        data=summaries,
        message=f"Found {len(summaries)} sessions",
    )


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[ManualSessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Get manual test session",
    description="Get detailed information about a manual test session.",
)
async def get_session(
    session_id: str = Path(..., description="Session ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualSessionDetail]:
    """Get a manual test session by ID."""
    session = executor.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    return ApiResponse(success=True, data=session_to_detail(session))


@router.delete(
    "/sessions/{session_id}",
    response_model=ApiResponse[bool],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Delete manual test session",
    description="Delete a manual test session and disconnect hardware.",
)
async def delete_session(
    session_id: str = Path(..., description="Session ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[bool]:
    """Delete a manual test session."""
    deleted = await executor.delete_session(session_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    return ApiResponse(
        success=True,
        data=True,
        message=f"Deleted session {session_id}",
    )


# ============================================================================
# Session Lifecycle Endpoints
# ============================================================================


@router.post(
    "/sessions/{session_id}/initialize",
    response_model=ApiResponse[ManualSessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    summary="Initialize manual test session",
    description="""
    Initialize a manual test session.

    This will:
    1. Connect to real hardware using configured drivers
    2. Run the sequence setup() method
    3. Prepare the session for step-by-step execution

    **Warning**: This connects to real hardware. Ensure:
    - Hardware is properly connected
    - Port configurations are correct
    - No other process is using the hardware
    """,
)
async def initialize_session(
    session_id: str = Path(..., description="Session ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualSessionDetail]:
    """Initialize a manual test session."""
    try:
        session = await executor.initialize_session(session_id)

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Session {session_id} initialized with hardware connected",
        )

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except (DriverLoadError, DriverConnectionError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Hardware error: {e}",
        )
    except Exception as e:
        logger.exception(f"Failed to initialize session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/sessions/{session_id}/finalize",
    response_model=ApiResponse[ManualSessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Finalize manual test session",
    description="""
    Finalize a manual test session.

    This will:
    1. Run the sequence teardown() method
    2. Disconnect all hardware
    3. Mark the session as completed
    """,
)
async def finalize_session(
    session_id: str = Path(..., description="Session ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualSessionDetail]:
    """Finalize a manual test session."""
    try:
        session = await executor.finalize_session(session_id)

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Session {session_id} finalized",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Failed to finalize session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/sessions/{session_id}/abort",
    response_model=ApiResponse[ManualSessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Abort manual test session",
    description="""
    Emergency abort a manual test session.

    This will:
    1. Stop any running operations
    2. Run teardown and disconnect hardware
    3. Mark remaining steps as skipped/failed
    """,
)
async def abort_session(
    session_id: str = Path(..., description="Session ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualSessionDetail]:
    """Abort a manual test session."""
    try:
        session = await executor.abort_session(session_id)

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Session {session_id} aborted",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Step Execution Endpoints
# ============================================================================


@router.post(
    "/sessions/{session_id}/steps/{step_name}/run",
    response_model=ApiResponse[ManualStepResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Run a step",
    description="""
    Execute a single step using real hardware.

    The session must be initialized before running steps.
    Parameter overrides can be provided for this step execution.
    """,
)
async def run_step(
    session_id: str = Path(..., description="Session ID"),
    step_name: str = Path(..., description="Step name to run"),
    request: Optional[RunStepRequest] = None,
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualStepResponse]:
    """Run a step in the manual session."""
    try:
        step = await executor.run_step(
            session_id=session_id,
            step_name=step_name,
            parameter_overrides=request.parameter_overrides if request else None,
        )

        status_msg = "passed" if step.status == ManualStepStatus.PASSED else "failed"
        return ApiResponse(
            success=True,
            data=step_to_response(step),
            message=f"Step '{step_name}' {status_msg} in {step.duration:.2f}s",
        )

    except ValueError as e:
        error_str = str(e).lower()
        if "not found" in error_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        if "not ready" in error_str or "not in" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Failed to run step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/sessions/{session_id}/steps/{step_name}/skip",
    response_model=ApiResponse[ManualStepResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Skip a step",
    description="Skip a pending step. Only skippable steps can be skipped.",
)
async def skip_step(
    session_id: str = Path(..., description="Session ID"),
    step_name: str = Path(..., description="Step name to skip"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[ManualStepResponse]:
    """Skip a step in the manual session."""
    try:
        step = await executor.skip_step(session_id, step_name)

        return ApiResponse(
            success=True,
            data=step_to_response(step),
            message=f"Step '{step_name}' skipped",
        )

    except ValueError as e:
        error_str = str(e).lower()
        if "not found" in error_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


# ============================================================================
# Hardware Control Endpoints
# ============================================================================


@router.get(
    "/sessions/{session_id}/hardware",
    response_model=ApiResponse[List[HardwareStateResponse]],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Get connected hardware",
    description="Get the list of hardware devices and their connection status.",
)
async def get_hardware(
    session_id: str = Path(..., description="Session ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[List[HardwareStateResponse]]:
    """Get hardware state for a session."""
    session = executor.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    return ApiResponse(
        success=True,
        data=[hw_to_response(h) for h in session.hardware],
    )


@router.get(
    "/sessions/{session_id}/hardware/{hardware_id}/commands",
    response_model=ApiResponse[List[CommandDefinition]],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Get hardware commands",
    description="Get available commands for a specific hardware device.",
)
async def get_hardware_commands(
    session_id: str = Path(..., description="Session ID"),
    hardware_id: str = Path(..., description="Hardware ID"),
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[List[CommandDefinition]]:
    """Get available commands for hardware."""
    try:
        commands = await executor.get_hardware_commands(session_id, hardware_id)

        return ApiResponse(
            success=True,
            data=[CommandDefinition(**cmd) for cmd in commands],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/sessions/{session_id}/hardware/{hardware_id}/execute",
    response_model=ApiResponse[CommandResultResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Execute hardware command",
    description="""
    Execute a command on a connected hardware device.

    The session must be initialized (hardware connected) before executing commands.
    """,
)
async def execute_hardware_command(
    session_id: str = Path(..., description="Session ID"),
    hardware_id: str = Path(..., description="Hardware ID"),
    request: ExecuteCommandRequest = ...,
    executor: ManualSequenceExecutor = Depends(get_manual_executor),
) -> ApiResponse[CommandResultResponse]:
    """Execute a hardware command."""
    try:
        result = await executor.execute_hardware_command(
            session_id=session_id,
            hardware_id=hardware_id,
            command=request.command,
            parameters=request.parameters,
        )

        return ApiResponse(
            success=result.success,
            data=cmd_to_response(result),
            message=f"Command '{request.command}' executed on {hardware_id}",
        )

    except ValueError as e:
        error_str = str(e).lower()
        if "not found" in error_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        if "not ready" in error_str or "not connected" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Failed to execute command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
