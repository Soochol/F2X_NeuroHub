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
    IPCTimeoutError,
)
from station_service.ipc import IPCServer, IPCEvent, CommandType
from station_service.models.batch import BatchStatus
from station_service.models.config import BatchConfig, StationConfig
from station_service.batch.process import BatchProcess
from station_service.storage.database import Database
from station_service.storage.repositories.execution_repository import ExecutionRepository
from station_service_sdk import SequenceLoader

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
        self._sequence_loader = SequenceLoader("sequences")

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

        # Auto-load hardware from manifest if not explicitly provided
        if not batch_config.hardware and batch_config.sequence_package:
            manifest_hardware = await self._load_hardware_from_manifest(
                batch_config.sequence_package
            )
            if manifest_hardware:
                # Update config with hardware from manifest
                batch_config = batch_config.model_copy(update={"hardware": manifest_hardware})
                # Store updated config for future reference
                self._batch_configs[batch_id] = batch_config

        # Create batch process with backend and workflow configs for 착공/완공 integration
        batch = BatchProcess(
            batch_id=batch_id,
            config=batch_config,
            ipc_router_address=self._ipc_server.router_address,
            ipc_sub_address=self._ipc_server.sub_address,
            backend_config=self._config.backend,
            workflow_config=self._config.workflow,
        )

        # Start the process
        await batch.start()

        self._batches[batch_id] = batch

        # Wait for worker to be ready for commands
        try:
            await self._ipc_server.wait_for_worker(batch_id, timeout=10.0)
        except IPCTimeoutError:
            # Cleanup on failure
            logger.error(f"Batch {batch_id} worker failed to connect within timeout")
            del self._batches[batch_id]
            await batch.stop()
            raise BatchError(f"Batch '{batch_id}' worker failed to initialize within timeout")

        # Emit event (only after worker is ready)
        await self._event_emitter.emit(Event(
            type=EventType.BATCH_STARTED,
            batch_id=batch_id,
            data={"pid": batch.pid},
        ))

        logger.info(f"Batch {batch_id} started and ready (PID: {batch.pid})")

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
            "parameters": config.parameters,
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

        Always reads from DB for reliable statistics.
        Worker in-memory stats are not reliable (reset on startup).

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
                "avgDuration": 0.0,
                "lastDuration": 0.0,
            }

            # Always read from database for reliable statistics
            # Worker in-memory stats reset on every startup, so they're not reliable
            db_stats = await self._get_batch_statistics_from_db(batch_id)
            if db_stats:
                stats.update(db_stats)

            statistics[batch_id] = stats

        return statistics

    async def _get_batch_statistics_from_db(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution statistics from the batch's database file.

        Args:
            batch_id: The batch ID

        Returns:
            Statistics dictionary or None if not available
        """
        db_path = f"data/batch_{batch_id}.db"
        db = None

        try:
            import os
            if not os.path.exists(db_path):
                return None

            # Use Database.create() factory method
            db = await Database.create(db_path=db_path)

            # Query execution results for this batch (including duration)
            rows = await db.fetch_all(
                """
                SELECT overall_pass, duration FROM execution_results
                WHERE batch_id = ?
                ORDER BY completed_at DESC
                """,
                (batch_id,),
            )

            if not rows:
                return None

            total = len(rows)
            # SQLite stores boolean as INTEGER (1/0), so use truthy check
            passed = sum(1 for r in rows if r.get("overall_pass"))
            failed = total - passed
            pass_rate = passed / total if total > 0 else 0.0

            # Calculate average duration (only from rows with valid duration)
            durations = [r.get("duration") for r in rows if r.get("duration") is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0.0

            # Get last duration (most recent execution)
            last_duration = rows[0].get("duration") if rows and rows[0].get("duration") is not None else 0.0

            return {
                "total": total,
                "pass": passed,
                "fail": failed,
                "passRate": pass_rate,
                "avgDuration": round(avg_duration, 2),
                "lastDuration": round(last_duration, 2),
            }

        except Exception as e:
            logger.debug(f"Could not read statistics from DB for {batch_id}: {e}")
            return None

        finally:
            if db:
                try:
                    await db.close()
                except Exception:
                    pass

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
        logger.info(f"[BatchManager] Received IPC event: {event.type.value} from batch {event.batch_id}")

        # Forward to event emitter for WebSocket broadcasting
        event_type_map = {
            "STEP_START": EventType.STEP_STARTED,
            "STEP_COMPLETE": EventType.STEP_COMPLETED,
            "SEQUENCE_COMPLETE": EventType.SEQUENCE_COMPLETED,
            "STATUS_UPDATE": EventType.BATCH_STATUS_CHANGED,
            "LOG": EventType.LOG,
            "ERROR": EventType.ERROR,
        }

        mapped_type = event_type_map.get(event.type.value)
        if mapped_type:
            logger.info(f"[BatchManager] Forwarding to EventEmitter: {mapped_type.value}")
            await self._event_emitter.emit(Event(
                type=mapped_type,
                batch_id=event.batch_id,
                data=event.data,
            ))

    async def _load_hardware_from_manifest(
        self,
        sequence_package: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Load hardware configuration from sequence manifest.

        This enables automatic hardware discovery when creating batches,
        so API callers don't need to explicitly provide hardware config.

        Args:
            sequence_package: Name of the sequence package (folder or manifest name)

        Returns:
            Hardware configuration dict suitable for BatchConfig.hardware,
            or empty dict if not found/error.
        """
        try:
            manifest = await self._sequence_loader.load_package(sequence_package)
            if manifest and manifest.hardware:
                hardware_config: Dict[str, Dict[str, Any]] = {}
                for hw_id, hw_def in manifest.hardware.items():
                    hardware_config[hw_id] = {
                        "type": hw_def.driver,
                        "driver": hw_def.class_name,
                        "config": {},
                        "display_name": hw_def.display_name,
                        "description": hw_def.description,
                    }
                    # Include config schema if available
                    if hw_def.config_schema:
                        hardware_config[hw_id]["config_schema"] = {
                            k: v.model_dump() for k, v in hw_def.config_schema.items()
                        }
                logger.info(
                    f"Loaded {len(hardware_config)} hardware devices from manifest '{sequence_package}': "
                    f"{list(hardware_config.keys())}"
                )
                return hardware_config
        except Exception as e:
            logger.warning(f"Failed to load hardware from manifest '{sequence_package}': {e}")

        return {}

    async def get_driver_instance(self, batch_id: str, hardware_id: str) -> Any:
        """
        Get a driver instance from a running batch.

        Args:
            batch_id: The batch ID
            hardware_id: The hardware device ID

        Returns:
            The driver instance if found, None otherwise

        Raises:
            BatchNotFoundError: If batch ID not in config
            BatchNotRunningError: If batch is not running
        """
        if batch_id not in self._batch_configs:
            raise BatchNotFoundError(batch_id)

        if batch_id not in self._batches:
            raise BatchNotRunningError(batch_id)

        # Send command to worker to get driver info
        try:
            response = await self._ipc_server.send_command(
                batch_id,
                CommandType.GET_STATUS,
                params={"include_drivers": True},
                timeout=2000,
            )
            if response.status == "ok" and response.data:
                drivers = response.data.get("drivers", {})
                if hardware_id in drivers:
                    # For introspection, we need to recreate driver instance
                    # since we can't send the actual driver across processes
                    driver_info = drivers[hardware_id]
                    return self._create_driver_for_introspection(hardware_id, driver_info)
        except Exception as e:
            logger.warning(f"Failed to get driver instance for {batch_id}/{hardware_id}: {e}")

        # Fallback: Try to create driver instance from config for introspection
        config = self._batch_configs[batch_id]
        if hardware_id in config.hardware:
            # Resolve sequence folder name from sequence_package (manifest name)
            folder_name = None
            if config.sequence_package:
                try:
                    package_path = self._sequence_loader.get_package_path(config.sequence_package)
                    folder_name = package_path.name  # e.g., "manual_test"
                    logger.debug(f"Resolved sequence folder: {folder_name} for {config.sequence_package}")
                except Exception as e:
                    logger.debug(f"Could not resolve folder name for {config.sequence_package}: {e}")

            return self._create_driver_for_introspection(
                hardware_id,
                config.hardware[hardware_id],
                sequence_folder=folder_name,
            )

        return None

    def _create_driver_for_introspection(
        self, hardware_id: str, hw_config: Dict[str, Any], sequence_folder: str = None
    ) -> Any:
        """
        Create a driver instance for introspection purposes.

        This creates a mock/real driver based on the hardware configuration
        so we can introspect its methods.

        Args:
            hardware_id: ID of the hardware device
            hw_config: Hardware configuration dict with "driver" and "class" keys
            sequence_folder: Actual folder name of the sequence package (not manifest name)
        """
        import importlib

        # Get driver class info from config
        # Note: In loaded hardware config from manifest:
        #   "type" = module name (e.g., "mock_power_supply")
        #   "driver" = class name (e.g., "MockPowerSupply")
        driver_module = hw_config.get("type", "")  # e.g., "mock_power_supply"
        driver_class_name = hw_config.get("driver", "")  # e.g., "MockPowerSupply"

        if not driver_module or not driver_class_name:
            logger.warning(f"Missing type or driver in config for {hardware_id}: {hw_config}")
            return None

        # Build dynamic import paths
        possible_paths = []

        # 1순위: sequence_folder가 제공되면 해당 시퀀스의 drivers 디렉토리
        if sequence_folder:
            possible_paths.append(
                f"sequences.{sequence_folder}.drivers.{driver_module}"
            )

        # 2순위: 기존 fallback 경로들 (하위 호환)
        possible_paths.extend([
            f"sequences.{driver_module}",
            f"sequences.pcb_voltage_test.drivers.{driver_module}",
            f"sequences.sensor_inspection.drivers.{driver_module}",
            f"sequences.manual_test.drivers.{driver_module}",
        ])

        for module_path in possible_paths:
            try:
                module = importlib.import_module(module_path)
                driver_class = getattr(module, driver_class_name, None)
                if driver_class:
                    logger.debug(f"Found driver {driver_class_name} at {module_path}")
                    return driver_class(name=hardware_id, config=hw_config.get("config", {}))
            except (ImportError, AttributeError) as e:
                logger.debug(f"Driver not found at {module_path}: {e}")
                continue

        # Fallback: Try type-based drivers
        try:
            if "multimeter" in hardware_id.lower():
                from sequences.pcb_voltage_test.drivers.mock_multimeter import MockMultimeter
                return MockMultimeter(name=hardware_id, config=hw_config)

            if "sensor" in hardware_id.lower():
                from sequences.sensor_inspection.drivers.mock_sensor import MockSensorInterface
                return MockSensorInterface(name=hardware_id, config=hw_config)
        except Exception as e:
            logger.debug(f"Type-based driver fallback failed: {e}")

        logger.warning(f"Could not find driver {driver_class_name} for {hardware_id} in any path")
        return None

    async def get_manual_steps(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Get sequence steps for manual execution.

        Args:
            batch_id: The batch ID

        Returns:
            List of step information dictionaries
        """
        if batch_id not in self._batch_configs:
            raise BatchNotFoundError(batch_id)

        config = self._batch_configs[batch_id]

        # Try to load sequence metadata
        try:
            from station_service_sdk import SequenceLoader, collect_steps

            loader = SequenceLoader("sequences")
            manifest = await loader.load_package(config.sequence_package)
            package_path = loader.get_package_path(config.sequence_package)
            sequence_class = await loader.load_sequence_class(manifest, package_path)

            step_infos = collect_steps(sequence_class, manifest)

            steps = []
            for method_name, _, step_meta in step_infos:
                step_name = step_meta.name or method_name
                steps.append({
                    "name": step_name,
                    "displayName": step_name.replace("_", " ").title(),
                    "order": step_meta.order,
                    "timeout": step_meta.timeout,
                    "cleanup": step_meta.cleanup,
                    "status": "pending",
                })

            return steps

        except Exception as e:
            logger.warning(f"Could not load steps for {batch_id}: {e}")
            return []

    async def run_manual_step(
        self,
        batch_id: str,
        step_name: str,
        parameter_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a single step manually.

        Args:
            batch_id: The batch ID
            step_name: The step name to execute
            parameter_overrides: Optional parameter overrides

        Returns:
            Step execution result
        """
        if batch_id not in self._batches:
            raise BatchNotRunningError(batch_id)

        # Send command to run specific step
        return await self.send_command(
            batch_id,
            CommandType.MANUAL_CONTROL,
            params={
                "hardware": "_sequence",
                "command": "run_step",
                "params": {
                    "step_name": step_name,
                    "parameters": parameter_overrides or {},
                },
            },
        )

    async def skip_manual_step(
        self, batch_id: str, step_name: str
    ) -> Dict[str, Any]:
        """
        Skip a step in manual mode.

        Args:
            batch_id: The batch ID
            step_name: The step name to skip

        Returns:
            Skip result
        """
        if batch_id not in self._batches:
            raise BatchNotRunningError(batch_id)

        return await self.send_command(
            batch_id,
            CommandType.MANUAL_CONTROL,
            params={
                "hardware": "_sequence",
                "command": "skip_step",
                "params": {"step_name": step_name},
            },
        )

    async def reset_manual_sequence(self, batch_id: str) -> None:
        """
        Reset manual sequence execution state.

        Args:
            batch_id: The batch ID
        """
        if batch_id not in self._batches:
            raise BatchNotRunningError(batch_id)

        await self.send_command(
            batch_id,
            CommandType.MANUAL_CONTROL,
            params={
                "hardware": "_sequence",
                "command": "reset",
                "params": {},
            },
        )

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
