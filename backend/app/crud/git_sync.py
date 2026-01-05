"""
CRUD operations for Git Sync configuration.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.git_sync import GitSyncConfig
from app.schemas.git_sync import GitSyncConfigCreate, GitSyncConfigUpdate


class GitSyncCRUD:
    """CRUD operations for GitSyncConfig."""

    async def get_by_id(self, db: AsyncSession, config_id: int) -> Optional[GitSyncConfig]:
        """Get config by ID."""
        result = await db.execute(
            select(GitSyncConfig).where(GitSyncConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[GitSyncConfig]:
        """Get config by name."""
        result = await db.execute(
            select(GitSyncConfig).where(GitSyncConfig.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> List[GitSyncConfig]:
        """Get all configs."""
        result = await db.execute(
            select(GitSyncConfig).order_by(GitSyncConfig.created_at)
        )
        return list(result.scalars().all())

    async def get_enabled(self, db: AsyncSession) -> List[GitSyncConfig]:
        """Get all enabled configs for polling."""
        result = await db.execute(
            select(GitSyncConfig)
            .where(GitSyncConfig.enabled == True)
            .order_by(GitSyncConfig.created_at)
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        config_data: GitSyncConfigCreate,
    ) -> GitSyncConfig:
        """Create new Git sync config."""
        config = GitSyncConfig(
            name=config_data.name,
            repository_url=config_data.repository_url,
            branch=config_data.branch,
            folder_path=config_data.folder_path,
            auth_type=config_data.auth_type,
            auth_token=config_data.auth_token,
            enabled=config_data.enabled,
            poll_interval_seconds=config_data.poll_interval_seconds,
            auto_upload=config_data.auto_upload,
            sync_status="idle",
        )
        db.add(config)
        await db.flush()
        return config

    async def update(
        self,
        db: AsyncSession,
        config: GitSyncConfig,
        update_data: GitSyncConfigUpdate,
    ) -> GitSyncConfig:
        """Update Git sync config."""
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(config, field, value)

        await db.flush()
        return config

    async def update_sync_status(
        self,
        db: AsyncSession,
        config: GitSyncConfig,
        status: str,
        commit_sha: Optional[str] = None,
        error: Optional[str] = None,
    ) -> GitSyncConfig:
        """Update sync status after check/sync."""
        config.sync_status = status
        config.last_check_at = datetime.now()

        if status == "synced" and commit_sha:
            config.last_commit_sha = commit_sha
            config.last_sync_at = datetime.now()
            config.last_error = None
        elif status == "error" and error:
            config.last_error = error

        await db.flush()
        return config

    async def delete(self, db: AsyncSession, config: GitSyncConfig) -> None:
        """Delete Git sync config."""
        await db.delete(config)
        await db.flush()


git_sync_crud = GitSyncCRUD()
