"""
BatchManager for Station Service.

Manages the lifecycle of batch processes including creation, monitoring,
and termination. Integrates with IPC for communication with worker processes.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional

from station_service.core.events import Event, EventEmitter, EventType, get_event_emitter
from station_service.core.exceptions import (
    BatchAlreadyRunningError,
    BatchError,
    BatchNotFoundError,
    BatchNotRunningError,
)
from station_service.ipc import IPCServer, IPCEvent, CommandType
from station_service.models.batch import BatchStatus
from station_service.models.config import BatchConfig, StationConfig
from station_service.batch.process import BatchProcess

logger = logging.getLogger(__name__)


class BatchManager:
    """
    Manages batch processes for Station Service.

    Handles batch lifecycle including:
    - Starting/stopping batch processes
    - Monitoring batch health
    - Routing commands to batches
    - Forwarding events from batches

    Usage:
        config = StationConfig.from_yaml("station.yaml")
        manager = BatchManager(config)
        await manager.start()

        # Start a specific batch
        await manager.start_batch("batch_1")

        # Send command to batch
        response = await manager.send_command("batch_1", CommandType.GET_STATUS)

        await manager.stop()
    """

    def __init__(
        self,
        config: StationConfig,
        ipc_server: Optional[IPCServer] = None,
        event_emitter: Optional[EventEmitter] = None,
    ) -> None:
        """
        Initialize the BatchManager.

        Args:
            config: Station configuration
            ipc_server: Optional IPC server (created if not provided)
            event_emitter: Optional event emitter (uses global if not provided)
        """
        self._config = config
        self._batch_configs: Dict[str, BatchConfig] = {
            batch.id: batch for batch in config.batches
        }

        self._ipc_server = ipc_server
        self._owns_ipc_server = ipc_server is None

        self._event_emitter = event_emitter or get_event_emitter()
        self._batches: Dict[str, BatchProcess] = {}

        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None

    @property
    def is_running(self) -> bool:
        """Check if the manager is running."""
        return self._running

    @property
    def batch_ids(self) -> List[str]:
        """Get list of configured batch IDs."""
        return list(self._batch_configs.keys())

    def get_batch_config(self, batch_id: str) -> Optional[BatchConfig]:
        """Get configuration for a specific batch."""
        return self._batch_configs.get(batch_id)

    def add_batch(self, config: BatchConfig) -> None:
        """
        Add a new batch configuration at runtime.

        Args:
            config: Batch configuration to add

        Raises:
            BatchError: If batch ID already exists
        """
        if config.id in self._batch_configs:
            raise BatchError(f"Batch '{config.id}' already exists")

        self._batch_configs[config.id] = config
        logger.info(f"Added batch configuration: {config.id}")

    def remove_batch(self, batch_id: str) -> bool:
        """
        Remove a batch configuration at runtime.

        Args:
            batch_id: The batch ID to remove

        Returns:
            True if batch was removed

        Raises:
            BatchNotFoundError: If batch ID not found
            BatchAlreadyRunningError: If batch is currently running
        """
        if batch_id not in self._batch_configs:
            raise BatchNotFoundError(batch_id)

        if batch_id in self._batches:
            raise BatchAlreadyRunningError(
                f"Cannot remove batch '{batch_id}' while it is running. Stop it first."
            )

        del self._batch_configs[batch_id]
        logger.info(f"Removed batch configuration: {batch_id}")
        return True

    @property
    def running_batch_ids(self) -> List[str]:
        """Get list of currently running batch IDs."""
        return list(self._batches.keys())

    async def start(self) -> None:
        """
        Start the BatchManager.

        Initializes IPC server and starts auto_start batches.
        """
        if self._running:
            logger.warning("BatchManager already running")
            return

        # Create IPC server if not provided
        if self._ipc_server is None:
            self._ipc_server = IPCServer()

        # Start IPC server
        if self._owns_ipc_server:
            await self._ipc_server.start()

        # Register event handler
        self._ipc_server.on_event(self._handle_ipc_event)

        self._running = True

        # Start monitor task
        self._monitor_task = asyncio.create_task(self._monitor_loop())

        # Start auto_start batches
        for batch_config in self._config.batches:
            if batch_config.auto_start:
                try:
                    await self.start_batch(batch_config.id)
                except Exception as e:
                    logger.error(f"Failed to auto-start batch {batch_config.id}: {e}")

        logger.info(
            f"BatchManager started with {len(self._config.batches)} configured batches"
        )

    async def stop(self) -> None:
        """
        Stop the BatchManager.

        Stops all running batches and shuts down IPC server.
        """
        if not self._running:
            return

        self._running = False

        # Cancel monitor task
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

        # Stop all running batches
        for batch_id in list(self._batches.keys()):
            try:
                await self.stop_batch(batch_id)
            except Exception as e:
                logger.error(f"Error stopping batch {batch_id}: {e}")

        # Stop IPC server if we own it
        if self._owns_ipc_server and self._ipc_server:
            await self._ipc_server.stop()

        logger.info("BatchManager stopped")

    async def start_batch(self, batch_id: str) -> BatchProcess:
        """
        Start a batch process.

        Args:
            batch_id: The batch ID to start

        Returns:
            The started BatchProcess

        Raises:
            BatchNotFoundError: If batch ID not in config
            BatchAlreadyRunningError: If batch is already running
        """
        # Validate batch exists in config
        if batch_id not in self._batch_configs:
            raise BatchNotFoundError(batch_id)

        # Check if already running
        if batch_id in self._batches:
            raise BatchAlreadyRunningError(batch_id)

        batch_config = self._batch_configs[batch_id]

        # Create batch process
        batch = BatchProcess(
            batch_id=batch_id,
            config=batch_config,
            ipc_router_address=self._ipc_server.router_address,
            ipc_sub_address=self._ipc_server.sub_address,
        )

        # Start the process
        await batch.start()

        self._batches[batch_id] = batch

        # Emit event
        await self._event_emitter.emit(Event(
            type=EventType.BATCH_STARTED,
            batch_id=batch_id,
            data={"pid": batch.pid},
        ))

        logger.info(f"Batch {batch_id} started (PID: {batch.pid})")

        return batch

    async def stop_batch(self, batch_id: str, timeout: float = 5.0) -> bool:
        """
        Stop a batch process.

        Args:
            batch_id: The batch ID to stop
            timeout: Timeout for graceful shutdown

        Returns:
            True if batch was stopped

        Raises:
            BatchNotRunningError: If batch is not running
        """
        if batch_id not in self._batches:
            raise BatchNotRunningError(batch_id)

        batch = self._batches[batch_id]

        # Request graceful shutdown via IPC
        try:
            if self._ipc_server.is_worker_connected(batch_id):
                await self._ipc_server.send_command(
                    batch_id,
                    CommandType.SHUTDOWN,
                    timeout=timeout * 1000,
                )
        except Exception as e:
            logger.warning(f"Error sending shutdown command to {batch_id}: {e}")

        # Stop the process
        await batch.stop(timeout=timeout)

        del self._batches[batch_id]

        # Unregister from IPC
        self._ipc_server.unregister_worker(batch_id)

        # Emit event
        await self._event_emitter.emit(Event(
            type=EventType.BATCH_STOPPED,
            batch_id=batch_id,
        ))

        logger.info(f"Batch {batch_id} stopped")

        return True

    async def restart_batch(self, batch_id: str) -> BatchProcess:
        """
        Restart a batch process.

        Args:
            batch_id: The batch ID to restart

        Returns:
            The restarted BatchProcess
        """
        if batch_id in self._batches:
            await self.stop_batch(batch_id)

        return await self.start_batch(batch_id)

    async def send_command(
        self,
        batch_id: str,
        command_type: CommandType,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5000,
    ) -> Dict[str, Any]:
        """
        Send a command to a batch worker.

        Args:
            batch_id: The batch ID to send to
            command_type: The command type
            params: Command parameters
            timeout: Timeout in milliseconds

        Returns:
            Command response data

        Raises:
            BatchNotRunningError: If batch is not running
        """
        if batch_id not in self._batches:
            raise BatchNotRunningError(batch_id)

        response = await self._ipc_server.send_command(
            batch_id,
            command_type,
            params=params,
            timeout=timeout,
        )

        if response.status == "error":
            raise BatchError(response.error or "Unknown error")

        return response.data or {}

    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get the status of a batch.

        Args:
            batch_id: The batch ID

        Returns:
            Batch status dictionary
        """
        # Get config
        if batch_id not in self._batch_configs:
            raise BatchNotFoundError(batch_id)

        config = self._batch_configs[batch_id]
        is_running = batch_id in self._batches

        status = {
            "id": batch_id,
            "name": config.name,
            "status": BatchStatus.RUNNING.value if is_running else BatchStatus.IDLE.value,
            "sequence_package": config.sequence_package,
            "auto_start": config.auto_start,
            "pid": self._batches[batch_id].pid if is_running else None,
        }

        # Get detailed status from worker if running
        if is_running and self._ipc_server.is_worker_connected(batch_id):
            try:
                response = await self._ipc_server.send_command(
                    batch_id,
                    CommandType.GET_STATUS,
                    timeout=2000,
                )
                if response.status == "ok" and response.data:
                    status.update(response.data)
            except Exception as e:
                logger.warning(f"Failed to get detailed status for {batch_id}: {e}")

        return status

    async def get_all_batch_statuses(self) -> List[Dict[str, Any]]:
        """
        Get status of all configured batches.

        Returns:
            List of batch status dictionaries
        """
        statuses = []
        for batch_id in self._batch_configs:
            try:
                status = await self.get_batch_status(batch_id)
                statuses.append(status)
            except Exception as e:
                logger.error(f"Error getting status for {batch_id}: {e}")
                statuses.append({
                    "id": batch_id,
                    "name": self._batch_configs[batch_id].name,
                    "status": "error",
                    "error": str(e),
                })
        return statuses

    async def start_sequence(
        self,
        batch_id: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start sequence execution on a batch.

        Args:
            batch_id: The batch ID
            parameters: Sequence parameters

        Returns:
            Execution ID

        Raises:
            BatchNotRunningError: If batch is not running
        """
        response = await self.send_command(
            batch_id,
            CommandType.START_SEQUENCE,
            params={"parameters": parameters or {}},
        )
        return response.get("execution_id", "")

    async def stop_sequence(self, batch_id: str) -> bool:
        """
        Stop sequence execution on a batch.

        Args:
            batch_id: The batch ID

        Returns:
            True if sequence was stopped
        """
        await self.send_command(batch_id, CommandType.STOP_SEQUENCE)
        return True

    async def manual_control(
        self,
        batch_id: str,
        hardware: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute manual control command on a batch.

        Args:
            batch_id: The batch ID
            hardware: Hardware identifier
            command: Command name
            params: Command parameters

        Returns:
            Command result
        """
        return await self.send_command(
            batch_id,
            CommandType.MANUAL_CONTROL,
            params={
                "hardware": hardware,
                "command": command,
                "params": params or {},
            },
        )

    async def get_all_batch_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get execution statistics for all batches.

        Returns:
            Dictionary mapping batch IDs to their statistics.
        """
        statistics: Dict[str, Dict[str, Any]] = {}

        for batch_id in self._batch_configs:
            # Default statistics
            stats = {
                "total": 0,
                "pass": 0,
                "fail": 0,
                "passRate": 0.0,
            }

            # Try to get stats from running worker
            if batch_id in self._batches and self._ipc_server.is_worker_connected(batch_id):
                try:
                    response = await self._ipc_server.send_command(
                        batch_id,
                        CommandType.GET_STATUS,
                        params={"include_statistics": True},
                        timeout=2000,
                    )
                    if response.status == "ok" and response.data:
                        worker_stats = response.data.get("statistics", {})
                        if worker_stats:
                            stats.update(worker_stats)
                except Exception as e:
                    logger.warning(f"Failed to get statistics for {batch_id}: {e}")

            statistics[batch_id] = stats

        return statistics

    async def get_hardware_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get hardware status for a batch.

        Args:
            batch_id: The batch ID

        Returns:
            Hardware status dictionary mapping hardware names to their status

        Raises:
            BatchNotFoundError: If batch ID not in config
        """
        if batch_id not in self._batch_configs:
            raise BatchNotFoundError(batch_id)

        config = self._batch_configs[batch_id]
        hardware_status: Dict[str, Any] = {}

        # Get hardware configuration from batch config
        for hw_name, hw_config in config.hardware.items():
            hardware_status[hw_name] = {
                "name": hw_name,
                "type": hw_config.get("type", "unknown"),
                "configured": True,
                "connected": False,
                "status": "unknown",
                "details": {},
            }

        # If batch is running, get actual status from worker
        if batch_id in self._batches and self._ipc_server.is_worker_connected(batch_id):
            try:
                response = await self._ipc_server.send_command(
                    batch_id,
                    CommandType.GET_STATUS,
                    params={"include_hardware": True},
                    timeout=2000,
                )
                if response.status == "ok" and response.data:
                    worker_hw_status = response.data.get("hardware", {})
                    for hw_name, hw_data in worker_hw_status.items():
                        if hw_name in hardware_status:
                            hardware_status[hw_name].update({
                                "connected": hw_data.get("connected", False),
                                "status": hw_data.get("status", "unknown"),
                                "details": hw_data.get("details", {}),
                            })
            except Exception as e:
                logger.warning(f"Failed to get hardware status for {batch_id}: {e}")

        return hardware_status

    async def _handle_ipc_event(self, event: IPCEvent) -> None:
        """Handle IPC events from workers."""
        # Forward to event emitter for WebSocket broadcasting
        event_type_map = {
            "STEP_START": EventType.STEP_STARTED,
            "STEP_COMPLETE": EventType.STEP_COMPLETED,
            "SEQUENCE_COMPLETE": EventType.SEQUENCE_COMPLETED,
            "LOG": EventType.LOG,
            "ERROR": EventType.ERROR,
        }

        mapped_type = event_type_map.get(event.type.value)
        if mapped_type:
            await self._event_emitter.emit(Event(
                type=mapped_type,
                batch_id=event.batch_id,
                data=event.data,
            ))

    async def _monitor_loop(self) -> None:
        """Background task to monitor batch processes."""
        logger.debug("Batch monitor loop started")

        while self._running:
            try:
                await asyncio.sleep(1)

                for batch_id, batch in list(self._batches.items()):
                    if not batch.is_alive:
                        # Process died unexpectedly
                        logger.error(f"Batch {batch_id} process died unexpectedly")

                        # Clean up
                        del self._batches[batch_id]
                        self._ipc_server.unregister_worker(batch_id)

                        # Emit crash event
                        await self._event_emitter.emit(Event(
                            type=EventType.BATCH_CRASHED,
                            batch_id=batch_id,
                            data={"exit_code": batch.exit_code},
                        ))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

        logger.debug("Batch monitor loop stopped")
