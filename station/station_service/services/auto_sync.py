"""
Auto-sync service for automatic sequence updates.

Provides background polling of Backend registry and automatic
pull of updated sequences.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable, List, Optional

from pydantic import BaseModel, Field

from station_service.models.config import BackendConfig
from station_service.services.sequence_sync import (
    SequenceSyncService,
    PullResult,
    SyncResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Models
# ============================================================================


class AutoSyncConfig(BaseModel):
    """Auto-sync configuration."""

    enabled: bool = Field(False, description="Enable auto-sync")
    poll_interval: int = Field(60, ge=10, le=3600, description="Polling interval in seconds")
    auto_pull: bool = Field(True, description="Automatically pull when updates detected")


class AutoSyncStatus(BaseModel):
    """Current auto-sync status."""

    enabled: bool
    running: bool
    poll_interval: int
    auto_pull: bool
    last_check_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    updates_available: int = 0
    last_error: Optional[str] = None


class AutoSyncEvent(BaseModel):
    """Event emitted when auto-sync detects changes."""

    type: str  # "check", "update_available", "sync_started", "sync_completed", "error"
    timestamp: datetime
    sequences_changed: List[str] = Field(default_factory=list)
    sync_result: Optional[SyncResult] = None
    error: Optional[str] = None


# ============================================================================
# Service
# ============================================================================


class AutoSyncService:
    """
    Background service for automatic sequence synchronization.

    Features:
    - Periodic polling of Backend registry
    - Automatic pull when updates are available
    - WebSocket notifications on changes
    - Configurable poll interval
    """

    def __init__(
        self,
        sync_service: SequenceSyncService,
        config: AutoSyncConfig = None,
        on_event: Optional[Callable[[AutoSyncEvent], None]] = None,
    ):
        """
        Initialize auto-sync service.

        Args:
            sync_service: SequenceSyncService for actual sync operations
            config: Auto-sync configuration
            on_event: Callback for sync events (for WebSocket notifications)
        """
        self._sync_service = sync_service
        self._config = config or AutoSyncConfig()
        self._on_event = on_event

        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_check_at: Optional[datetime] = None
        self._last_sync_at: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._updates_available = 0

    @property
    def status(self) -> AutoSyncStatus:
        """Get current auto-sync status."""
        return AutoSyncStatus(
            enabled=self._config.enabled,
            running=self._running,
            poll_interval=self._config.poll_interval,
            auto_pull=self._config.auto_pull,
            last_check_at=self._last_check_at,
            last_sync_at=self._last_sync_at,
            updates_available=self._updates_available,
            last_error=self._last_error,
        )

    def configure(self, config: AutoSyncConfig) -> None:
        """
        Update auto-sync configuration.

        If enabled state changes, starts or stops the polling task.
        """
        was_enabled = self._config.enabled
        self._config = config

        if config.enabled and not was_enabled:
            self.start()
        elif not config.enabled and was_enabled:
            self.stop()

    def start(self) -> None:
        """Start the auto-sync background task."""
        if self._running:
            return

        self._config.enabled = True
        self._running = True
        self._task = asyncio.create_task(self._polling_loop())
        logger.info(f"Auto-sync started with interval {self._config.poll_interval}s")

    def stop(self) -> None:
        """Stop the auto-sync background task."""
        self._config.enabled = False
        self._running = False

        if self._task:
            self._task.cancel()
            self._task = None

        logger.info("Auto-sync stopped")

    async def check_now(self) -> AutoSyncStatus:
        """Manually trigger an update check."""
        await self._check_for_updates()
        return self.status

    async def sync_now(self) -> SyncResult:
        """Manually trigger a sync operation."""
        return await self._perform_sync()

    def _emit_event(self, event: AutoSyncEvent) -> None:
        """Emit an event to listeners."""
        if self._on_event:
            try:
                self._on_event(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    async def _polling_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                await self._check_for_updates()

                # Auto-pull if enabled and updates available
                if self._config.auto_pull and self._updates_available > 0:
                    await self._perform_sync()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._last_error = str(e)
                logger.error(f"Auto-sync polling error: {e}")
                self._emit_event(AutoSyncEvent(
                    type="error",
                    timestamp=datetime.now(),
                    error=str(e),
                ))

            # Wait for next poll
            try:
                await asyncio.sleep(self._config.poll_interval)
            except asyncio.CancelledError:
                break

    async def _check_for_updates(self) -> None:
        """Check Backend for available updates."""
        self._last_check_at = datetime.now()
        self._last_error = None

        try:
            updates = await self._sync_service.check_updates()

            # Count sequences that need updates
            sequences_with_updates = [
                name for name, info in updates.items()
                if info.get("needs_update", False)
            ]
            self._updates_available = len(sequences_with_updates)

            self._emit_event(AutoSyncEvent(
                type="check" if not sequences_with_updates else "update_available",
                timestamp=datetime.now(),
                sequences_changed=sequences_with_updates,
            ))

            if sequences_with_updates:
                logger.info(f"Auto-sync: {len(sequences_with_updates)} updates available")

        except Exception as e:
            self._last_error = str(e)
            raise

    async def _perform_sync(self) -> SyncResult:
        """Perform sync of all available updates."""
        self._emit_event(AutoSyncEvent(
            type="sync_started",
            timestamp=datetime.now(),
        ))

        try:
            result = await self._sync_service.sync_all()
            self._last_sync_at = datetime.now()
            self._updates_available = 0
            self._last_error = None

            self._emit_event(AutoSyncEvent(
                type="sync_completed",
                timestamp=datetime.now(),
                sync_result=result,
            ))

            logger.info(
                f"Auto-sync completed: {result.sequences_updated} updated, "
                f"{result.sequences_failed} failed"
            )

            return result

        except Exception as e:
            self._last_error = str(e)
            self._emit_event(AutoSyncEvent(
                type="error",
                timestamp=datetime.now(),
                error=str(e),
            ))
            raise


# Global instance
_auto_sync_service: Optional[AutoSyncService] = None


def get_auto_sync_service() -> Optional[AutoSyncService]:
    """Get the global auto-sync service instance."""
    return _auto_sync_service


def set_auto_sync_service(service: AutoSyncService) -> None:
    """Set the global auto-sync service instance."""
    global _auto_sync_service
    _auto_sync_service = service
