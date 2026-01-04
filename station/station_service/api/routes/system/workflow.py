"""
Workflow configuration routes.

Provides endpoints for:
- Get workflow configuration (/workflow)
- Update workflow configuration (/workflow)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from station_service.api.dependencies import get_config, get_config_path
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.routes.system.schemas import (
    WorkflowConfigResponse,
    UpdateWorkflowRequest,
)
from station_service.models.config import StationConfig, WorkflowConfig

logger = logging.getLogger(__name__)

router = APIRouter()


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
    """Get workflow configuration."""
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
    """Update workflow configuration."""
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
