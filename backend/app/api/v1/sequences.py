"""
Sequence management API endpoints.

Provides endpoints for uploading, downloading, and deploying test sequences
to Station Services.
"""

import io
import re
import zipfile
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import httpx
import yaml
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_async_db, get_station_auth, get_auth_context, StationAuth
from app.crud.sequence import sequence_crud
from app.models.sequence import Sequence
from app.models.user import User, UserRole
from app.schemas.sequence import (
    GithubUploadRequest,
    SequenceDeployRequest,
    SequenceDeployResponse,
    SequenceDeploymentResponse,
    SequenceDownloadInfo,
    SequenceListParams,
    SequenceListResponse,
    SequenceManifest,
    SequencePullRequest,
    SequencePullResponse,
    SequenceResponse,
    SequenceRollbackRequest,
    SequenceRollbackResponse,
    SequenceUpdate,
    SequenceUploadResponse,
    SequenceVersionResponse,
)

router = APIRouter(prefix="/sequences", tags=["sequences"])


# ============================================================================
# Helper Functions
# ============================================================================


def require_manager_role(user: User) -> None:
    """Require MANAGER or ADMIN role."""
    if user.role not in (UserRole.MANAGER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin role required",
        )


async def get_sequence_or_404(
    db: AsyncSession,
    sequence_id: Optional[int] = None,
    sequence_name: Optional[str] = None,
) -> Sequence:
    """Get sequence by ID or name, or raise 404."""
    if sequence_id:
        sequence = await sequence_crud.get_by_id(db, sequence_id)
    elif sequence_name:
        sequence = await sequence_crud.get_by_name(db, sequence_name)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sequence_id or sequence_name required",
        )

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found",
        )
    return sequence


def parse_manifest(zip_data: bytes) -> SequenceManifest:
    """
    Parse manifest.yaml from ZIP package.

    Raises:
        HTTPException: If manifest is missing or invalid
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
            # Find manifest.yaml
            manifest_path = None
            for name in zf.namelist():
                if name.endswith("manifest.yaml") or name.endswith("manifest.yml"):
                    manifest_path = name
                    break

            if not manifest_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="manifest.yaml not found in package",
                )

            # Parse manifest
            with zf.open(manifest_path) as f:
                manifest_data = yaml.safe_load(f)

            return SequenceManifest(
                name=manifest_data.get("name", ""),
                version=manifest_data.get("version", "1.0.0"),
                display_name=manifest_data.get("display_name"),
                description=manifest_data.get("description"),
                hardware=manifest_data.get("hardware"),
                parameters=manifest_data.get("parameters"),
                steps=manifest_data.get("steps"),
            )

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ZIP file",
        )
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid manifest.yaml: {e}",
        )


def validate_package_structure(zip_data: bytes, sequence_name: str) -> None:
    """
    Validate package structure.

    Checks for required files (main.py, __init__.py).
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zf:
            names = zf.namelist()

            # Check for main.py (CLI entry point)
            has_main = any(
                name.endswith("main.py") and sequence_name in name
                for name in names
            )
            if not has_main:
                # Also check for main.py at root of package
                has_main = any(
                    name == "main.py" or name.endswith("/main.py")
                    for name in names
                )

            if not has_main:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="main.py (CLI entry point) not found in package",
                )

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ZIP file",
        )


def parse_github_url(url: str) -> tuple[str, str, str, str]:
    """
    Parse GitHub URL to extract owner, repo, branch, and path.

    Supports formats:
    - https://github.com/owner/repo/tree/branch/path/to/folder
    - https://github.com/owner/repo/tree/branch (entire repo)

    Returns:
        Tuple of (owner, repo, branch, path)

    Raises:
        HTTPException: If URL format is invalid
    """
    parsed = urlparse(url)

    if parsed.netloc != "github.com":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only GitHub URLs are supported",
        )

    # Parse path: /owner/repo/tree/branch/path...
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 4 or path_parts[2] != "tree":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GitHub URL format. Expected: https://github.com/owner/repo/tree/branch/path",
        )

    owner = path_parts[0]
    repo = path_parts[1]
    branch = path_parts[3]
    folder_path = "/".join(path_parts[4:]) if len(path_parts) > 4 else ""

    return owner, repo, branch, folder_path


async def download_github_folder_as_zip(
    owner: str, repo: str, branch: str, folder_path: str
) -> bytes:
    """
    Download a GitHub folder as a ZIP file.

    Uses GitHub API to list files and download them, then creates a ZIP.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        folder_path: Path to folder within repo

    Returns:
        ZIP file contents as bytes
    """
    base_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "F2X-NeuroHub-Sequence-Uploader",
    }

    async def fetch_contents(path: str) -> list:
        """Recursively fetch directory contents."""
        url = f"{base_api_url}/{path}" if path else base_api_url
        url = f"{url}?ref={branch}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Path not found: {path}",
                )
            elif response.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="GitHub API rate limit exceeded. Please try again later.",
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_BAD_GATEWAY,
                    detail=f"GitHub API error: {response.status_code}",
                )

            return response.json()

    async def download_file(download_url: str) -> bytes:
        """Download a single file."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(download_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_BAD_GATEWAY,
                    detail=f"Failed to download file: {download_url}",
                )
            return response.content

    async def process_contents(path: str, files: dict) -> None:
        """Recursively process directory contents."""
        contents = await fetch_contents(path)

        if not isinstance(contents, list):
            # Single file
            contents = [contents]

        for item in contents:
            item_path = item["path"]
            # Calculate relative path from folder_path
            if folder_path:
                rel_path = item_path[len(folder_path):].lstrip("/")
            else:
                rel_path = item_path

            if item["type"] == "file":
                file_content = await download_file(item["download_url"])
                files[rel_path] = file_content
            elif item["type"] == "dir":
                await process_contents(item_path, files)

    # Collect all files
    files: Dict[str, bytes] = {}
    await process_contents(folder_path, files)

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files found in the specified path",
        )

    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, content in files.items():
            zf.writestr(file_path, content)

    return zip_buffer.getvalue()


# ============================================================================
# List & Get Endpoints
# ============================================================================


@router.get("", response_model=Dict[str, Any])
async def list_sequences(
    is_active: Optional[bool] = Query(None),
    is_deprecated: Optional[bool] = Query(None),
    process_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> Dict[str, Any]:
    """
    List all sequences with filtering and pagination.

    Returns list of sequences with total count.
    Supports both JWT Bearer token (user) and X-API-Key (station) authentication.
    """
    params = SequenceListParams(
        is_active=is_active,
        is_deprecated=is_deprecated,
        process_id=process_id,
        search=search,
        skip=skip,
        limit=limit,
    )

    sequences, total = await sequence_crud.get_list(db, params)

    return {
        "items": [SequenceListResponse.model_validate(s) for s in sequences],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{sequence_name}", response_model=SequenceResponse)
async def get_sequence(
    sequence_name: str,
    db: AsyncSession = Depends(get_async_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> SequenceResponse:
    """Get sequence details by name. Supports JWT and X-API-Key authentication."""
    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)
    return SequenceResponse.model_validate(sequence)


@router.get("/{sequence_name}/versions", response_model=List[SequenceVersionResponse])
async def get_sequence_versions(
    sequence_name: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> List[SequenceVersionResponse]:
    """Get version history for a sequence. Supports JWT and X-API-Key authentication."""
    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)
    versions = await sequence_crud.get_versions(db, sequence.id, limit=limit)
    return [SequenceVersionResponse.model_validate(v) for v in versions]


# ============================================================================
# Upload Endpoint
# ============================================================================


@router.post("/upload", response_model=SequenceUploadResponse)
async def upload_sequence(
    file: UploadFile = File(..., description="ZIP package file"),
    change_notes: Optional[str] = Query(None, description="Version change notes"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> SequenceUploadResponse:
    """
    Upload a sequence package (ZIP file).

    The ZIP must contain:
    - manifest.yaml with name, version, and metadata
    - main.py as CLI entry point
    - sequence.py with SequenceBase implementation

    If a sequence with the same name exists, it will be updated
    and the previous version saved to history.
    """
    require_manager_role(current_user)

    # Read file
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a ZIP archive",
        )

    zip_data = await file.read()
    if len(zip_data) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package size exceeds 50MB limit",
        )

    # Parse manifest
    manifest = parse_manifest(zip_data)
    if not manifest.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sequence name required in manifest.yaml",
        )

    # Validate package structure
    validate_package_structure(zip_data, manifest.name)

    # Calculate checksum and encode
    checksum = sequence_crud.calculate_checksum(zip_data)
    package_data = sequence_crud.encode_package(zip_data)
    package_size = len(zip_data)

    # Check if sequence exists
    existing = await sequence_crud.get_by_name(db, manifest.name)

    if existing:
        # Update existing sequence
        previous_version = existing.version

        # Check if same checksum (no actual change)
        if existing.checksum == checksum:
            return SequenceUploadResponse(
                id=existing.id,
                name=existing.name,
                version=existing.version,
                display_name=existing.display_name,
                checksum=checksum,
                package_size=package_size,
                is_new=False,
                previous_version=previous_version,
                message="Package unchanged (same checksum)",
            )

        # Auto-increment version (ignore manifest version)
        new_version = sequence_crud.increment_version(existing.version)

        sequence, version = await sequence_crud.update_package(
            db,
            existing,
            version=new_version,
            package_data=package_data,
            checksum=checksum,
            package_size=package_size,
            hardware=manifest.hardware,
            parameters=manifest.parameters,
            steps=manifest.steps,
            uploaded_by=current_user.id,
            change_notes=change_notes,
        )

        await db.commit()

        return SequenceUploadResponse(
            id=sequence.id,
            name=sequence.name,
            version=sequence.version,
            display_name=sequence.display_name,
            checksum=checksum,
            package_size=package_size,
            is_new=False,
            previous_version=previous_version,
            message=f"Updated from v{previous_version} to v{sequence.version} (auto-versioned)",
        )

    else:
        # Create new sequence - always start at 1.0.0
        sequence = await sequence_crud.create(
            db,
            name=manifest.name,
            version="1.0.0",
            package_data=package_data,
            checksum=checksum,
            package_size=package_size,
            display_name=manifest.display_name,
            description=manifest.description,
            hardware=manifest.hardware,
            parameters=manifest.parameters,
            steps=manifest.steps,
            uploaded_by=current_user.id,
        )

        await db.commit()

        return SequenceUploadResponse(
            id=sequence.id,
            name=sequence.name,
            version=sequence.version,
            display_name=sequence.display_name,
            checksum=checksum,
            package_size=package_size,
            is_new=True,
            previous_version=None,
            message=f"New sequence created: {sequence.name} v{sequence.version}",
        )


# ============================================================================
# GitHub Upload Endpoint
# ============================================================================


@router.post("/upload/github", response_model=SequenceUploadResponse)
async def upload_sequence_from_github(
    request: GithubUploadRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> SequenceUploadResponse:
    """
    Upload a sequence from a GitHub repository URL.

    The URL should point to a folder containing:
    - manifest.yaml with name, version, and metadata
    - main.py as CLI entry point
    - sequence.py with SequenceBase implementation

    Supported URL formats:
    - https://github.com/owner/repo/tree/branch/path/to/sequence

    If a sequence with the same name exists, it will be updated
    and the previous version saved to history.
    """
    require_manager_role(current_user)

    # Parse GitHub URL
    owner, repo, branch, folder_path = parse_github_url(request.url)

    # Download folder as ZIP
    try:
        zip_data = await download_github_folder_as_zip(owner, repo, branch, folder_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_BAD_GATEWAY,
            detail=f"Failed to download from GitHub: {str(e)}",
        )

    if len(zip_data) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Package size exceeds 50MB limit",
        )

    # Parse manifest
    manifest = parse_manifest(zip_data)
    if not manifest.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sequence name required in manifest.yaml",
        )

    # Validate package structure
    validate_package_structure(zip_data, manifest.name)

    # Calculate checksum and encode
    checksum = sequence_crud.calculate_checksum(zip_data)
    package_data = sequence_crud.encode_package(zip_data)
    package_size = len(zip_data)

    # Check if sequence exists
    existing = await sequence_crud.get_by_name(db, manifest.name)

    if existing:
        # Update existing sequence
        previous_version = existing.version

        # Check if same checksum (no actual change)
        if existing.checksum == checksum:
            return SequenceUploadResponse(
                id=existing.id,
                name=existing.name,
                version=existing.version,
                display_name=existing.display_name,
                checksum=checksum,
                package_size=package_size,
                is_new=False,
                previous_version=previous_version,
                message="Package unchanged (same checksum)",
            )

        # Auto-increment version (ignore manifest version)
        new_version = sequence_crud.increment_version(existing.version)

        # Add GitHub URL to change notes
        change_notes = request.change_notes or ""
        if change_notes:
            change_notes += f"\n\nSource: {request.url}"
        else:
            change_notes = f"Source: {request.url}"

        sequence, version = await sequence_crud.update_package(
            db,
            existing,
            version=new_version,
            package_data=package_data,
            checksum=checksum,
            package_size=package_size,
            hardware=manifest.hardware,
            parameters=manifest.parameters,
            steps=manifest.steps,
            uploaded_by=current_user.id,
            change_notes=change_notes,
        )

        await db.commit()

        return SequenceUploadResponse(
            id=sequence.id,
            name=sequence.name,
            version=sequence.version,
            display_name=sequence.display_name,
            checksum=checksum,
            package_size=package_size,
            is_new=False,
            previous_version=previous_version,
            message=f"Updated from v{previous_version} to v{sequence.version} (from GitHub)",
        )

    else:
        # Create new sequence - always start at 1.0.0
        sequence = await sequence_crud.create(
            db,
            name=manifest.name,
            version="1.0.0",
            package_data=package_data,
            checksum=checksum,
            package_size=package_size,
            display_name=manifest.display_name,
            description=manifest.description,
            hardware=manifest.hardware,
            parameters=manifest.parameters,
            steps=manifest.steps,
            uploaded_by=current_user.id,
        )

        await db.commit()

        return SequenceUploadResponse(
            id=sequence.id,
            name=sequence.name,
            version=sequence.version,
            display_name=sequence.display_name,
            checksum=checksum,
            package_size=package_size,
            is_new=True,
            previous_version=None,
            message=f"New sequence created: {sequence.name} v{sequence.version} (from GitHub)",
        )


# ============================================================================
# Download Endpoint
# ============================================================================


@router.get("/{sequence_name}/download")
async def download_sequence(
    sequence_name: str,
    version: Optional[str] = Query(None, description="Specific version to download"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """
    Download sequence package as ZIP file.

    If version is specified, downloads that version from history.
    Otherwise downloads the current version.
    """
    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)

    if version and version != sequence.version:
        # Get from version history
        version_record = await sequence_crud.get_version(db, sequence.id, version)
        if not version_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version} not found",
            )
        package_data = version_record.package_data
        download_version = version
    else:
        package_data = sequence.package_data
        download_version = sequence.version

    # Decode package
    zip_data = sequence_crud.decode_package(package_data)

    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{sequence_name}-{download_version}.zip"',
            "X-Sequence-Version": download_version,
            "X-Sequence-Checksum": sequence.checksum,
        },
    )


# ============================================================================
# Update & Delete Endpoints
# ============================================================================


@router.patch("/{sequence_name}", response_model=SequenceResponse)
async def update_sequence(
    sequence_name: str,
    update_data: SequenceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> SequenceResponse:
    """Update sequence metadata (not package)."""
    require_manager_role(current_user)

    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)
    sequence = await sequence_crud.update(db, sequence, update_data)
    await db.commit()

    return SequenceResponse.model_validate(sequence)


@router.delete("/{sequence_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sequence(
    sequence_name: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete sequence and all versions."""
    require_manager_role(current_user)

    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)
    await sequence_crud.delete(db, sequence)
    await db.commit()


# ============================================================================
# Deployment Endpoints
# ============================================================================


@router.post("/{sequence_name}/deploy", response_model=SequenceDeployResponse)
async def deploy_sequence(
    sequence_name: str,
    deploy_request: SequenceDeployRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> SequenceDeployResponse:
    """
    Deploy sequence to a station.

    Creates a deployment record. The actual deployment is handled
    by Station Service polling or push notification.
    """
    require_manager_role(current_user)

    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)

    if not sequence.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deploy inactive sequence",
        )

    version = deploy_request.version or sequence.version

    # Check if version exists
    if version != sequence.version:
        version_record = await sequence_crud.get_version(db, sequence.id, version)
        if not version_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version} not found",
            )

    deployment = await sequence_crud.create_deployment(
        db,
        sequence_id=sequence.id,
        version=version,
        station_id=deploy_request.station_id,
        batch_id=deploy_request.batch_id,
        deployed_by=current_user.id,
    )

    await db.commit()

    return SequenceDeployResponse(
        deployment_id=deployment.id,
        sequence_name=sequence_name,
        version=version,
        station_id=deploy_request.station_id,
        batch_id=deploy_request.batch_id,
        status="pending",
        message=f"Deployment created for {sequence_name} v{version} to {deploy_request.station_id}",
    )


@router.get("/{sequence_name}/deployments", response_model=List[SequenceDeploymentResponse])
async def get_sequence_deployments(
    sequence_name: str,
    station_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> List[SequenceDeploymentResponse]:
    """Get deployment history for a sequence."""
    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)
    deployments = await sequence_crud.get_deployments(
        db,
        sequence_id=sequence.id,
        station_id=station_id,
        status=status,
        limit=limit,
    )
    return [SequenceDeploymentResponse.model_validate(d) for d in deployments]


@router.post("/{sequence_name}/rollback", response_model=SequenceRollbackResponse)
async def rollback_sequence(
    sequence_name: str,
    rollback_request: SequenceRollbackRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> SequenceRollbackResponse:
    """
    Rollback sequence to a previous version.

    Restores package data from version history.
    """
    require_manager_role(current_user)

    sequence = await get_sequence_or_404(db, sequence_name=sequence_name)

    # Get target version
    version_record = await sequence_crud.get_version(
        db, sequence.id, rollback_request.version
    )
    if not version_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {rollback_request.version} not found",
        )

    previous_version = sequence.version

    # Update package with version data
    sequence, _ = await sequence_crud.update_package(
        db,
        sequence,
        version=version_record.version,
        package_data=version_record.package_data,
        checksum=version_record.checksum,
        package_size=version_record.package_size,
        hardware=version_record.hardware,
        parameters=version_record.parameters,
        steps=version_record.steps,
        uploaded_by=current_user.id,
        change_notes=f"Rollback from v{previous_version}: {rollback_request.reason or 'No reason provided'}",
    )

    await db.commit()

    return SequenceRollbackResponse(
        sequence_name=sequence_name,
        previous_version=previous_version,
        new_version=sequence.version,
        message=f"Rolled back from v{previous_version} to v{sequence.version}",
    )


# ============================================================================
# Station Pull Endpoint (for Station Service)
# ============================================================================


@router.post("/{sequence_name}/pull", response_model=SequencePullResponse)
async def pull_sequence(
    sequence_name: str,
    pull_request: SequencePullRequest,
    db: AsyncSession = Depends(get_async_db),
    station: StationAuth = Depends(get_station_auth),
) -> SequencePullResponse:
    """
    Pull sequence for Station Service.

    This endpoint is called by Station Service to check for updates
    and download the latest version if needed.

    Requires X-API-Key header with valid station API key.
    The station_id in the request must match the API key's station_id.
    """
    # Verify station_id matches the authenticated station
    if pull_request.station_id != station.station_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Station ID mismatch: request={pull_request.station_id}, auth={station.station_id}",
        )

    sequence = await sequence_crud.get_by_name(db, sequence_name)

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence '{sequence_name}' not found",
        )

    if not sequence.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sequence is not active",
        )

    # Check if update needed
    needs_update = (
        pull_request.current_version is None
        or pull_request.current_version != sequence.version
    )

    # Return package data if update needed
    package_data = sequence.package_data if needs_update else None

    # Update deployment status if we have a pending deployment
    if needs_update:
        deployments = await sequence_crud.get_deployments(
            db,
            sequence_id=sequence.id,
            station_id=pull_request.station_id,
            status="pending",
            limit=1,
        )
        if deployments:
            await sequence_crud.update_deployment_status(
                db, deployments[0], "deployed"
            )
            await db.commit()

    return SequencePullResponse(
        name=sequence.name,
        version=sequence.version,
        checksum=sequence.checksum,
        package_size=sequence.package_size,
        needs_update=needs_update,
        package_data=package_data,
    )
