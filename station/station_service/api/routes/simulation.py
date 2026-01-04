"""
Interactive Simulation API Routes for Station Service.

This module provides endpoints for interactive step-by-step sequence simulation,
allowing UI-driven testing without actual hardware.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field

from station_service.api.dependencies import get_sequence_loader
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service_sdk import (
    SequenceLoader,
    InteractiveSimulator,
    SimulationSession,
    SimulationSessionStatus,
    StepState,
    StepExecutionStatus,
    PackageError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simulation", tags=["Interactive Simulation"])


# ============================================================================
# Simulator Singleton
# ============================================================================

_simulator: Optional[InteractiveSimulator] = None


def get_simulator(
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> InteractiveSimulator:
    """Get or create the interactive simulator singleton."""
    global _simulator
    if _simulator is None:
        _simulator = InteractiveSimulator(sequence_loader)
    return _simulator


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateSessionRequest(BaseModel):
    """Request to create a simulation session."""

    sequence_name: str = Field(..., description="Name of the sequence to simulate")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameter overrides"
    )
    hardware_config: Optional[Dict[str, Any]] = Field(
        None, description="Hardware configuration"
    )


class RunStepRequest(BaseModel):
    """Request to run a step."""

    parameter_overrides: Optional[Dict[str, Any]] = Field(
        None, description="Parameter overrides for this step"
    )


class SessionSummary(BaseModel):
    """Summary of a simulation session."""

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
    overall_pass: bool = Field(..., alias="overallPass")

    model_config = {"populate_by_name": True}


class SessionDetail(BaseModel):
    """Detailed session information."""

    id: str
    sequence_name: str = Field(..., alias="sequenceName")
    sequence_version: str = Field(..., alias="sequenceVersion")
    status: str
    created_at: str = Field(..., alias="createdAt")
    started_at: Optional[str] = Field(None, alias="startedAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")
    current_step_index: int = Field(..., alias="currentStepIndex")
    steps: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    overall_pass: bool = Field(..., alias="overallPass")
    error: Optional[str] = None

    model_config = {"populate_by_name": True}


class StepResultResponse(BaseModel):
    """Response for step execution."""

    name: str
    display_name: str = Field(..., alias="displayName")
    order: int
    status: str
    started_at: Optional[str] = Field(None, alias="startedAt")
    completed_at: Optional[str] = Field(None, alias="completedAt")
    duration: float
    result: Optional[Dict[str, Any]] = None
    measurements: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    model_config = {"populate_by_name": True}


# ============================================================================
# Helper Functions
# ============================================================================


def session_to_summary(session: SimulationSession) -> SessionSummary:
    """Convert session to summary."""
    passed = sum(1 for s in session.steps if s.status == StepExecutionStatus.PASSED)
    failed = sum(1 for s in session.steps if s.status == StepExecutionStatus.FAILED)

    return SessionSummary(
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
        overallPass=session.overall_pass,
    )


def session_to_detail(session: SimulationSession) -> SessionDetail:
    """Convert session to detail."""
    return SessionDetail(
        id=session.id,
        sequenceName=session.sequence_name,
        sequenceVersion=session.sequence_version,
        status=session.status.value,
        createdAt=session.created_at.isoformat(),
        startedAt=session.started_at.isoformat() if session.started_at else None,
        completedAt=session.completed_at.isoformat() if session.completed_at else None,
        currentStepIndex=session.current_step_index,
        steps=[s.to_dict() for s in session.steps],
        parameters=session.parameters,
        overallPass=session.overall_pass,
        error=session.error,
    )


def step_to_response(step: StepState) -> StepResultResponse:
    """Convert step state to response."""
    return StepResultResponse(
        name=step.name,
        displayName=step.display_name,
        order=step.order,
        status=step.status.value,
        startedAt=step.started_at.isoformat() if step.started_at else None,
        completedAt=step.completed_at.isoformat() if step.completed_at else None,
        duration=step.duration,
        result=step.result,
        measurements=step.measurements,
        error=step.error,
    )


# ============================================================================
# Session Management Endpoints
# ============================================================================


@router.post(
    "/sessions",
    response_model=ApiResponse[SessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Create simulation session",
    description="""
    Create a new interactive simulation session for a sequence.

    The session is created in 'created' state. Call /sessions/{id}/initialize
    to run the sequence setup and prepare for step execution.
    """,
)
async def create_session(
    request: CreateSessionRequest,
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[SessionDetail]:
    """Create a new simulation session."""
    try:
        session = await simulator.create_session(
            sequence_name=request.sequence_name,
            parameters=request.parameters,
            hardware_config=request.hardware_config,
        )

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Created simulation session {session.id}",
        )

    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence not found: {e}",
        )
    except Exception as e:
        logger.exception(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/sessions",
    response_model=ApiResponse[List[SessionSummary]],
    summary="List simulation sessions",
    description="List all active simulation sessions.",
)
async def list_sessions(
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[List[SessionSummary]]:
    """List all simulation sessions."""
    sessions = simulator.list_sessions()
    summaries = [session_to_summary(s) for s in sessions]

    return ApiResponse(
        success=True,
        data=summaries,
        message=f"Found {len(summaries)} sessions",
    )


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[SessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Get simulation session",
    description="Get detailed information about a simulation session.",
)
async def get_session(
    session_id: str = Path(..., description="Session ID"),
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[SessionDetail]:
    """Get a simulation session by ID."""
    session = simulator.get_session(session_id)

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
    summary="Delete simulation session",
    description="Delete a simulation session and clean up resources.",
)
async def delete_session(
    session_id: str = Path(..., description="Session ID"),
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[bool]:
    """Delete a simulation session."""
    deleted = await simulator.delete_session(session_id)

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
    response_model=ApiResponse[SessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Initialize simulation session",
    description="""
    Initialize a simulation session by running the sequence setup.

    This creates mock hardware, runs setup(), and prepares the session
    for step-by-step execution.
    """,
)
async def initialize_session(
    session_id: str = Path(..., description="Session ID"),
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[SessionDetail]:
    """Initialize a simulation session."""
    try:
        session = await simulator.initialize_session(session_id)

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Session {session_id} initialized",
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
    except Exception as e:
        logger.exception(f"Failed to initialize session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/sessions/{session_id}/finalize",
    response_model=ApiResponse[SessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Finalize simulation session",
    description="""
    Finalize a simulation session by running the sequence teardown.

    This cleans up mock hardware and marks the session as completed.
    """,
)
async def finalize_session(
    session_id: str = Path(..., description="Session ID"),
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[SessionDetail]:
    """Finalize a simulation session."""
    try:
        session = await simulator.finalize_session(session_id)

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
    response_model=ApiResponse[SessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
    summary="Abort simulation session",
    description="Abort a simulation session, skipping remaining steps.",
)
async def abort_session(
    session_id: str = Path(..., description="Session ID"),
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[SessionDetail]:
    """Abort a simulation session."""
    try:
        session = await simulator.abort_session(session_id)

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
    response_model=ApiResponse[StepResultResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Run a simulation step",
    description="""
    Execute a single step in the simulation.

    The session must be initialized before running steps.
    Parameter overrides can be provided for this step execution.
    """,
)
async def run_step(
    session_id: str = Path(..., description="Session ID"),
    step_name: str = Path(..., description="Step name to run"),
    request: Optional[RunStepRequest] = None,
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[StepResultResponse]:
    """Run a simulation step."""
    try:
        step = await simulator.run_step(
            session_id=session_id,
            step_name=step_name,
            parameter_overrides=request.parameter_overrides if request else None,
        )

        status_msg = "passed" if step.status == StepExecutionStatus.PASSED else "failed"
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
    response_model=ApiResponse[StepResultResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
    summary="Skip a simulation step",
    description="Skip a pending step in the simulation.",
)
async def skip_step(
    session_id: str = Path(..., description="Session ID"),
    step_name: str = Path(..., description="Step name to skip"),
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[StepResultResponse]:
    """Skip a simulation step."""
    try:
        step = await simulator.skip_step(session_id, step_name)

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
# Quick Simulation Endpoint (All-in-one)
# ============================================================================


@router.post(
    "/quick/{sequence_name}",
    response_model=ApiResponse[SessionDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Quick simulation",
    description="""
    Run a complete simulation in one call.

    Creates a session, initializes, runs all steps, and finalizes.
    Returns the final session state with all step results.
    """,
)
async def quick_simulation(
    sequence_name: str = Path(..., description="Sequence name"),
    request: Optional[CreateSessionRequest] = None,
    simulator: InteractiveSimulator = Depends(get_simulator),
) -> ApiResponse[SessionDetail]:
    """Run a complete simulation."""
    try:
        # Create session
        session = await simulator.create_session(
            sequence_name=sequence_name,
            parameters=request.parameters if request else None,
            hardware_config=request.hardware_config if request else None,
        )

        # Initialize
        await simulator.initialize_session(session.id)

        # Run all steps
        for step in session.steps:
            if step.status == StepExecutionStatus.PENDING:
                await simulator.run_step(session.id, step.name)

        # Finalize
        session = await simulator.finalize_session(session.id)

        return ApiResponse(
            success=True,
            data=session_to_detail(session),
            message=f"Simulation completed: {'PASS' if session.overall_pass else 'FAIL'}",
        )

    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence not found: {e}",
        )
    except Exception as e:
        logger.exception(f"Quick simulation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
