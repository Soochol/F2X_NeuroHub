"""
Dependency injection for Station Service API.

Provides FastAPI dependency functions for accessing shared resources
like BatchManager, Database, and EventEmitter.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, Request, status

if TYPE_CHECKING:
    from station_service.batch.manager import BatchManager
    from station_service.core.events import EventEmitter
    from station_service.models.config import StationConfig
    from station_service.sequence.loader import SequenceLoader
    from station_service.storage.database import Database
    from station_service.sync.engine import SyncEngine


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
