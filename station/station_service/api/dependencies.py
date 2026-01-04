"""
Dependency injection for Station Service API.

Provides FastAPI dependency functions for accessing shared resources
like BatchManager, Database, and EventEmitter.

There are two ways to access services:
1. Via app.state (traditional) - used by existing routes
2. Via ServiceContainer (new) - preferred for new code

Both approaches are supported for backward compatibility.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from fastapi import Depends, HTTPException, Request, status

if TYPE_CHECKING:
    from station_service.batch.manager import BatchManager
    from station_service.core.batch_config_service import BatchConfigService
    from station_service.core.container import ServiceContainer
    from station_service.core.events import EventEmitter
    from station_service.models.config import StationConfig
    from station_service_sdk import SequenceLoader
    from station_service.storage.database import Database
    from station_service.storage.repositories import BatchConfigRepository
    from station_service.sync.backend_client import BackendClient
    from station_service.sync.engine import SyncEngine


# Module-level singleton for BatchConfigRepository (lazily initialized)
_batch_config_repository: Optional["BatchConfigRepository"] = None

# Module-level singleton for BatchConfigService (lazily initialized)
_batch_config_service: Optional["BatchConfigService"] = None


# ============================================================================
# Container-based Dependencies (New - Preferred for new code)
# ============================================================================


def get_container() -> "ServiceContainer":
    """
    Get the global ServiceContainer instance.

    This is the preferred way to access services in new code.
    Falls back to None if container not initialized.

    Returns:
        ServiceContainer instance

    Raises:
        RuntimeError: If container not initialized
    """
    from station_service.core.container import get_container as _get_container
    return _get_container()


def get_container_or_none() -> Optional["ServiceContainer"]:
    """
    Get the global ServiceContainer instance or None if not initialized.

    Returns:
        ServiceContainer instance or None
    """
    try:
        from station_service.core.container import get_container as _get_container
        return _get_container()
    except RuntimeError:
        return None


# ============================================================================
# App State Dependencies (Traditional - For backward compatibility)
# ============================================================================


def get_config(request: Request) -> "StationConfig":
    """
    Get the station configuration from app state.

    Args:
        request: FastAPI request object

    Returns:
        StationConfig instance

    Raises:
        HTTPException: 503 if config not available
    """
    config = getattr(request.app.state, "config", None)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not fully initialized",
        )
    return config


def get_database(request: Request) -> "Database":
    """
    Get the database instance from app state.

    Args:
        request: FastAPI request object

    Returns:
        Database instance

    Raises:
        HTTPException: 503 if database not available
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized",
        )
    return database


def get_batch_manager(request: Request) -> "BatchManager":
    """
    Get the BatchManager from app state.

    Args:
        request: FastAPI request object

    Returns:
        BatchManager instance

    Raises:
        HTTPException: 503 if BatchManager not available
    """
    batch_manager = getattr(request.app.state, "batch_manager", None)
    if batch_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Batch manager not initialized",
        )
    return batch_manager


def get_event_emitter(request: Request) -> "EventEmitter":
    """
    Get the EventEmitter from app state.

    Args:
        request: FastAPI request object

    Returns:
        EventEmitter instance

    Raises:
        HTTPException: 503 if EventEmitter not available
    """
    event_emitter = getattr(request.app.state, "event_emitter", None)
    if event_emitter is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event emitter not initialized",
        )
    return event_emitter


def get_sync_engine(request: Request) -> "SyncEngine":
    """
    Get the SyncEngine from app state.

    Args:
        request: FastAPI request object

    Returns:
        SyncEngine instance

    Raises:
        HTTPException: 503 if SyncEngine not available
    """
    sync_engine = getattr(request.app.state, "sync_engine", None)
    if sync_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sync engine not initialized",
        )
    return sync_engine


def get_backend_client(request: Request) -> "BackendClient":
    """
    Get the BackendClient from app state.

    Args:
        request: FastAPI request object

    Returns:
        BackendClient instance

    Raises:
        HTTPException: 503 if BackendClient not available
    """
    backend_client = getattr(request.app.state, "backend_client", None)
    if backend_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Backend client not initialized",
        )
    return backend_client


def get_sequence_loader(request: Request) -> "SequenceLoader":
    """
    Get the SequenceLoader from app state.

    Args:
        request: FastAPI request object

    Returns:
        SequenceLoader instance

    Raises:
        HTTPException: 503 if SequenceLoader not available
    """
    sequence_loader = getattr(request.app.state, "sequence_loader", None)
    if sequence_loader is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sequence loader not initialized",
        )
    return sequence_loader


def get_config_path() -> Path:
    """
    Get the path to the station config file.

    Returns:
        Path to station.yaml config file
    """
    config_path = os.environ.get("STATION_CONFIG", "config/station.yaml")
    path = Path(config_path)

    if not path.exists():
        # Try relative to module
        module_path = Path(__file__).parent.parent / config_path
        if module_path.exists():
            path = module_path

    return path


def get_batch_config_repository(
    request: Request,
) -> "BatchConfigRepository":
    """
    Get or create the BatchConfigRepository singleton.

    Uses lazy initialization to create the repository on first access.

    Args:
        request: FastAPI request object (used to access config path)

    Returns:
        BatchConfigRepository instance

    Raises:
        HTTPException: 503 if config path cannot be determined
    """
    global _batch_config_repository

    if _batch_config_repository is None:
        from station_service.storage.repositories import BatchConfigRepository

        config_path = get_config_path()
        if not config_path.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Config file not found: {config_path}",
            )
        _batch_config_repository = BatchConfigRepository(config_path)

    return _batch_config_repository


def get_batch_config_service(
    request: Request,
    batch_manager: "BatchManager" = Depends(get_batch_manager),
    config_repository: "BatchConfigRepository" = Depends(get_batch_config_repository),
) -> "BatchConfigService":
    """
    Get or create the BatchConfigService singleton.

    Uses lazy initialization to create the service on first access.

    Args:
        request: FastAPI request object
        batch_manager: BatchManager dependency
        config_repository: BatchConfigRepository dependency

    Returns:
        BatchConfigService instance
    """
    global _batch_config_service

    if _batch_config_service is None:
        from station_service.core.batch_config_service import BatchConfigService

        _batch_config_service = BatchConfigService(
            batch_manager=batch_manager,
            config_repository=config_repository,
        )

    return _batch_config_service


def reset_batch_config_singletons() -> None:
    """
    Reset the batch config singletons.

    Useful for testing or when the config file changes.
    """
    global _batch_config_repository, _batch_config_service
    _batch_config_repository = None
    _batch_config_service = None
