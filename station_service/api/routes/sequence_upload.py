"""
Sequence Upload API routes for Station Service.

This module provides endpoints for uploading, validating, and managing
sequence packages as ZIP files.
"""

import asyncio
import io
import logging
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field, ValidationError

from station_service.api.dependencies import get_config, get_sequence_loader
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.models.config import StationConfig
from station_service.sdk import (
    SequenceLoader,
    SequenceManifest,
    ManifestError,
    PackageError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sequences", tags=["Sequence Upload"])


class DependencyInstallResult(BaseModel):
    """Result of a single dependency installation."""

    package: str = Field(..., description="Package specification (e.g., 'pyserial>=3.5')")
    success: bool = Field(..., description="Whether installation was successful")
    message: str = Field(default="", description="Installation message or error")
    already_installed: bool = Field(default=False, description="Package was already installed")


class DependenciesResult(BaseModel):
    """Result of all dependency installations."""

    total: int = Field(default=0, description="Total number of dependencies")
    installed: int = Field(default=0, description="Number of newly installed")
    skipped: int = Field(default=0, description="Number already installed (skipped)")
    failed: int = Field(default=0, description="Number that failed to install")
    details: List[DependencyInstallResult] = Field(default_factory=list, description="Per-package results")


class SequenceUploadResponse(BaseModel):
    """Response for successful sequence upload."""

    name: str = Field(..., description="Sequence package name")
    version: str = Field(..., description="Sequence version")
    path: str = Field(..., description="Installed package path")
    hardware: List[str] = Field(default_factory=list, description="Hardware definitions")
    parameters: List[str] = Field(default_factory=list, description="Parameter names")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    dependencies: Optional[DependenciesResult] = Field(None, description="Dependency installation results")


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""

    field: str = Field(..., description="Field that caused the error")
    message: str = Field(..., description="Error message")


class ManifestInfo(BaseModel):
    """Manifest information from validation."""

    name: str = Field(..., description="Sequence name")
    version: str = Field(..., description="Sequence version")
    displayName: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Sequence description")


class SequenceValidationResult(BaseModel):
    """Result of sequence package validation."""

    valid: bool = Field(..., description="Whether the package is valid")
    errors: List[ValidationErrorDetail] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    manifest: Optional[ManifestInfo] = Field(None, description="Manifest info if valid")


class SequenceDeleteResponse(BaseModel):
    """Response for sequence deletion."""

    name: str = Field(..., description="Deleted sequence name")
    deleted: bool = Field(..., description="Whether deletion was successful")
    path: str = Field(..., description="Deleted package path")


SEQUENCES_DIR = Path("sequences")


async def install_dependencies(
    dependencies: List[str],
    upgrade: bool = False,
) -> DependenciesResult:
    """
    Install Python package dependencies using pip.

    Args:
        dependencies: List of package specifications (e.g., ["pyserial>=3.5", "numpy"])
        upgrade: Whether to upgrade already installed packages

    Returns:
        DependenciesResult with installation details
    """
    result = DependenciesResult(total=len(dependencies))

    if not dependencies:
        return result

    for pkg_spec in dependencies:
        install_result = await _install_single_package(pkg_spec, upgrade)
        result.details.append(install_result)

        if install_result.success:
            if install_result.already_installed:
                result.skipped += 1
            else:
                result.installed += 1
        else:
            result.failed += 1

    return result


async def _install_single_package(
    pkg_spec: str,
    upgrade: bool = False,
) -> DependencyInstallResult:
    """
    Install a single Python package.

    Args:
        pkg_spec: Package specification (e.g., "pyserial>=3.5")
        upgrade: Whether to upgrade if already installed

    Returns:
        DependencyInstallResult with installation status
    """
    # Extract package name (without version specifier) for checking
    pkg_name = pkg_spec.split(">=")[0].split("<=")[0].split("==")[0].split("<")[0].split(">")[0].strip()

    # Check if already installed
    try:
        check_cmd = [sys.executable, "-m", "pip", "show", pkg_name]
        check_result = await asyncio.to_thread(
            subprocess.run,
            check_cmd,
            capture_output=True,
            text=True,
        )
        already_installed = check_result.returncode == 0
    except Exception:
        already_installed = False

    if already_installed and not upgrade:
        logger.debug(f"Package already installed: {pkg_spec}")
        return DependencyInstallResult(
            package=pkg_spec,
            success=True,
            message="Already installed",
            already_installed=True,
        )

    # Install the package
    try:
        cmd = [sys.executable, "-m", "pip", "install", pkg_spec]
        if upgrade:
            cmd.append("--upgrade")
        cmd.append("--quiet")  # Less verbose output

        logger.info(f"Installing dependency: {pkg_spec}")

        proc_result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout per package
        )

        if proc_result.returncode == 0:
            logger.info(f"Successfully installed: {pkg_spec}")
            return DependencyInstallResult(
                package=pkg_spec,
                success=True,
                message="Installed successfully",
                already_installed=False,
            )
        else:
            error_msg = proc_result.stderr.strip() or proc_result.stdout.strip()
            logger.error(f"Failed to install {pkg_spec}: {error_msg}")
            return DependencyInstallResult(
                package=pkg_spec,
                success=False,
                message=f"Installation failed: {error_msg[:200]}",  # Truncate long errors
                already_installed=False,
            )

    except subprocess.TimeoutExpired:
        logger.error(f"Timeout installing {pkg_spec}")
        return DependencyInstallResult(
            package=pkg_spec,
            success=False,
            message="Installation timed out (120s)",
            already_installed=False,
        )
    except Exception as e:
        logger.exception(f"Error installing {pkg_spec}: {e}")
        return DependencyInstallResult(
            package=pkg_spec,
            success=False,
            message=f"Installation error: {str(e)[:200]}",
            already_installed=False,
        )


@router.post(
    "/upload",
    response_model=ApiResponse[SequenceUploadResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Upload sequence package",
    description="""
    Upload a sequence package as a ZIP file.

    The ZIP file should contain a directory with:
    - manifest.yaml (required): Package metadata and configuration
    - sequence.py (required): Main sequence class with @sequence decorator
    - drivers/ (optional): Hardware driver implementations

    If a package with the same name already exists, use `force=true` to overwrite.
    """,
)
async def upload_sequence(
    file: UploadFile = File(..., description="ZIP file containing the sequence package"),
    force: bool = Query(False, description="Overwrite existing package if it exists"),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SequenceUploadResponse]:
    """
    Upload and install a sequence package from a ZIP file.
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a ZIP archive with .zip extension",
        )

    temp_dir = None
    try:
        # Read uploaded file
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        # Validate it's a valid ZIP file
        try:
            zip_buffer = io.BytesIO(content)
            with zipfile.ZipFile(zip_buffer, "r") as zf:
                # Get package name from ZIP structure
                result = _extract_and_validate_zip(zf)
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ZIP file format",
            )

        if not result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid sequence package: {'; '.join(result['errors'])}",
            )

        package_name = result["name"]
        packages_dir = sequence_loader.packages_path

        # Ensure sequences directory exists
        packages_dir.mkdir(parents=True, exist_ok=True)

        # Check if package already exists
        target_path = packages_dir / package_name
        backup_path = None

        if target_path.exists():
            if not force:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Package '{package_name}' already exists. Use force=true to overwrite.",
                )
            # Backup existing package (don't delete yet)
            backup_path = target_path.with_suffix(".backup")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.move(str(target_path), str(backup_path))
            logger.info(f"Backed up existing package: {package_name}")

        # Extract to temporary directory first
        temp_dir = tempfile.mkdtemp(prefix="sequence_upload_")
        zip_buffer.seek(0)

        try:
            with zipfile.ZipFile(zip_buffer, "r") as zf:
                zf.extractall(temp_dir)

            # Find the package directory in temp
            temp_path = Path(temp_dir)
            extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir()]

            if len(extracted_dirs) == 1:
                # ZIP contains a single root directory
                source_path = extracted_dirs[0]
            else:
                # ZIP contains files directly at root
                source_path = temp_path

            # Move to final location
            shutil.move(str(source_path), str(target_path))
            logger.info(f"Installed sequence package: {package_name} to {target_path}")

            # Success - remove backup
            if backup_path and backup_path.exists():
                shutil.rmtree(backup_path)
                logger.info(f"Removed backup: {backup_path}")

        except Exception as e:
            # Restore from backup if installation failed
            if backup_path and backup_path.exists():
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.move(str(backup_path), str(target_path))
                logger.info(f"Restored package from backup: {package_name}")
            raise

        # Reload the package to validate and cache
        manifest = await sequence_loader.reload_package(package_name)

        # Install dependencies from manifest
        deps_result = None
        python_deps = manifest.get_required_packages()
        if python_deps:
            logger.info(f"Installing {len(python_deps)} dependencies for {package_name}")
            deps_result = await install_dependencies(python_deps)

            if deps_result.failed > 0:
                failed_pkgs = [d.package for d in deps_result.details if not d.success]
                logger.warning(
                    f"Some dependencies failed to install for {package_name}: {failed_pkgs}"
                )

        response = SequenceUploadResponse(
            name=manifest.name,
            version=manifest.version,
            path=str(target_path),
            hardware=manifest.get_hardware_names(),
            parameters=manifest.get_parameter_names(),
            uploaded_at=datetime.now(),
            dependencies=deps_result,
        )

        # Build success message
        msg = f"Package '{package_name}' uploaded successfully"
        if deps_result:
            msg += f" ({deps_result.installed} deps installed, {deps_result.skipped} skipped"
            if deps_result.failed > 0:
                msg += f", {deps_result.failed} failed"
            msg += ")"

        return ApiResponse(
            success=True,
            data=response,
            message=msg,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to upload sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload sequence: {str(e)}",
        )
    finally:
        # Cleanup temp directory
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


@router.post(
    "/upload-folder",
    response_model=ApiResponse[SequenceUploadResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Upload sequence package from folder",
    description="""
    Upload a sequence package as individual files (for folder upload support).

    The files should include:
    - manifest.yaml (required): Package metadata and configuration
    - sequence.py (required): Main sequence class with @sequence decorator
    - drivers/ (optional): Hardware driver implementations

    File paths should be relative to the package root.
    If a package with the same name already exists, use `force=true` to overwrite.
    """,
)
async def upload_sequence_folder(
    files: List[UploadFile] = File(..., description="Files from the sequence package folder"),
    force: bool = Query(False, description="Overwrite existing package if it exists"),
    sequence_loader: SequenceLoader = Depends(get_sequence_loader),
) -> ApiResponse[SequenceUploadResponse]:
    """
    Upload and install a sequence package from a folder (multiple files).
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded",
        )

    temp_dir = None
    try:
        # Create temporary directory to reconstruct folder structure
        temp_dir = tempfile.mkdtemp(prefix="sequence_folder_upload_")
        temp_path = Path(temp_dir)

        # Find the common root directory from file paths
        # File paths come as "folder_name/file.py" or "folder_name/subfolder/file.py"
        root_dirs = set()
        for f in files:
            if f.filename:
                parts = f.filename.split("/")
                if len(parts) > 1:
                    root_dirs.add(parts[0])

        if len(root_dirs) == 1:
            # All files are under a common root directory
            package_root = list(root_dirs)[0]
        else:
            # Files are at root level, use manifest name later
            package_root = None

        # Write files to temp directory
        manifest_content = None
        for f in files:
            if not f.filename:
                continue

            content = await f.read()
            file_path = temp_path / f.filename

            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_bytes(content)

            # Capture manifest content
            if f.filename.endswith("manifest.yaml"):
                manifest_content = content.decode("utf-8")

        if not manifest_content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="manifest.yaml not found in uploaded files",
            )

        # Parse manifest to get package name
        try:
            manifest_data = yaml.safe_load(manifest_content)
            manifest = SequenceManifest.model_validate(manifest_data)
        except yaml.YAMLError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid YAML in manifest: {e}",
            )
        except ValidationError as e:
            errors = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in e.errors()]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid manifest: {'; '.join(errors)}",
            )

        package_name = manifest.name
        packages_dir = sequence_loader.packages_path

        # Ensure sequences directory exists
        packages_dir.mkdir(parents=True, exist_ok=True)

        # Check if package already exists
        target_path = packages_dir / package_name
        backup_path = None

        if target_path.exists():
            if not force:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Package '{package_name}' already exists. Use force=true to overwrite.",
                )
            # Backup existing package (don't delete yet)
            backup_path = target_path.with_suffix(".backup")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.move(str(target_path), str(backup_path))
            logger.info(f"Backed up existing package: {package_name}")

        try:
            # Determine source path
            if package_root:
                source_path = temp_path / package_root
            else:
                source_path = temp_path

            # Move to final location
            shutil.move(str(source_path), str(target_path))
            logger.info(f"Installed sequence package from folder: {package_name} to {target_path}")

            # Success - remove backup
            if backup_path and backup_path.exists():
                shutil.rmtree(backup_path)
                logger.info(f"Removed backup: {backup_path}")

        except Exception as e:
            # Restore from backup if installation failed
            if backup_path and backup_path.exists():
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.move(str(backup_path), str(target_path))
                logger.info(f"Restored package from backup: {package_name}")
            raise

        # Reload the package to validate and cache
        manifest = await sequence_loader.reload_package(package_name)

        # Install dependencies from manifest
        deps_result = None
        python_deps = manifest.get_required_packages()
        if python_deps:
            logger.info(f"Installing {len(python_deps)} dependencies for {package_name}")
            deps_result = await install_dependencies(python_deps)

            if deps_result.failed > 0:
                failed_pkgs = [d.package for d in deps_result.details if not d.success]
                logger.warning(
                    f"Some dependencies failed to install for {package_name}: {failed_pkgs}"
                )

        response = SequenceUploadResponse(
            name=manifest.name,
            version=manifest.version,
            path=str(target_path),
            hardware=manifest.get_hardware_names(),
            parameters=manifest.get_parameter_names(),
            uploaded_at=datetime.now(),
            dependencies=deps_result,
        )

        # Build success message
        msg = f"Package '{package_name}' uploaded successfully (from folder)"
        if deps_result:
            msg += f" ({deps_result.installed} deps installed, {deps_result.skipped} skipped"
            if deps_result.failed > 0:
                msg += f", {deps_result.failed} failed"
            msg += ")"

        return ApiResponse(
            success=True,
            data=response,
            message=msg,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to upload sequence folder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload sequence: {str(e)}",
        )
    finally:
        # Cleanup temp directory
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


@router.post(
    "/validate",
    response_model=ApiResponse[SequenceValidationResult],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Validate sequence package",
    description="""
    Validate a sequence package ZIP file without installing it.

    Returns validation results including any errors or warnings found.
    """,
)
async def validate_sequence(
    file: UploadFile = File(..., description="ZIP file containing the sequence package"),
) -> ApiResponse[SequenceValidationResult]:
    """
    Validate a sequence package without installing it.
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a ZIP archive with .zip extension",
        )

    try:
        content = await file.read()

        if len(content) == 0:
            return ApiResponse(
                success=True,
                data=SequenceValidationResult(
                    valid=False,
                    errors=[ValidationErrorDetail(field="file", message="Uploaded file is empty")],
                ),
            )

        try:
            zip_buffer = io.BytesIO(content)
            with zipfile.ZipFile(zip_buffer, "r") as zf:
                result = _extract_and_validate_zip(zf)
        except zipfile.BadZipFile:
            return ApiResponse(
                success=True,
                data=SequenceValidationResult(
                    valid=False,
                    errors=[ValidationErrorDetail(field="file", message="Invalid ZIP file format")],
                ),
            )

        # Convert string errors to ValidationErrorDetail objects
        error_details = [
            ValidationErrorDetail(field="package", message=err)
            for err in result.get("errors", [])
        ]

        # Build manifest info if valid
        manifest_info = None
        if result["valid"] and result.get("name"):
            manifest_info = ManifestInfo(
                name=result["name"],
                version=result.get("version", "0.0.0"),
                displayName=result.get("display_name"),
                description=result.get("description"),
            )

        return ApiResponse(
            success=True,
            data=SequenceValidationResult(
                valid=result["valid"],
                errors=error_details,
                warnings=result.get("warnings", []),
                manifest=manifest_info,
            ),
        )

    except Exception as e:
        logger.exception(f"Failed to validate sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate sequence: {str(e)}",
        )


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


def _extract_and_validate_zip(zf: zipfile.ZipFile) -> Dict[str, Any]:
    """
    Extract and validate ZIP file contents.

    Returns:
        Dictionary with validation results
    """
    result: Dict[str, Any] = {
        "valid": False,
        "name": None,
        "version": None,
        "errors": [],
        "warnings": [],
        "hardware": [],
        "parameters": [],
    }

    file_list = zf.namelist()

    if not file_list:
        result["errors"].append("ZIP file is empty")
        return result

    # Find manifest.yaml
    manifest_path = None
    package_name = None

    for name in file_list:
        if name.endswith("manifest.yaml"):
            manifest_path = name
            # Extract package name from path
            parts = name.split("/")
            if len(parts) > 1:
                package_name = parts[0]
            break

    if manifest_path is None:
        result["errors"].append("manifest.yaml not found in package")
        return result

    # Read and validate manifest
    try:
        manifest_content = zf.read(manifest_path).decode("utf-8")
        manifest_data = yaml.safe_load(manifest_content)

        if manifest_data is None:
            result["errors"].append("manifest.yaml is empty")
            return result

        # Validate against schema
        manifest = SequenceManifest.model_validate(manifest_data)

        result["name"] = manifest.name
        result["version"] = manifest.version
        result["display_name"] = manifest.name  # Use name as display_name
        result["description"] = manifest.description
        result["hardware"] = manifest.get_hardware_names()
        result["parameters"] = manifest.get_parameter_names()

        # Use manifest name as package name if not extracted from path
        if package_name is None:
            package_name = manifest.name

    except yaml.YAMLError as e:
        result["errors"].append(f"Invalid YAML in manifest: {e}")
        return result
    except ValidationError as e:
        for error in e.errors():
            field = ".".join(str(f) for f in error["loc"])
            result["errors"].append(f"Manifest error at '{field}': {error['msg']}")
        return result
    except Exception as e:
        result["errors"].append(f"Failed to parse manifest: {e}")
        return result

    # Check for entry point file
    entry_module = manifest.entry_point.module
    entry_file_options = [
        f"{package_name}/{entry_module}.py",
        f"{entry_module}.py",
    ]

    entry_found = False
    for option in entry_file_options:
        if option in file_list:
            entry_found = True
            break

    if not entry_found:
        result["errors"].append(f"Entry point module '{entry_module}.py' not found")

    # Check for hardware drivers
    for hw_name, hw_def in manifest.hardware.items():
        driver_module = hw_def.driver
        driver_file_options = [
            f"{package_name}/drivers/{driver_module}.py",
            f"{package_name}/{driver_module}.py",
            f"drivers/{driver_module}.py",
            f"{driver_module}.py",
        ]

        driver_found = False
        for option in driver_file_options:
            if option in file_list:
                driver_found = True
                break

        if not driver_found:
            result["warnings"].append(
                f"Driver '{driver_module}' for hardware '{hw_name}' not found in package "
                f"(may be a system module)"
            )

    # If we get here with no errors, package is valid
    if not result["errors"]:
        result["valid"] = True
        result["name"] = package_name or manifest.name

    return result
