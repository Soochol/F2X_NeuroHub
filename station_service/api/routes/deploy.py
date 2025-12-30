"""
Deploy API routes for Station Service.

This module provides endpoints for deploying sequences to batches,
managing deployments, and running simulations.
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from station_service.api.dependencies import get_config, get_sequence_loader
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.core.config_writer import (
    update_batch_sequence,
    get_deployed_sequence,
    list_batches_with_sequences,
)
from station_service.models.config import StationConfig
from station_service.sequence.loader import SequenceLoader
from station_service.sequence.exceptions import PackageError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/deploy", tags=["Deploy"])


# ============================================================================
# Response Models
# ============================================================================


class DeployResponse(BaseModel):
    """Response for sequence deployment."""

    sequence_name: str = Field(..., description="Name of deployed sequence")
    batch_id: str = Field(..., description="ID of the batch")
    deployed_at: datetime = Field(..., description="Deployment timestamp")
    previous_sequence: Optional[str] = Field(None, description="Previously deployed sequence")


class DeployedSequenceInfo(BaseModel):
    """Information about a deployed sequence."""

    batch_id: str = Field(..., description="Batch ID")
    batch_name: str = Field(..., description="Batch name")
    sequence_name: Optional[str] = Field(None, description="Deployed sequence name")
    sequence_path: Optional[str] = Field(None, description="Deployed sequence path")


class BatchDeploymentInfo(BaseModel):
    """Deployment information for a batch."""

    batch_id: str = Field(..., description="Batch ID")
    name: str = Field(..., description="Batch name")
    sequence_package: Optional[str] = Field(None, description="Deployed sequence package")


class StepPreview(BaseModel):
    """Preview of a sequence step."""

    order: int = Field(..., description="Step execution order")
    name: str = Field(..., description="Step name")
    display_name: str = Field(..., description="Human-readable step name")
    timeout: int = Field(60, description="Step timeout in seconds")
    retry: int = Field(0, description="Number of retry attempts")
    cleanup: bool = Field(False, description="Whether this is a cleanup step")
    description: Optional[str] = Field(None, description="Step description")


class SimulationRequest(BaseModel):
    """Request for running a simulation."""

    mode: Literal["dry_run", "preview"] = Field("preview", description="Simulation mode")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter overrides")


class SimulationResult(BaseModel):
    """Result of a simulation run."""

    id: str = Field(..., description="Simulation ID")
    sequence_name: str = Field(..., description="Simulated sequence name")
    mode: str = Field(..., description="Simulation mode")
    status: str = Field(..., description="Simulation status")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    steps: List[StepPreview] = Field(default_factory=list, description="Step previews")
    step_results: Optional[List[Dict[str, Any]]] = Field(None, description="Step execution results")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters used")
    error: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# Deploy Endpoints
# ============================================================================


@router.post(
    "/{sequence_name}",
    response_model=ApiResponse[DeployResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Deploy sequence to batch",
    description="""
    Deploy a sequence package to a specific batch.

    This updates the station.yaml configuration to use the specified sequence
    for the given batch. The change is persistent across restarts.
    """,
)
async def deploy_sequence(
    sequence_name: str,
    batch_id: str = Query(..., description="ID of the batch to deploy to"),
    config: StationConfig = Depends(get_config),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[DeployResponse]:
    """
    Deploy a sequence to a batch.
    """
    try:
        # Verify sequence exists
        package_path = sequence_loader.get_package_path(sequence_name)
        if not package_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sequence '{sequence_name}' not found",
            )

        # Load manifest to validate
        await sequence_loader.load_package(sequence_name)

        # Get config file path
        config_path = Path(os.environ.get("STATION_CONFIG", "config/station.yaml"))

        # Get previous sequence
        previous_sequence = await get_deployed_sequence(config_path, batch_id)

        # Update the config file
        sequence_path = f"sequences/{sequence_name}"
        try:
            await update_batch_sequence(config_path, batch_id, sequence_path)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

        logger.info(f"Deployed sequence '{sequence_name}' to batch '{batch_id}'")

        return ApiResponse(
            success=True,
            data=DeployResponse(
                sequence_name=sequence_name,
                batch_id=batch_id,
                deployed_at=datetime.now(),
                previous_sequence=previous_sequence,
            ),
            message=f"Sequence '{sequence_name}' deployed to batch '{batch_id}'",
        )

    except HTTPException:
        raise
    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Failed to deploy sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy sequence: {str(e)}",
        )


@router.get(
    "",
    response_model=ApiResponse[List[BatchDeploymentInfo]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="List all deployments",
    description="Get deployment information for all batches.",
)
async def list_deployments() -> ApiResponse[List[BatchDeploymentInfo]]:
    """
    List all batch deployments.
    """
    try:
        config_path = Path(os.environ.get("STATION_CONFIG", "config/station.yaml"))
        batches = await list_batches_with_sequences(config_path)

        deployments = [
            BatchDeploymentInfo(
                batch_id=b["batch_id"],
                name=b["name"],
                sequence_package=b["sequence_package"],
            )
            for b in batches
        ]

        return ApiResponse(success=True, data=deployments)

    except Exception as e:
        logger.exception(f"Failed to list deployments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deployments: {str(e)}",
        )


@router.get(
    "/batch/{batch_id}",
    response_model=ApiResponse[DeployedSequenceInfo],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get deployed sequence for batch",
    description="Get the currently deployed sequence for a specific batch.",
)
async def get_batch_deployment(
    batch_id: str,
    config: StationConfig = Depends(get_config),
) -> ApiResponse[DeployedSequenceInfo]:
    """
    Get the deployed sequence for a batch.
    """
    try:
        # Find the batch
        batch_config = None
        for batch in config.batches:
            if batch.id == batch_id:
                batch_config = batch
                break

        if batch_config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch '{batch_id}' not found",
            )

        # Extract sequence name from path
        sequence_path = batch_config.sequence_package
        sequence_name = None
        if sequence_path:
            # Extract name from path like "sequences/pcb_voltage_test"
            sequence_name = Path(sequence_path).name

        return ApiResponse(
            success=True,
            data=DeployedSequenceInfo(
                batch_id=batch_id,
                batch_name=batch_config.name,
                sequence_name=sequence_name,
                sequence_path=sequence_path,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment: {str(e)}",
        )


# ============================================================================
# Simulation Endpoints
# ============================================================================


@router.post(
    "/simulate/{sequence_name}",
    response_model=ApiResponse[SimulationResult],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Run simulation",
    description="""
    Run a simulation of a sequence.

    Modes:
    - preview: Returns step information without execution
    - dry_run: Executes sequence with mock hardware
    """,
)
async def run_simulation(
    sequence_name: str,
    request: SimulationRequest,
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SimulationResult]:
    """
    Run a simulation of a sequence.
    """
    try:
        # Load the manifest
        manifest = await sequence_loader.load_package(sequence_name)
        package_path = sequence_loader.get_package_path(sequence_name)

        simulation_id = str(uuid.uuid4())[:8]
        started_at = datetime.now()

        # Load sequence class to get steps
        from station_service.sequence.decorators import collect_steps

        try:
            sequence_class = await sequence_loader.load_sequence_class(manifest, package_path)
            steps_data = collect_steps(sequence_class)
        except Exception as e:
            logger.warning(f"Failed to load sequence class: {e}")
            steps_data = []

        # Build step previews
        step_previews = []
        for method_name, method, step_meta in steps_data:
            step_previews.append(StepPreview(
                order=step_meta.order,
                name=step_meta.name or method_name,
                display_name=(step_meta.name or method_name).replace("_", " ").title(),
                timeout=int(step_meta.timeout),
                retry=step_meta.retry,
                cleanup=step_meta.cleanup,
                description=step_meta.description,
            ))

        if request.mode == "preview":
            # Preview mode - just return step information
            return ApiResponse(
                success=True,
                data=SimulationResult(
                    id=simulation_id,
                    sequence_name=sequence_name,
                    mode="preview",
                    status="completed",
                    started_at=started_at,
                    completed_at=datetime.now(),
                    steps=step_previews,
                    parameters=request.parameters,
                ),
            )
        else:
            # Dry run mode - execute with mock hardware
            from station_service.sequence.simulator import SequenceSimulator

            simulator = SequenceSimulator(sequence_loader)
            result = await simulator.dry_run(
                sequence_name=sequence_name,
                parameters=request.parameters or {},
            )

            return ApiResponse(
                success=True,
                data=SimulationResult(
                    id=simulation_id,
                    sequence_name=sequence_name,
                    mode="dry_run",
                    status=result.get("status", "completed"),
                    started_at=started_at,
                    completed_at=datetime.now(),
                    steps=step_previews,
                    step_results=result.get("steps"),
                    parameters=request.parameters,
                    error=result.get("error"),
                ),
            )

    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence '{sequence_name}' not found: {e}",
        )
    except Exception as e:
        logger.exception(f"Simulation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}",
        )
