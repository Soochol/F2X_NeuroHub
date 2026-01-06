"""
Configuration Writer Module.

Provides utilities for updating station.yaml configuration file
with atomic writes and backup support.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from station_service.models.config import BackendConfig, StationConfig, StationInfo, WorkflowConfig

logger = logging.getLogger(__name__)


async def update_batch_sequence(
    config_path: Path,
    batch_id: str,
    sequence_package: str,
) -> StationConfig:
    """
    Update a batch's sequence_package in the station.yaml config file.

    Performs an atomic update with backup to ensure config integrity.

    Args:
        config_path: Path to the station.yaml file
        batch_id: ID of the batch to update
        sequence_package: New sequence package path (e.g., "sequences/pcb_voltage_test")

    Returns:
        Updated StationConfig

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If batch_id is not found
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Read current config
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Find and update the batch
    batch_found = False
    previous_sequence = None

    for batch in config_data.get("batches", []):
        if batch.get("id") == batch_id:
            previous_sequence = batch.get("sequence_package")
            batch["sequence_package"] = sequence_package
            batch_found = True
            break

    if not batch_found:
        raise ValueError(f"Batch '{batch_id}' not found in configuration")

    # Create backup
    backup_path = config_path.with_suffix(f".yaml.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(config_path, backup_path)
    logger.info(f"Created config backup: {backup_path}")

    # Write updated config atomically (write to temp, then rename)
    temp_path = config_path.with_suffix(".yaml.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

        # Atomic replace
        temp_path.replace(config_path)
        logger.info(
            f"Updated batch '{batch_id}' sequence: {previous_sequence} -> {sequence_package}"
        )

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise e

    # Return updated config
    return StationConfig(**config_data)


async def get_deployed_sequence(
    config_path: Path,
    batch_id: str,
) -> Optional[str]:
    """
    Get the currently deployed sequence for a batch.

    Args:
        config_path: Path to the station.yaml file
        batch_id: ID of the batch to query

    Returns:
        Sequence package path or None if not found
    """
    if not config_path.exists():
        return None

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    for batch in config_data.get("batches", []):
        if batch.get("id") == batch_id:
            return batch.get("sequence_package")

    return None


async def list_batches_with_sequences(
    config_path: Path,
) -> list[dict]:
    """
    List all batches and their deployed sequences.

    Args:
        config_path: Path to the station.yaml file

    Returns:
        List of dicts with batch_id, name, and sequence_package
    """
    if not config_path.exists():
        return []

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    batches = []
    for batch in config_data.get("batches", []):
        batches.append({
            "batch_id": batch.get("id"),
            "name": batch.get("name"),
            "sequence_package": batch.get("sequence_package"),
        })

    return batches


async def update_station_info(
    config_path: Path,
    station_info: StationInfo,
) -> StationConfig:
    """
    Update station information (id, name, description) in the station.yaml config file.

    Performs an atomic update with backup to ensure config integrity.

    Args:
        config_path: Path to the station.yaml file
        station_info: New station information

    Returns:
        Updated StationConfig

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Read current config
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Update station info
    previous_info = config_data.get("station", {})
    config_data["station"] = {
        "id": station_info.id,
        "name": station_info.name,
        "description": station_info.description,
    }

    # Create backup
    backup_path = config_path.with_suffix(f".yaml.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(config_path, backup_path)
    logger.info(f"Created config backup: {backup_path}")

    # Write updated config atomically (write to temp, then rename)
    temp_path = config_path.with_suffix(".yaml.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        # Atomic replace
        temp_path.replace(config_path)
        logger.info(
            f"Updated station info: {previous_info} -> {station_info.model_dump()}"
        )

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise e

    # Clean up old backups
    cleanup_old_backups(config_path)

    # Return updated config
    return StationConfig(**config_data)


def cleanup_old_backups(
    config_path: Path,
    keep_count: int = 5,
) -> int:
    """
    Clean up old config backup files, keeping only the most recent ones.

    Args:
        config_path: Path to the station.yaml file
        keep_count: Number of backups to keep

    Returns:
        Number of backups deleted
    """
    backup_pattern = config_path.stem + ".yaml.bak.*"
    backups = sorted(
        config_path.parent.glob(backup_pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    deleted = 0
    for backup in backups[keep_count:]:
        backup.unlink()
        deleted += 1
        logger.debug(f"Deleted old backup: {backup}")

    if deleted:
        logger.info(f"Cleaned up {deleted} old config backup(s)")

    return deleted


async def update_workflow_config(
    config_path: Path,
    workflow_config: WorkflowConfig,
) -> StationConfig:
    """
    Update workflow configuration in the station.yaml config file.

    Performs an atomic update with backup to ensure config integrity.

    Args:
        config_path: Path to the station.yaml file
        workflow_config: New workflow configuration

    Returns:
        Updated StationConfig

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Read current config
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Update workflow config
    previous_workflow = config_data.get("workflow", {})
    config_data["workflow"] = {
        "enabled": workflow_config.enabled,
        "input_mode": workflow_config.input_mode,
        "auto_sequence_start": workflow_config.auto_sequence_start,
        "require_operator_login": workflow_config.require_operator_login,
    }

    # Create backup
    backup_path = config_path.with_suffix(f".yaml.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(config_path, backup_path)
    logger.info(f"Created config backup: {backup_path}")

    # Write updated config atomically (write to temp, then rename)
    temp_path = config_path.with_suffix(".yaml.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        # Atomic replace
        temp_path.replace(config_path)
        logger.info(
            f"Updated workflow config: {previous_workflow} -> {workflow_config.model_dump()}"
        )

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise e

    # Clean up old backups
    cleanup_old_backups(config_path)

    # Return updated config
    return StationConfig(**config_data)


async def update_backend_config(
    config_path: Path,
    backend_config: BackendConfig,
) -> StationConfig:
    """
    Update backend configuration in the station.yaml config file.

    Performs an atomic update with backup to ensure config integrity.
    Note: api_key is preserved from the existing config and cannot be updated via this function.

    Args:
        config_path: Path to the station.yaml file
        backend_config: New backend configuration (api_key is ignored)

    Returns:
        Updated StationConfig

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Read current config
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    # Update backend config (preserve api_key)
    previous_backend = config_data.get("backend", {})
    existing_api_key = previous_backend.get("api_key", "")

    config_data["backend"] = {
        "url": backend_config.url,
        "api_key": existing_api_key,  # Preserve existing API key
        "sync_interval": backend_config.sync_interval,
        "station_id": backend_config.station_id,
        "timeout": backend_config.timeout,
        "max_retries": backend_config.max_retries,
    }

    # Create backup
    backup_path = config_path.with_suffix(f".yaml.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(config_path, backup_path)
    logger.info(f"Created config backup: {backup_path}")

    # Write updated config atomically (write to temp, then rename)
    temp_path = config_path.with_suffix(".yaml.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        # Atomic replace
        temp_path.replace(config_path)
        logger.info(
            f"Updated backend config: url={backend_config.url}, sync_interval={backend_config.sync_interval}"
        )

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise e

    # Clean up old backups
    cleanup_old_backups(config_path)

    # Return updated config
    return StationConfig(**config_data)
