"""
Pydantic schemas for Git Sync API.

Provides request/response schemas for Git repository sync configuration.
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Request Schemas
# ============================================================================


class GitSyncConfigCreate(BaseModel):
    """Request schema for creating Git sync configuration."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique config name",
        examples=["main-sequences"],
    )
    repository_url: str = Field(
        ...,
        max_length=500,
        description="Git repository URL (HTTPS)",
        examples=["https://github.com/owner/sequences-repo"],
    )
    branch: str = Field(
        default="main",
        max_length=100,
        description="Branch to track",
    )
    folder_path: Optional[str] = Field(
        None,
        max_length=500,
        description="Path to sequences folder within repo",
        examples=["sequences/", "src/sequences"],
    )
    auth_type: Literal["none", "token"] = Field(
        default="none",
        description="Authentication type",
    )
    auth_token: Optional[str] = Field(
        None,
        description="GitHub/GitLab personal access token",
    )
    enabled: bool = Field(
        default=True,
        description="Enable automatic polling",
    )
    poll_interval_seconds: int = Field(
        default=60,
        ge=10,
        le=3600,
        description="Polling interval (10-3600 seconds)",
    )
    auto_upload: bool = Field(
        default=True,
        description="Automatically upload sequences on change",
    )


class GitSyncConfigUpdate(BaseModel):
    """Request schema for updating Git sync configuration."""

    repository_url: Optional[str] = Field(None, max_length=500)
    branch: Optional[str] = Field(None, max_length=100)
    folder_path: Optional[str] = Field(None, max_length=500)
    auth_type: Optional[Literal["none", "token"]] = None
    auth_token: Optional[str] = None
    enabled: Optional[bool] = None
    poll_interval_seconds: Optional[int] = Field(None, ge=10, le=3600)
    auto_upload: Optional[bool] = None


class GitSyncTriggerRequest(BaseModel):
    """Request schema for manual sync trigger."""

    force: bool = Field(
        default=False,
        description="Force sync even if no changes detected",
    )
    sequence_names: Optional[list[str]] = Field(
        None,
        description="Specific sequences to sync (None = all)",
    )


# ============================================================================
# Response Schemas
# ============================================================================


class GitSyncConfigResponse(BaseModel):
    """Response schema for Git sync configuration."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    repository_url: str
    branch: str
    folder_path: Optional[str] = None
    auth_type: str
    enabled: bool
    poll_interval_seconds: int
    auto_upload: bool
    last_commit_sha: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    last_check_at: Optional[datetime] = None
    sync_status: str
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GitSyncStatusResponse(BaseModel):
    """Response schema for sync status check."""

    config_name: str
    repository_url: str
    branch: str
    enabled: bool
    sync_status: str
    last_commit_sha: Optional[str] = None
    remote_commit_sha: Optional[str] = None
    has_updates: bool = False
    last_sync_at: Optional[datetime] = None
    last_check_at: Optional[datetime] = None
    last_error: Optional[str] = None
    sequences_changed: list[str] = Field(default_factory=list)


class GitSyncResultResponse(BaseModel):
    """Response schema for sync operation result."""

    config_name: str
    success: bool
    message: str
    commit_sha: Optional[str] = None
    sequences_updated: list[str] = Field(default_factory=list)
    sequences_created: list[str] = Field(default_factory=list)
    sequences_failed: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class GitRepoInfoResponse(BaseModel):
    """Response schema for repository information."""

    repository_url: str
    branch: str
    latest_commit_sha: str
    latest_commit_message: str
    latest_commit_date: datetime
    sequences_found: list[str] = Field(default_factory=list)
