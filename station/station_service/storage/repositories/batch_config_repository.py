"""
Batch Configuration Repository for Station Service.

Provides CRUD operations for batch configurations in station.yaml.
Implements atomic writes with backup support for data integrity.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from station_service.core.exceptions import (
    BatchAlreadyExistsError,
    BatchNotFoundError,
)

logger = logging.getLogger(__name__)


class BatchConfigRepository:
    """
    Repository for batch configuration persistence to YAML.

    Handles all YAML file operations with atomic writes and automatic backups.
    Thread-safe through asyncio.Lock for concurrent access.

    Usage:
        repo = BatchConfigRepository(Path("config/station.yaml"))

        # Create a new batch
        await repo.create({
            "id": "my_batch",
            "name": "My Batch",
            "sequence_package": "my_sequence",
        })

        # Update batch
        await repo.update("my_batch", {"name": "Updated Name"})

        # Delete batch
        await repo.delete("my_batch")

        # Get batch
        batch = await repo.get("my_batch")

        # List all batches
        batches = await repo.get_all()
    """

    def __init__(self, config_path: Path, backup_count: int = 5) -> None:
        """
        Initialize repository with config file path.

        Args:
            config_path: Path to station.yaml configuration file
            backup_count: Number of backup files to keep (default: 5)
        """
        self._config_path = config_path
        self._backup_count = backup_count
        self._file_lock = asyncio.Lock()

    @property
    def config_path(self) -> Path:
        """Get the configuration file path."""
        return self._config_path

    async def create(self, batch_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new batch configuration to YAML.

        Args:
            batch_dict: Batch configuration dict with at least 'id', 'name', 'sequence_package'

        Returns:
            The created batch configuration

        Raises:
            BatchAlreadyExistsError: If batch with same ID already exists
            FileNotFoundError: If config file doesn't exist
        """
        batch_id = batch_dict.get("id")
        if not batch_id:
            raise ValueError("Batch ID is required")

        async with self._file_lock:
            config = self._load_config()

            # Check for duplicates
            existing_ids = [b.get("id") for b in config.get("batches", [])]
            if batch_id in existing_ids:
                raise BatchAlreadyExistsError(batch_id)

            # Add batch
            if "batches" not in config:
                config["batches"] = []
            config["batches"].append(batch_dict)

            # Save with backup
            self._save_config(config)
            logger.info(f"Created batch '{batch_id}' in YAML configuration")

            return batch_dict

    async def update(self, batch_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing batch configuration in YAML.

        Args:
            batch_id: ID of the batch to update
            updates: Dictionary of fields to update

        Returns:
            The updated batch configuration

        Raises:
            BatchNotFoundError: If batch not found
            FileNotFoundError: If config file doesn't exist
        """
        async with self._file_lock:
            config = self._load_config()

            # Find and update batch
            for batch in config.get("batches", []):
                if batch.get("id") == batch_id:
                    # Don't allow changing the ID
                    updates.pop("id", None)
                    # Dict fields that should be merged instead of replaced
                    merge_fields = {"config", "parameters", "hardware"}
                    for field in merge_fields:
                        if field in updates and field in batch and isinstance(batch[field], dict):
                            batch[field].update(updates[field])
                            updates = {k: v for k, v in updates.items() if k != field}
                    batch.update(updates)
                    self._save_config(config)
                    logger.info(f"Updated batch '{batch_id}' in YAML configuration")
                    return batch

            raise BatchNotFoundError(batch_id)

    async def delete(self, batch_id: str) -> None:
        """
        Remove a batch configuration from YAML.

        Args:
            batch_id: ID of the batch to delete

        Raises:
            BatchNotFoundError: If batch not found
            FileNotFoundError: If config file doesn't exist
        """
        async with self._file_lock:
            config = self._load_config()

            original_batches = config.get("batches", [])
            config["batches"] = [b for b in original_batches if b.get("id") != batch_id]

            if len(config["batches"]) == len(original_batches):
                raise BatchNotFoundError(batch_id)

            self._save_config(config)
            logger.info(f"Deleted batch '{batch_id}' from YAML configuration")

    async def get(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a batch configuration by ID.

        Args:
            batch_id: ID of the batch to retrieve

        Returns:
            Batch configuration dict or None if not found
        """
        config = self._load_config()

        for batch in config.get("batches", []):
            if batch.get("id") == batch_id:
                return batch

        return None

    async def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all batch configurations.

        Returns:
            List of batch configuration dicts
        """
        config = self._load_config()
        return config.get("batches", [])

    async def exists(self, batch_id: str) -> bool:
        """
        Check if a batch exists in the configuration.

        Args:
            batch_id: ID of the batch to check

        Returns:
            True if batch exists, False otherwise
        """
        return await self.get(batch_id) is not None

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        if not self._config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self._config_path}")

        with open(self._config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to YAML file with atomic write and backup.

        Args:
            config: Configuration dictionary to save
        """
        # Create backup
        self._create_backup()

        # Atomic write: write to temp file, then rename
        temp_path = self._config_path.with_suffix(".yaml.tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    config,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

            # Atomic replace
            temp_path.replace(self._config_path)

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e

        # Clean up old backups
        self._cleanup_old_backups()

    def _create_backup(self) -> Path:
        """
        Create a timestamped backup of the config file.

        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self._config_path.with_suffix(f".yaml.bak.{timestamp}")
        shutil.copy2(self._config_path, backup_path)
        logger.debug(f"Created config backup: {backup_path}")
        return backup_path

    def _cleanup_old_backups(self) -> int:
        """
        Remove old backup files, keeping only the most recent ones.

        Returns:
            Number of backups deleted
        """
        backup_pattern = self._config_path.stem + ".yaml.bak.*"
        backups = sorted(
            self._config_path.parent.glob(backup_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        deleted = 0
        for backup in backups[self._backup_count:]:
            backup.unlink()
            deleted += 1
            logger.debug(f"Deleted old backup: {backup}")

        if deleted:
            logger.debug(f"Cleaned up {deleted} old config backup(s)")

        return deleted
