"""
Dependency Injection Container for Station Service.

Provides a centralized container for managing service instances and their lifecycles.
Replaces global singletons with properly scoped dependencies.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from station_service.batch.manager import BatchManager
    from station_service.core.events import EventEmitter
    from station_service.ipc.server import IPCServer
    from station_service.models.config import StationConfig
    from station_service_sdk import SequenceLoader
    from station_service.storage.database import Database
    from station_service.sync.engine import SyncEngine

logger = logging.getLogger(__name__)


@dataclass
class ServiceContainer:
    """
    Dependency Injection Container for Station Service.

    Manages the lifecycle of all core services and provides
    proper dependency injection instead of global singletons.

    Usage:
        container = ServiceContainer()
        await container.initialize(config, db_path)

        # Access services
        db = container.database
        events = container.event_emitter
        batch_manager = container.batch_manager

        # Cleanup
        await container.shutdown()

    Context Manager:
        async with ServiceContainer.create(config, db_path) as container:
            # Use container.database, container.batch_manager, etc.
        # Services are automatically cleaned up
    """

    # Core configuration
    config: Optional["StationConfig"] = None

    # Service instances (lazy initialized)
    _database: Optional["Database"] = field(default=None, repr=False)
    _event_emitter: Optional["EventEmitter"] = field(default=None, repr=False)
    _ipc_server: Optional["IPCServer"] = field(default=None, repr=False)
    _batch_manager: Optional["BatchManager"] = field(default=None, repr=False)
    _sync_engine: Optional["SyncEngine"] = field(default=None, repr=False)
    _sequence_loader: Optional["SequenceLoader"] = field(default=None, repr=False)
    _backend_client: Optional[Any] = field(default=None, repr=False)  # BackendClient

    # State tracking
    _initialized: bool = field(default=False, repr=False)
    _db_path: Optional[Path] = field(default=None, repr=False)

    # ============================================================
    # Service Properties
    # ============================================================

    @property
    def database(self) -> "Database":
        """Get the database instance."""
        if self._database is None:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._database

    @property
    def event_emitter(self) -> "EventEmitter":
        """Get the event emitter instance."""
        if self._event_emitter is None:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._event_emitter

    @property
    def ipc_server(self) -> "IPCServer":
        """Get the IPC server instance."""
        if self._ipc_server is None:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._ipc_server

    @property
    def batch_manager(self) -> "BatchManager":
        """Get the batch manager instance."""
        if self._batch_manager is None:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._batch_manager

    @property
    def sync_engine(self) -> Optional["SyncEngine"]:
        """Get the sync engine instance (may be None if not configured)."""
        return self._sync_engine

    @property
    def sequence_loader(self) -> "SequenceLoader":
        """Get the sequence loader instance."""
        if self._sequence_loader is None:
            raise RuntimeError("Container not initialized. Call initialize() first.")
        return self._sequence_loader

    @property
    def backend_client(self) -> Optional[Any]:
        """Get the backend client instance (may be None if not configured)."""
        return self._backend_client

    @backend_client.setter
    def backend_client(self, client: Any) -> None:
        """Set the backend client instance (for external initialization)."""
        self._backend_client = client

    @property
    def is_initialized(self) -> bool:
        """Check if container is initialized."""
        return self._initialized

    # ============================================================
    # Lifecycle Methods
    # ============================================================

    async def initialize(
        self,
        config: "StationConfig",
        db_path: Path,
        sequences_dir: str = "sequences",
    ) -> None:
        """
        Initialize all services in the container.

        Args:
            config: Station configuration
            db_path: Path to SQLite database file
            sequences_dir: Directory containing sequence packages

        Raises:
            RuntimeError: If already initialized
        """
        if self._initialized:
            logger.warning("Container already initialized")
            return

        self.config = config
        self._db_path = db_path

        logger.info("Initializing service container...")

        # Import here to avoid circular imports
        from station_service.batch.manager import BatchManager
        from station_service.core.events import EventEmitter
        from station_service.ipc.server import IPCServer
        from station_service_sdk import SequenceLoader
        from station_service.storage.database import Database
        from station_service.sync.engine import SyncEngine

        # 1. Initialize database
        logger.debug("Initializing database...")
        self._database = await Database.create(db_path)
        await self._database.init_db()

        # 2. Initialize event emitter
        logger.debug("Initializing event emitter...")
        self._event_emitter = EventEmitter()

        # 3. Initialize IPC server
        logger.debug("Initializing IPC server...")
        self._ipc_server = IPCServer(
            router_port=config.ipc.router_port,
            sub_port=config.ipc.sub_port,
        )
        await self._ipc_server.start()

        # 4. Initialize sequence loader
        logger.debug("Initializing sequence loader...")
        self._sequence_loader = SequenceLoader(packages_dir=sequences_dir)

        # 5. Initialize batch manager
        logger.debug("Initializing batch manager...")
        self._batch_manager = BatchManager(
            config=config,
            ipc_server=self._ipc_server,
            event_emitter=self._event_emitter,
        )
        await self._batch_manager.start()

        # 6. Initialize sync engine (optional, based on config)
        if config.backend.url:
            logger.debug("Initializing sync engine...")
            self._sync_engine = SyncEngine(
                config=config.backend,
                database=self._database,
                event_emitter=self._event_emitter,
            )
            await self._sync_engine.start()
        else:
            logger.info("Sync engine disabled (no backend URL configured)")

        self._initialized = True
        logger.info("Service container initialized successfully")

    async def shutdown(self) -> None:
        """
        Shutdown all services gracefully.

        Services are shut down in reverse order of initialization.
        """
        if not self._initialized:
            return

        logger.info("Shutting down service container...")

        # 1. Disconnect backend client
        if self._backend_client:
            try:
                if hasattr(self._backend_client, 'disconnect'):
                    await self._backend_client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting backend client: {e}")

        # 2. Stop sync engine
        if self._sync_engine:
            try:
                await self._sync_engine.stop()
            except Exception as e:
                logger.error(f"Error stopping sync engine: {e}")

        # 3. Stop batch manager
        if self._batch_manager:
            try:
                await self._batch_manager.stop()
            except Exception as e:
                logger.error(f"Error stopping batch manager: {e}")

        # 4. Stop IPC server
        if self._ipc_server:
            try:
                await self._ipc_server.stop()
            except Exception as e:
                logger.error(f"Error stopping IPC server: {e}")

        # 5. Clear event emitter
        if self._event_emitter:
            self._event_emitter.clear()

        # 6. Close database
        if self._database:
            try:
                await self._database.close()
            except Exception as e:
                logger.error(f"Error closing database: {e}")

        # Reset state
        self._database = None
        self._event_emitter = None
        self._ipc_server = None
        self._batch_manager = None
        self._sync_engine = None
        self._sequence_loader = None
        self._backend_client = None
        self._initialized = False

        logger.info("Service container shutdown complete")

    # ============================================================
    # Context Manager Support
    # ============================================================

    async def __aenter__(self) -> "ServiceContainer":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.shutdown()

    @classmethod
    async def create(
        cls,
        config: "StationConfig",
        db_path: Path,
        sequences_dir: str = "sequences",
    ) -> "ServiceContainer":
        """
        Factory method to create and initialize a container.

        Args:
            config: Station configuration
            db_path: Path to SQLite database
            sequences_dir: Directory containing sequences

        Returns:
            Initialized ServiceContainer
        """
        container = cls()
        await container.initialize(config, db_path, sequences_dir)
        return container

    # ============================================================
    # Utility Methods
    # ============================================================

    def get_app_state(self) -> Dict[str, Any]:
        """
        Get all services as a dictionary for FastAPI app.state.

        Returns:
            Dictionary of service instances
        """
        return {
            "config": self.config,
            "database": self._database,
            "batch_manager": self._batch_manager,
            "event_emitter": self._event_emitter,
            "sync_engine": self._sync_engine,
            "sequence_loader": self._sequence_loader,
            "backend_client": self._backend_client,
        }

    def set_sync_engine(self, sync_engine: "SyncEngine") -> None:
        """
        Set the sync engine instance (for external initialization with extra params).

        Args:
            sync_engine: SyncEngine instance to use
        """
        self._sync_engine = sync_engine


# ============================================================
# Global Container Instance (for backward compatibility)
# ============================================================

# This is provided for backward compatibility during migration.
# New code should inject the container or use FastAPI dependencies.
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """
    Get the global container instance.

    Note: This is for backward compatibility. Prefer dependency injection.

    Returns:
        The global ServiceContainer instance

    Raises:
        RuntimeError: If container not initialized
    """
    if _container is None:
        raise RuntimeError("Global container not initialized")
    return _container


def set_container(container: ServiceContainer) -> None:
    """
    Set the global container instance.

    Args:
        container: The container to use globally
    """
    global _container
    _container = container


async def initialize_container(
    config: "StationConfig",
    db_path: Path,
    sequences_dir: str = "sequences",
) -> ServiceContainer:
    """
    Initialize and set the global container.

    Args:
        config: Station configuration
        db_path: Path to SQLite database
        sequences_dir: Directory containing sequences

    Returns:
        Initialized ServiceContainer
    """
    global _container
    _container = await ServiceContainer.create(config, db_path, sequences_dir)
    return _container


async def shutdown_container() -> None:
    """Shutdown the global container."""
    global _container
    if _container:
        await _container.shutdown()
        _container = None
