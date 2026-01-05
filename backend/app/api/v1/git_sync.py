"""
Git Sync API endpoints.

Provides endpoints for managing Git repository sync configuration
and triggering manual sync operations.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_async_db
from app.crud.git_sync import git_sync_crud
from app.models.user import User, UserRole
from app.schemas.git_sync import (
    GitRepoInfoResponse,
    GitSyncConfigCreate,
    GitSyncConfigResponse,
    GitSyncConfigUpdate,
    GitSyncResultResponse,
    GitSyncStatusResponse,
    GitSyncTriggerRequest,
)
from app.services.git_sync_service import git_sync_service

router = APIRouter(prefix="/git-sync", tags=["git-sync"])


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


# ============================================================================
# Configuration Endpoints
# ============================================================================


@router.get("/configs", response_model=List[GitSyncConfigResponse])
async def list_git_sync_configs(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> List[GitSyncConfigResponse]:
    """List all Git sync configurations."""
    configs = await git_sync_crud.get_all(db)
    return [GitSyncConfigResponse.model_validate(c) for c in configs]


@router.post("/configs", response_model=GitSyncConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_git_sync_config(
    config_data: GitSyncConfigCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> GitSyncConfigResponse:
    """Create a new Git sync configuration."""
    require_manager_role(current_user)

    # Check for duplicate name
    existing = await git_sync_crud.get_by_name(db, config_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Config with name '{config_data.name}' already exists",
        )

    config = await git_sync_crud.create(db, config_data)
    await db.commit()

    return GitSyncConfigResponse.model_validate(config)


@router.get("/configs/{config_name}", response_model=GitSyncConfigResponse)
async def get_git_sync_config(
    config_name: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> GitSyncConfigResponse:
    """Get a Git sync configuration by name."""
    config = await git_sync_crud.get_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{config_name}' not found",
        )

    return GitSyncConfigResponse.model_validate(config)


@router.patch("/configs/{config_name}", response_model=GitSyncConfigResponse)
async def update_git_sync_config(
    config_name: str,
    update_data: GitSyncConfigUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> GitSyncConfigResponse:
    """Update a Git sync configuration."""
    require_manager_role(current_user)

    config = await git_sync_crud.get_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{config_name}' not found",
        )

    config = await git_sync_crud.update(db, config, update_data)
    await db.commit()

    return GitSyncConfigResponse.model_validate(config)


@router.delete("/configs/{config_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_git_sync_config(
    config_name: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a Git sync configuration."""
    require_manager_role(current_user)

    config = await git_sync_crud.get_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{config_name}' not found",
        )

    await git_sync_crud.delete(db, config)
    await db.commit()


# ============================================================================
# Status & Info Endpoints
# ============================================================================


@router.get("/configs/{config_name}/status", response_model=GitSyncStatusResponse)
async def check_git_sync_status(
    config_name: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> GitSyncStatusResponse:
    """Check sync status and detect updates for a configuration."""
    config = await git_sync_crud.get_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{config_name}' not found",
        )

    status_response = await git_sync_service.check_for_updates(config)

    # Update last_check_at
    await git_sync_crud.update_sync_status(db, config, config.sync_status)
    await db.commit()

    return status_response


@router.get("/configs/{config_name}/repo-info", response_model=GitRepoInfoResponse)
async def get_repo_info(
    config_name: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> GitRepoInfoResponse:
    """Get repository information including available sequences."""
    config = await git_sync_crud.get_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{config_name}' not found",
        )

    try:
        return await git_sync_service.get_repo_info(config)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# Sync Endpoints
# ============================================================================


@router.post("/configs/{config_name}/sync", response_model=GitSyncResultResponse)
async def trigger_git_sync(
    config_name: str,
    request: GitSyncTriggerRequest = GitSyncTriggerRequest(),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> GitSyncResultResponse:
    """Manually trigger a sync for a configuration."""
    require_manager_role(current_user)

    config = await git_sync_crud.get_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{config_name}' not found",
        )

    # Update status to syncing
    await git_sync_crud.update_sync_status(db, config, "syncing")
    await db.commit()

    # Perform sync
    result = await git_sync_service.sync_sequences(
        config,
        force=request.force,
        sequence_names=request.sequence_names,
        user_id=current_user.id,
    )

    return result


@router.post("/sync-all", response_model=List[GitSyncResultResponse])
async def trigger_sync_all(
    request: GitSyncTriggerRequest = GitSyncTriggerRequest(),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> List[GitSyncResultResponse]:
    """Trigger sync for all enabled configurations."""
    require_manager_role(current_user)

    configs = await git_sync_crud.get_enabled(db)
    results = []

    for config in configs:
        # Update status
        await git_sync_crud.update_sync_status(db, config, "syncing")
        await db.commit()

        # Sync
        result = await git_sync_service.sync_sequences(
            config,
            force=request.force,
            sequence_names=request.sequence_names,
            user_id=current_user.id,
        )
        results.append(result)

    return results
