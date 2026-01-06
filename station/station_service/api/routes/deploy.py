"""
Deploy API routes for Station Service.

This module provides endpoints for deploying sequences to batches,
managing deployments, pulling sequences from Backend, and running simulations.
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
from station_service_sdk import SequenceLoader, PackageError
from station_service.services.sequence_sync import (
    SequenceSyncService,
    PullResult,
    SyncResult,
    LocalSequenceInfo,
)
from station_service.services.auto_sync import (
    AutoSyncConfig,
    AutoSyncStatus,
    get_auto_sync_service,
)

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
        from station_service_sdk import collect_steps

        try:
            sequence_class = await sequence_loader.load_sequence_class(manifest, package_path)
            steps_data = collect_steps(sequence_class, manifest)
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
            from station_service_sdk import SequenceSimulator

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


# ============================================================================
# Sync Service Dependency
# ============================================================================

_sync_service: Optional[SequenceSyncService] = None


def get_sync_service(config: StationConfig = Depends(get_config)) -> SequenceSyncService:
    """Get or create sequence sync service."""
    global _sync_service
    if _sync_service is None:
        _sync_service = SequenceSyncService(
            backend_config=config.backend,
            sequences_dir="sequences",
        )
        # Connect TokenManager for dynamic station_api_key
        try:
            from station_service.core.token_manager import get_token_manager
            _sync_service.set_token_manager(get_token_manager())
        except Exception as e:
            logger.warning(f"Could not set TokenManager for sync service: {e}")
    return _sync_service


# ============================================================================
# Pull Response Models
# ============================================================================


class PullRequest(BaseModel):
    """Request for pulling a sequence."""

    force: bool = Field(False, description="Force download even if up-to-date")


class SyncRequest(BaseModel):
    """Request for syncing sequences."""

    sequence_names: Optional[List[str]] = Field(
        None, description="Specific sequences to sync (all if not specified)"
    )


class UpdateCheckResponse(BaseModel):
    """Response for update check."""

    sequence_name: str
    remote_version: str
    local_version: Optional[str]
    needs_update: bool
    installed: bool


class SequenceRegistryItem(BaseModel):
    """Unified sequence registry item combining local and remote info."""

    name: str = Field(..., description="Sequence name")
    display_name: Optional[str] = Field(None, description="Human-readable name")
    description: Optional[str] = Field(None, description="Sequence description")

    # Status
    status: Literal[
        "installed_latest",  # Installed and up-to-date
        "update_available",  # Installed but newer version on server
        "not_installed",     # Available on server, not installed locally
        "local_only",        # Installed locally, not on server
    ] = Field(..., description="Installation status")

    # Version info
    local_version: Optional[str] = Field(None, description="Locally installed version")
    remote_version: Optional[str] = Field(None, description="Version available on server")

    # Metadata
    installed_at: Optional[datetime] = Field(None, description="When installed locally")
    remote_updated_at: Optional[datetime] = Field(None, description="When updated on server")
    is_active: bool = Field(True, description="Whether sequence is active on server")


# ============================================================================
# Pull Endpoints (Backend Sync)
# ============================================================================


@router.post(
    "/pull/{sequence_name}",
    response_model=ApiResponse[PullResult],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    summary="Pull sequence from Backend",
    description="""
    Pull a sequence from the Backend API.

    Downloads the sequence package if:
    - Not installed locally
    - Local version differs from remote
    - Force flag is set

    The sequence will be installed to the sequences directory.
    """,
)
async def pull_sequence_from_backend(
    sequence_name: str,
    request: PullRequest = PullRequest(),
    sync_service: SequenceSyncService = Depends(get_sync_service),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[PullResult]:
    """
    Pull a sequence from Backend.
    """
    try:
        result = await sync_service.pull_sequence(sequence_name, force=request.force)

        if result.error:
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.error,
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error,
            )

        # Clear loader cache if updated
        if result.updated:
            sequence_loader.clear_cache()

        message = (
            f"Updated {sequence_name} to v{result.version}"
            if result.updated
            else f"{sequence_name} is up-to-date (v{result.version})"
        )

        return ApiResponse(success=True, data=result, message=message)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Backend not configured: {e}",
        )
    except Exception as e:
        logger.exception(f"Failed to pull sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull sequence: {str(e)}",
        )


@router.post(
    "/sync",
    response_model=ApiResponse[SyncResult],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Sync all sequences from Backend",
    description="""
    Sync all or specified sequences from the Backend API.

    Downloads and installs any sequences that are:
    - Not installed locally
    - Have newer versions available
    """,
)
async def sync_sequences(
    request: SyncRequest = SyncRequest(),
    sync_service: SequenceSyncService = Depends(get_sync_service),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SyncResult]:
    """
    Sync sequences from Backend.
    """
    try:
        result = await sync_service.sync_all(request.sequence_names)

        # Clear loader cache if any updates
        if result.sequences_updated > 0:
            sequence_loader.clear_cache()

        message = (
            f"Synced {result.sequences_checked} sequences: "
            f"{result.sequences_updated} updated, {result.sequences_failed} failed"
        )

        return ApiResponse(success=True, data=result, message=message)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Backend not configured: {e}",
        )
    except Exception as e:
        logger.exception(f"Sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        )


@router.get(
    "/updates",
    response_model=ApiResponse[List[UpdateCheckResponse]],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Check for sequence updates",
    description="Check which sequences have updates available from Backend.",
)
async def check_updates(
    sync_service: SequenceSyncService = Depends(get_sync_service),
) -> ApiResponse[List[UpdateCheckResponse]]:
    """
    Check for sequence updates.
    """
    try:
        updates = await sync_service.check_updates()

        results = [
            UpdateCheckResponse(
                sequence_name=name,
                remote_version=info["remote_version"],
                local_version=info["local_version"],
                needs_update=info["needs_update"],
                installed=info["installed"],
            )
            for name, info in updates.items()
        ]

        needs_update_count = sum(1 for r in results if r.needs_update)
        message = (
            f"{needs_update_count} updates available"
            if needs_update_count
            else "All sequences up-to-date"
        )

        return ApiResponse(success=True, data=results, message=message)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Backend not configured: {e}",
        )
    except Exception as e:
        logger.exception(f"Failed to check updates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check updates: {str(e)}",
        )


@router.get(
    "/local",
    response_model=ApiResponse[List[LocalSequenceInfo]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="List local sequences",
    description="List all locally installed sequences.",
)
async def list_local_sequences(
    sync_service: SequenceSyncService = Depends(get_sync_service),
) -> ApiResponse[List[LocalSequenceInfo]]:
    """
    List locally installed sequences.
    """
    try:
        sequences = sync_service.list_local_sequences()
        return ApiResponse(
            success=True,
            data=sequences,
            message=f"Found {len(sequences)} installed sequences",
        )

    except Exception as e:
        logger.exception(f"Failed to list local sequences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list local sequences: {str(e)}",
        )


@router.delete(
    "/local/{sequence_name}",
    response_model=ApiResponse[bool],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Delete local sequence",
    description="Delete a locally installed sequence.",
)
async def delete_local_sequence(
    sequence_name: str,
    sync_service: SequenceSyncService = Depends(get_sync_service),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[bool]:
    """
    Delete a locally installed sequence.
    """
    try:
        deleted = sync_service.delete_sequence(sequence_name)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sequence '{sequence_name}' not found locally",
            )

        # Clear loader cache
        sequence_loader.clear_cache()

        return ApiResponse(
            success=True,
            data=True,
            message=f"Deleted sequence '{sequence_name}'",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sequence: {str(e)}",
        )


# ============================================================================
# Registry Endpoint (Unified View)
# ============================================================================


def _is_newer_version(version_a: str, version_b: str) -> bool:
    """
    Check if version_a is newer than version_b using semantic versioning.

    Args:
        version_a: Version to compare (e.g., "1.2.0")
        version_b: Version to compare against (e.g., "1.1.0")

    Returns:
        True if version_a is strictly newer than version_b
    """
    def parse_version(v: str) -> tuple:
        """Parse version string into comparable tuple."""
        parts = v.split(".")
        result = []
        for part in parts:
            try:
                result.append(int(part))
            except ValueError:
                result.append(0)
        # Pad to 3 parts (major, minor, patch)
        while len(result) < 3:
            result.append(0)
        return tuple(result[:3])

    try:
        return parse_version(version_a) > parse_version(version_b)
    except Exception:
        # Fallback to string comparison if parsing fails
        return version_a != version_b


@router.get(
    "/registry",
    response_model=ApiResponse[List[SequenceRegistryItem]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get sequence registry",
    description="""
    Get unified registry of all sequences (local and remote).

    Returns combined view with status indicating:
    - installed_latest: Installed and matches server version
    - update_available: Installed but newer version on server
    - not_installed: Available on server, not installed locally
    - local_only: Installed locally, not available on server
    """,
)
async def get_sequence_registry(
    sync_service: SequenceSyncService = Depends(get_sync_service),
) -> ApiResponse[List[SequenceRegistryItem]]:
    """
    Get unified sequence registry.
    """
    try:
        registry: List[SequenceRegistryItem] = []

        # Get local sequences
        local_sequences = {s.name: s for s in sync_service.list_local_sequences()}

        # Try to get remote sequences
        remote_sequences = {}
        backend_available = True
        backend_error: Optional[str] = None
        try:
            available = await sync_service.list_available_sequences()
            remote_sequences = {s.name: s for s in available}
        except Exception as e:
            logger.warning(f"Could not fetch remote sequences: {e}")
            backend_available = False
            # Extract meaningful error message
            error_str = str(e)
            if "401" in error_str or "invalid" in error_str.lower() or "expired" in error_str.lower():
                backend_error = "API 키가 만료되었거나 유효하지 않습니다. 다시 로그인해주세요."
            elif "connection" in error_str.lower() or "connect" in error_str.lower():
                backend_error = "백엔드 서버에 연결할 수 없습니다. 서버 상태를 확인해주세요."
            elif "timeout" in error_str.lower():
                backend_error = "백엔드 서버 응답 시간이 초과되었습니다."
            else:
                backend_error = f"백엔드 연결 실패: {error_str}"

        # Process remote sequences
        for name, remote in remote_sequences.items():
            local = local_sequences.pop(name, None)

            if local:
                # Installed - check if update available using semantic version comparison
                if _is_newer_version(remote.version, local.version):
                    status_val = "update_available"
                else:
                    status_val = "installed_latest"

                registry.append(SequenceRegistryItem(
                    name=name,
                    display_name=remote.display_name or name,
                    description=remote.description,
                    status=status_val,
                    local_version=local.version,
                    remote_version=remote.version,
                    installed_at=local.installed_at,
                    is_active=remote.is_active,
                ))
            else:
                # Not installed
                registry.append(SequenceRegistryItem(
                    name=name,
                    display_name=remote.display_name or name,
                    description=remote.description,
                    status="not_installed",
                    local_version=None,
                    remote_version=remote.version,
                    is_active=remote.is_active,
                ))

        # Process remaining local-only sequences
        for name, local in local_sequences.items():
            registry.append(SequenceRegistryItem(
                name=name,
                display_name=name,
                description=None,
                status="local_only",
                local_version=local.version,
                remote_version=None,
                installed_at=local.installed_at,
                is_active=True,
            ))

        # Sort: updates first, then installed, then not installed
        status_order = {
            "update_available": 0,
            "installed_latest": 1,
            "local_only": 2,
            "not_installed": 3,
        }
        registry.sort(key=lambda x: (status_order.get(x.status, 99), x.name))

        # Build message
        installed_count = sum(1 for r in registry if r.status in ("installed_latest", "update_available", "local_only"))
        update_count = sum(1 for r in registry if r.status == "update_available")

        if not backend_available:
            message = f"{installed_count} local sequences (backend unavailable)"
        elif update_count > 0:
            message = f"{len(registry)} sequences, {update_count} updates available"
        else:
            message = f"{len(registry)} sequences, all up-to-date"

        # Include warnings if backend failed
        warnings = [backend_error] if backend_error else None

        return ApiResponse(success=True, data=registry, message=message, warnings=warnings)

    except Exception as e:
        logger.exception(f"Failed to get registry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get registry: {str(e)}",
        )


# ============================================================================
# Auto-Sync Endpoints
# ============================================================================


@router.get(
    "/auto-sync/status",
    response_model=ApiResponse[AutoSyncStatus],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get auto-sync status",
    description="Get the current status of the auto-sync service.",
)
async def get_auto_sync_status() -> ApiResponse[AutoSyncStatus]:
    """
    Get auto-sync status.
    """
    auto_sync = get_auto_sync_service()
    if auto_sync is None:
        return ApiResponse(
            success=True,
            data=AutoSyncStatus(
                enabled=False,
                running=False,
                poll_interval=60,
                auto_pull=True,
            ),
            message="Auto-sync service not initialized",
        )

    return ApiResponse(success=True, data=auto_sync.status)


@router.post(
    "/auto-sync/configure",
    response_model=ApiResponse[AutoSyncStatus],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Configure auto-sync",
    description="""
    Configure the auto-sync service.

    Settings:
    - enabled: Enable/disable auto-sync
    - poll_interval: Interval between checks (10-3600 seconds)
    - auto_pull: Automatically pull when updates are detected
    """,
)
async def configure_auto_sync(
    config: AutoSyncConfig,
) -> ApiResponse[AutoSyncStatus]:
    """
    Configure auto-sync service.
    """
    auto_sync = get_auto_sync_service()
    if auto_sync is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auto-sync service not initialized",
        )

    auto_sync.configure(config)

    message = "Auto-sync enabled" if config.enabled else "Auto-sync disabled"
    return ApiResponse(success=True, data=auto_sync.status, message=message)


@router.post(
    "/auto-sync/check",
    response_model=ApiResponse[AutoSyncStatus],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Trigger update check",
    description="Manually trigger an update check without syncing.",
)
async def trigger_auto_sync_check() -> ApiResponse[AutoSyncStatus]:
    """
    Manually trigger update check.
    """
    auto_sync = get_auto_sync_service()
    if auto_sync is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auto-sync service not initialized",
        )

    try:
        status_result = await auto_sync.check_now()
        message = (
            f"{status_result.updates_available} updates available"
            if status_result.updates_available > 0
            else "All sequences up-to-date"
        )
        return ApiResponse(success=True, data=status_result, message=message)
    except Exception as e:
        logger.exception(f"Check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check failed: {str(e)}",
        )


@router.post(
    "/auto-sync/sync-now",
    response_model=ApiResponse[SyncResult],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Trigger immediate sync",
    description="Manually trigger an immediate sync of all updates.",
)
async def trigger_auto_sync_now(
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SyncResult]:
    """
    Manually trigger immediate sync.
    """
    auto_sync = get_auto_sync_service()
    if auto_sync is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auto-sync service not initialized",
        )

    try:
        result = await auto_sync.sync_now()

        # Clear loader cache if any updates
        if result.sequences_updated > 0:
            sequence_loader.clear_cache()

        message = (
            f"Synced {result.sequences_updated} sequences"
            if result.sequences_updated > 0
            else "No updates to sync"
        )
        return ApiResponse(success=True, data=result, message=message)
    except Exception as e:
        logger.exception(f"Sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}",
        )
