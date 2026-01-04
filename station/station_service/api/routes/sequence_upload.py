"""
Sequence Package API routes for Station Service.

This module provides endpoints for managing local sequence packages:
- Download packages as ZIP
- Delete packages

Note: Upload functionality has been moved to Backend.
Use /api/deploy/pull/{name} to install sequences from Backend.
"""

import io
import logging
import shutil
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from station_service.api.dependencies import get_sequence_loader
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service_sdk import SequenceLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sequences", tags=["Sequence Packages"])


class SequenceDeleteResponse(BaseModel):
    """Response for sequence deletion."""

    name: str = Field(..., description="Deleted sequence name")
    deleted: bool = Field(..., description="Whether deletion was successful")
    path: str = Field(..., description="Deleted package path")


# ============================================================================
# Endpoints
# ============================================================================


@router.delete(
    "/{sequence_name}",
    response_model=ApiResponse[SequenceDeleteResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Delete sequence package",
    description="Delete a sequence package from the filesystem.",
)
async def delete_sequence(
    sequence_name: str,
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SequenceDeleteResponse]:
    """
    Delete a sequence package.
    """
    try:
        package_path = sequence_loader.get_package_path(sequence_name)

        if not package_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sequence package '{sequence_name}' not found",
            )

        # Remove from cache
        sequence_loader.clear_cache()

        # Delete the directory
        shutil.rmtree(package_path)
        logger.info(f"Deleted sequence package: {sequence_name}")

        return ApiResponse(
            success=True,
            data=SequenceDeleteResponse(
                name=sequence_name,
                deleted=True,
                path=str(package_path),
            ),
            message=f"Package '{sequence_name}' deleted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sequence: {str(e)}",
        )


@router.get(
    "/{sequence_name}/download",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/zip": {}},
            "description": "ZIP file of the sequence package",
        },
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Download sequence package",
    description="Download a sequence package as a ZIP file.",
)
async def download_sequence(
    sequence_name: str,
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> Response:
    """
    Download a sequence package as a ZIP file.
    """
    try:
        package_path = sequence_loader.get_package_path(sequence_name)

        if not package_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sequence package '{sequence_name}' not found",
            )

        # Create ZIP in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in package_path.rglob("*"):
                if file_path.is_file():
                    # Skip __pycache__ and .pyc files
                    if "__pycache__" in str(file_path) or file_path.suffix == ".pyc":
                        continue
                    arcname = f"{sequence_name}/{file_path.relative_to(package_path)}"
                    zf.write(file_path, arcname)

        zip_buffer.seek(0)

        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{sequence_name}.zip"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to download sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download sequence: {str(e)}",
        )
