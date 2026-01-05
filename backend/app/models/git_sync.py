"""
Git Sync configuration model for automatic sequence synchronization.

Stores Git repository configuration and sync status for automatic
sequence updates from Git repositories.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GitSyncConfig(Base):
    """
    Git repository sync configuration.

    Stores configuration for automatic polling and syncing of sequences
    from a Git repository (GitHub, GitLab, etc.).
    """

    __tablename__ = "git_sync_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Repository configuration
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique config name (e.g., 'main-sequences')",
    )
    repository_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Git repository URL (HTTPS or SSH)",
    )
    branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="main",
        comment="Branch to track",
    )
    folder_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Path to sequences folder within repo (e.g., 'sequences/')",
    )

    # Authentication (optional)
    auth_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="none",
        comment="Auth type: none, token, ssh",
    )
    auth_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="GitHub/GitLab personal access token (encrypted)",
    )

    # Sync settings
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Enable automatic polling",
    )
    poll_interval_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60,
        comment="Polling interval in seconds",
    )
    auto_upload: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Automatically upload new sequences on change",
    )

    # Sync status
    last_commit_sha: Mapped[Optional[str]] = mapped_column(
        String(40),
        nullable=True,
        comment="Last synced commit SHA",
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful sync timestamp",
    )
    last_check_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last poll check timestamp",
    )
    sync_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="idle",
        comment="Status: idle, checking, syncing, error",
    )
    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Last error message if any",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<GitSyncConfig {self.name}: {self.repository_url}>"
