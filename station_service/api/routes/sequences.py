"""
Sequence API routes for Station Service.

This module provides endpoints for sequence package management,
including listing, retrieving details, and updating sequences.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path as PathParam, status

from station_service.api.dependencies import get_config, get_sequence_loader
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.schemas.sequence import (
    HardwareConfigSchema,
    HardwareDefinition,
    ParameterDefinition,
    SequenceDetail,
    SequenceSummary,
    SequenceUpdateRequest,
    SequenceUpdateResponse,
    StepDefinition,
)
from station_service.core.exceptions import SequenceNotFoundError
from station_service.models.config import StationConfig
from station_service.sequence.loader import SequenceLoader
from station_service.sequence.decorators import collect_steps
from station_service.sequence.exceptions import PackageError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sequences", tags=["Sequences"])


@router.get(
    "",
    response_model=ApiResponse[List[SequenceSummary]],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="List all sequences",
    description="""
    Retrieve a list of all available sequence packages.

    Returns summary information for each sequence including:
    - Sequence name and version
    - Display name and description
    - Package path
    - Last update timestamp
    """,
)
async def list_sequences(
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[List[SequenceSummary]]:
    """
    List all available sequence packages.

    Scans the configured sequences directory and returns metadata
    for all valid sequence packages found.
    """
    try:
        # Discover all packages from filesystem
        package_names = await sequence_loader.discover_packages()
        summaries = []

        for package_name in package_names:
            try:
                # Load the manifest for each package
                manifest = await sequence_loader.load_package(package_name)
                package_path = sequence_loader.get_package_path(package_name)

                # Get file modification time
                if package_path.exists():
                    stat = package_path.stat()
                    updated_at = datetime.fromtimestamp(stat.st_mtime)
                else:
                    updated_at = datetime.now()

                # Use manifest updated_at if available
                if manifest.updated_at:
                    updated_at = manifest.updated_at

                summaries.append(SequenceSummary(
                    name=manifest.name,
                    version=manifest.version,
                    display_name=manifest.name.replace("_", " ").title(),
                    description=manifest.description or None,
                    path=str(package_path),
                    updated_at=updated_at,
                ))
            except Exception as e:
                logger.warning(f"Failed to load package {package_name}: {e}")
                continue

        return ApiResponse(success=True, data=summaries)

    except Exception as e:
        logger.exception(f"Error listing sequences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{sequence_name}",
    response_model=ApiResponse[SequenceDetail],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get sequence details",
    description="""
    Retrieve detailed information for a specific sequence package.

    Returns comprehensive sequence information including:
    - Basic metadata (name, version, author, dates)
    - Hardware definitions with configuration schemas
    - Parameter definitions with types, defaults, and constraints
    - Step definitions with execution order, timeouts, and conditions
    """,
)
async def get_sequence(
    sequence_name: str = PathParam(..., description="Sequence package name"),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SequenceDetail]:
    """
    Get detailed information for a specific sequence package.
    """
    try:
        # Load the manifest
        manifest = await sequence_loader.load_package(sequence_name)
        package_path = sequence_loader.get_package_path(sequence_name)

        # Get file modification time
        if package_path.exists():
            stat = package_path.stat()
            updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        else:
            updated_at = datetime.now().isoformat()

        # Use manifest updated_at if available
        if manifest.updated_at:
            updated_at = manifest.updated_at.isoformat()

        created_at = None
        if manifest.created_at:
            created_at = manifest.created_at.isoformat()

        # Convert hardware definitions
        hardware_list: List[HardwareDefinition] = []
        for hw_id, hw_def in manifest.hardware.items():
            config_schema = {}
            if hw_def.config_schema:
                for field_name, field_def in hw_def.config_schema.items():
                    config_schema[field_name] = HardwareConfigSchema(
                        type=field_def.type.value,
                        required=field_def.required,
                        default=field_def.default,
                    )

            hardware_list.append(HardwareDefinition(
                id=hw_id,
                display_name=hw_def.display_name,
                driver=hw_def.driver,
                config_schema=config_schema,
            ))

        # Convert parameter definitions
        parameters_list: List[ParameterDefinition] = []
        for param_name, param_def in manifest.parameters.items():
            parameters_list.append(ParameterDefinition(
                name=param_name,
                display_name=param_def.display_name,
                type=param_def.type.value,
                default=param_def.default,
                min=param_def.min,
                max=param_def.max,
                unit=param_def.unit or None,
                options=[str(o) for o in param_def.options] if param_def.options else None,
            ))

        # Try to load sequence class to extract step information
        steps_list: List[StepDefinition] = []
        try:
            sequence_class = await sequence_loader.load_sequence_class(manifest, package_path)
            steps = collect_steps(sequence_class)

            for method_name, method, step_meta in steps:
                steps_list.append(StepDefinition(
                    order=step_meta.order,
                    name=step_meta.name or method_name,
                    display_name=(step_meta.name or method_name).replace("_", " ").title(),
                    description=step_meta.description,
                    timeout=int(step_meta.timeout),
                    retry=step_meta.retry,
                    cleanup=step_meta.cleanup,
                    condition=step_meta.condition,
                ))
        except Exception as e:
            logger.warning(f"Failed to load sequence class for {sequence_name}: {e}")
            # Steps will be empty if we can't load the class

        detail = SequenceDetail(
            name=manifest.name,
            version=manifest.version,
            display_name=manifest.name.replace("_", " ").title(),
            description=manifest.description or None,
            author=manifest.author or None,
            created_at=created_at,
            updated_at=updated_at,
            hardware=hardware_list,
            parameters=parameters_list,
            steps=steps_list,
        )

        return ApiResponse(success=True, data=detail)

    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence '{sequence_name}' not found: {e}",
        )
    except Exception as e:
        logger.exception(f"Error getting sequence {sequence_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/{sequence_name}",
    response_model=ApiResponse[SequenceUpdateResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Update sequence",
    description="""
    Update a sequence package configuration.

    Allows modification of:
    - Parameter default values
    - Step execution order
    - Step timeout values

    The sequence version will be automatically incremented after update.

    Note: This does not modify the step implementation code, only the configuration.
    """,
)
async def update_sequence(
    request: SequenceUpdateRequest,
    sequence_name: str = PathParam(..., description="Sequence package name"),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SequenceUpdateResponse]:
    """
    Update a sequence package configuration.
    """
    try:
        # Verify package exists
        package_path = sequence_loader.get_package_path(sequence_name)
        if not package_path.exists():
            raise PackageError(f"Package not found: {sequence_name}")

        # Convert request to dictionaries for loader
        parameter_updates = [
            {"name": p.name, "default": p.default}
            for p in request.parameters
        ] if request.parameters else None

        step_updates = [
            {"name": s.name, "order": s.order, "timeout": s.timeout}
            for s in request.steps
        ] if request.steps else None

        # Update the manifest using the sequence loader
        updated_manifest = await sequence_loader.update_manifest(
            package_name=sequence_name,
            parameter_updates=parameter_updates,
            step_updates=step_updates,
        )

        return ApiResponse(
            success=True,
            data=SequenceUpdateResponse(
                name=sequence_name,
                version=updated_manifest.version,
                updated_at=datetime.now(),
            ),
        )

    except PackageError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error updating sequence {sequence_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
