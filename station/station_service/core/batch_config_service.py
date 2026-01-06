"""
Batch Configuration Service for Station Service.

Provides orchestration layer for batch configuration management.
Implements Persist-First strategy with rollback mechanism.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from station_service.core.exceptions import (
    BatchAlreadyExistsError,
    BatchNotFoundError,
    BatchPersistenceError,
    BatchValidationError,
)
from station_service.models.config import BatchConfig
from station_service.storage.repositories import BatchConfigRepository

if TYPE_CHECKING:
    from station_service.batch.manager import BatchManager

logger = logging.getLogger(__name__)


class BatchConfigService:
    """
    Service layer for batch configuration management.

    Orchestrates persistence (Repository) and runtime state (BatchManager).
    Implements Persist-First strategy: YAML is saved first, then memory is updated.
    If memory update fails, YAML changes are rolled back.

    Design Principles:
        - Persist-First: YAML is the source of truth
        - Rollback: Memory failures trigger YAML rollback
        - Single Lock: Service-level lock for thread safety
        - Separation: Repository handles data, Service handles logic

    Usage:
        service = BatchConfigService(batch_manager, config_repository)

        # Create batch (persists to YAML + memory)
        batch = await service.create_batch(config)

        # Update batch
        updated = await service.update_batch("batch_id", {"name": "New Name"})

        # Delete batch
        await service.delete_batch("batch_id")
    """

    def __init__(
        self,
        batch_manager: "BatchManager",
        config_repository: BatchConfigRepository,
    ) -> None:
        """
        Initialize service with dependencies.

        Args:
            batch_manager: BatchManager for runtime state management
            config_repository: Repository for YAML persistence
        """
        self._batch_manager = batch_manager
        self._repository = config_repository
        self._operation_lock = asyncio.Lock()

    async def create_batch(self, config: BatchConfig) -> BatchConfig:
        """
        Create a new batch configuration.

        Persist-First Strategy:
        1. Validate configuration
        2. Save to YAML (source of truth)
        3. Add to BatchManager memory
        4. Rollback YAML if memory update fails

        Args:
            config: Batch configuration to create

        Returns:
            Created BatchConfig

        Raises:
            BatchAlreadyExistsError: If batch ID already exists
            BatchValidationError: If configuration is invalid
            BatchPersistenceError: If persistence fails
        """
        async with self._operation_lock:
            # 1. Validate
            self._validate_for_create(config)

            # 2. Persist to YAML first (Source of Truth)
            batch_dict = self._to_yaml_dict(config)
            try:
                await self._repository.create(batch_dict)
            except BatchAlreadyExistsError:
                raise
            except Exception as e:
                raise BatchPersistenceError(config.id, f"Failed to save to YAML: {e}")

            # 3. Update memory (rollback on failure)
            try:
                self._batch_manager.add_batch(config)
            except Exception as e:
                # Rollback: remove from YAML
                logger.warning(
                    f"Memory update failed for batch '{config.id}', rolling back YAML: {e}"
                )
                try:
                    await self._repository.delete(config.id)
                except Exception as rollback_err:
                    logger.error(f"Rollback failed: {rollback_err}")
                raise BatchPersistenceError(config.id, f"Memory update failed: {e}")

            logger.info(f"Created batch '{config.id}' with YAML persistence")
            return config

    async def update_batch(
        self, batch_id: str, updates: Dict[str, Any]
    ) -> BatchConfig:
        """
        Update an existing batch configuration.

        Persist-First Strategy:
        1. Validate batch exists and is not running
        2. Save updates to YAML
        3. Update BatchManager memory

        Args:
            batch_id: ID of the batch to update
            updates: Dictionary of fields to update

        Returns:
            Updated BatchConfig

        Raises:
            BatchNotFoundError: If batch not found
            BatchValidationError: If update is invalid (e.g., batch is running)
            BatchPersistenceError: If persistence fails
        """
        async with self._operation_lock:
            # 1. Get current config from memory
            current = self._batch_manager.get_batch_config(batch_id)
            if not current:
                raise BatchNotFoundError(batch_id)

            # 2. Validate not running
            status = await self._batch_manager.get_batch_status(batch_id)
            if status and status.get("status") in ("running", "paused"):
                raise BatchValidationError(
                    "Cannot update batch while it is running",
                    batch_id=batch_id,
                )

            # 3. Persist to YAML first
            try:
                await self._repository.update(batch_id, updates)
            except BatchNotFoundError:
                # Batch exists in memory but not in YAML (runtime-created)
                # Create it in YAML first
                batch_dict = self._to_yaml_dict(current)
                batch_dict.update(updates)
                await self._repository.create(batch_dict)
            except Exception as e:
                raise BatchPersistenceError(batch_id, f"Failed to update YAML: {e}")

            # 4. Update memory
            try:
                # Dict fields that should be merged instead of replaced
                merge_fields = {"config", "parameters", "hardware"}
                for key, value in updates.items():
                    if hasattr(current, key) and key != "id":
                        # Special handling for dict fields: merge instead of replace
                        if key in merge_fields and isinstance(value, dict):
                            getattr(current, key).update(value)
                        else:
                            setattr(current, key, value)
            except Exception as e:
                logger.error(f"Memory update failed for batch '{batch_id}': {e}")
                # Note: YAML is already updated, but we continue
                # This is acceptable since YAML is the source of truth

            logger.info(f"Updated batch '{batch_id}' with YAML persistence")
            return current

    async def delete_batch(self, batch_id: str) -> None:
        """
        Delete a batch configuration.

        Args:
            batch_id: ID of the batch to delete

        Raises:
            BatchNotFoundError: If batch not found in memory
            BatchValidationError: If batch is running
        """
        async with self._operation_lock:
            # 1. Check exists in memory
            current = self._batch_manager.get_batch_config(batch_id)

            # 2. Validate not running
            if current:
                status = await self._batch_manager.get_batch_status(batch_id)
                if status and status.get("status") in ("running", "paused"):
                    raise BatchValidationError(
                        "Cannot delete batch while it is running",
                        batch_id=batch_id,
                    )

            # 3. Delete from YAML (may not exist if runtime-only)
            try:
                await self._repository.delete(batch_id)
                logger.info(f"Deleted batch '{batch_id}' from YAML")
            except BatchNotFoundError:
                logger.debug(f"Batch '{batch_id}' not in YAML (runtime-only batch)")
            except Exception as e:
                raise BatchPersistenceError(batch_id, f"Failed to delete from YAML: {e}")

            # 4. Delete from memory
            if current:
                self._batch_manager.remove_batch(batch_id)
                logger.info(f"Deleted batch '{batch_id}' from memory")
            elif not await self._repository.exists(batch_id):
                # Neither in memory nor YAML
                raise BatchNotFoundError(batch_id)

    async def get_batch(self, batch_id: str) -> Optional[BatchConfig]:
        """
        Get batch configuration from memory.

        Args:
            batch_id: ID of the batch

        Returns:
            BatchConfig or None if not found
        """
        return self._batch_manager.get_batch_config(batch_id)

    async def sync_from_yaml(self, batch_id: str) -> Optional[BatchConfig]:
        """
        Reload a batch configuration from YAML into memory.

        Useful for hot-reload scenarios.

        Args:
            batch_id: ID of the batch to reload

        Returns:
            Updated BatchConfig or None if not in YAML
        """
        yaml_config = await self._repository.get(batch_id)
        if not yaml_config:
            return None

        config = BatchConfig(
            id=yaml_config.get("id"),
            name=yaml_config.get("name"),
            sequence_package=yaml_config.get("sequence_package"),
            process_id=yaml_config.get("process_id"),
            auto_start=yaml_config.get("auto_start", False),
            hardware=yaml_config.get("hardware", {}),
        )

        # Update or add in memory
        existing = self._batch_manager.get_batch_config(batch_id)
        if existing:
            # Update existing
            for key in ["name", "sequence_package", "process_id", "auto_start", "hardware"]:
                setattr(existing, key, getattr(config, key))
            return existing
        else:
            # Add new
            self._batch_manager.add_batch(config)
            return config

    def _validate_for_create(self, config: BatchConfig) -> None:
        """
        Validate batch configuration for creation.

        Args:
            config: Configuration to validate

        Raises:
            BatchAlreadyExistsError: If batch already exists
            BatchValidationError: If configuration is invalid
        """
        # Check for duplicates in memory
        if self._batch_manager.get_batch_config(config.id):
            raise BatchAlreadyExistsError(config.id)

        # Validate required fields
        if not config.id:
            raise BatchValidationError("Batch ID is required")
        if not config.name:
            raise BatchValidationError("Batch name is required")
        if not config.sequence_package:
            raise BatchValidationError("Sequence package is required")

    def _to_yaml_dict(self, config: BatchConfig) -> Dict[str, Any]:
        """
        Convert BatchConfig to YAML-compatible dictionary.

        Args:
            config: BatchConfig to convert

        Returns:
            Dictionary suitable for YAML serialization
        """
        result = {
            "id": config.id,
            "name": config.name,
            "sequence_package": config.sequence_package,
            "auto_start": config.auto_start,
        }

        # Only include optional fields if set
        if config.process_id is not None:
            result["process_id"] = config.process_id

        if config.hardware:
            result["hardware"] = config.hardware

        if config.parameters:
            result["parameters"] = config.parameters

        if config.config:
            result["config"] = config.config

        return result
