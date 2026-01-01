"""
BatchWorker for Station Service.

Runs in a subprocess and handles sequence execution, hardware control,
IPC communication with the master process, and Backend integration for
착공(process start) and 완공(process complete) operations.
"""

import asyncio
import json
import logging
import signal
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from station_service.core.exceptions import (
    BackendConnectionError,
    BackendError,
    WIPNotFoundError,
)
from station_service.ipc import IPCClient, IPCResponse
from station_service.ipc.messages import CommandType, IPCCommand, IPCEvent
from station_service.models.batch import BatchStatus
from station_service.models.config import BackendConfig, BatchConfig
from station_service.sequence.executor import SequenceExecutor, ExecutionResult, StepResult
from station_service.sequence.decorators import StepMeta
from station_service.storage.database import Database
from station_service.storage.repositories.sync_repository import SyncRepository
from station_service.sync.backend_client import BackendClient
from station_service.sync.models import (
    ProcessCompleteRequest,
    ProcessStartRequest,
    WIPLookupResult,
)

logger = logging.getLogger(__name__)


class BatchWorker:
    """
    Batch worker that runs in a subprocess.

    Handles:
    - IPC communication with master process
    - Sequence loading and execution
    - Hardware driver management
    - Command processing

    Usage:
        worker = BatchWorker(
            batch_id="batch_1",
            config=batch_config,
            ipc_router_address="tcp://127.0.0.1:5555",
            ipc_sub_address="tcp://127.0.0.1:5557",
        )
        await worker.run()
    """

    def __init__(
        self,
        batch_id: str,
        config: BatchConfig,
        ipc_router_address: str,
        ipc_sub_address: str,
        backend_config: Optional[BackendConfig] = None,
    ) -> None:
        """
        Initialize the BatchWorker.

        Args:
            batch_id: The batch identifier
            config: Batch configuration
            ipc_router_address: IPC router address for commands
            ipc_sub_address: IPC sub address for events
            backend_config: Optional backend configuration for API calls
        """
        self._batch_id = batch_id
        self._config = config
        self._backend_config = backend_config

        # IPC client
        self._ipc = IPCClient(
            batch_id=batch_id,
            router_address=ipc_router_address,
            sub_address=ipc_sub_address,
        )

        # State
        self._running = True
        self._status = BatchStatus.IDLE
        self._sequence_instance = None
        self._executor: Optional[SequenceExecutor] = None
        self._execution_task: Optional[asyncio.Task] = None
        self._current_execution_id: Optional[str] = None
        self._drivers: Dict[str, Any] = {}

        # Sequence loading state
        self._manifest = None
        self._loader = None
        self._package_path = None

        # Execution state for status reporting
        self._current_step: Optional[str] = None
        self._step_index: int = 0
        self._total_steps: int = 0
        self._progress: float = 0.0
        self._started_at: Optional[datetime] = None
        self._step_results: List[Dict[str, Any]] = []  # Track step results

        # Last run state (preserved after completion)
        self._last_run_passed: Optional[bool] = None
        self._last_run_progress: float = 0.0
        self._last_step_results: List[Dict[str, Any]] = []

        # Backend integration state
        self._backend_client: Optional[BackendClient] = None
        self._backend_online: bool = False
        self._current_wip_id: Optional[str] = None  # String WIP ID from scan
        self._current_wip_int_id: Optional[int] = None  # Int ID for API calls
        self._current_process_id: Optional[int] = None
        self._current_operator_id: Optional[int] = None
        self._process_start_time: Optional[datetime] = None

        # SQLite database and sync repository for persistent offline queue
        self._database: Optional[Database] = None
        self._sync_repo: Optional[SyncRepository] = None

    @property
    def batch_id(self) -> str:
        """Get the batch ID."""
        return self._batch_id

    async def run(self) -> None:
        """
        Main worker loop.

        Connects to IPC, loads sequence, and processes commands.
        """
        logger.info(f"BatchWorker {self._batch_id} starting")

        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_signal)

        try:
            # Connect to IPC
            await self._ipc.connect()
            self._ipc.on_command(self._handle_command)

            # Initialize SQLite database for persistent sync queue
            await self._init_database()

            # Initialize Backend client if configured
            await self._init_backend_client()

            # Load sequence package
            await self._load_sequence()

            # Initialize drivers
            await self._initialize_drivers()

            self._status = BatchStatus.IDLE
            logger.info(f"BatchWorker {self._batch_id} ready")

            # Main loop
            while self._running:
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.exception(f"BatchWorker error: {e}")
            await self._ipc.error("WORKER_ERROR", str(e))

        finally:
            await self._cleanup()

        logger.info(f"BatchWorker {self._batch_id} exiting")

    def _handle_signal(self) -> None:
        """Handle shutdown signals."""
        logger.info(f"BatchWorker {self._batch_id} received shutdown signal")
        self._running = False

    async def _handle_command(self, command: IPCCommand) -> IPCResponse:
        """
        Handle incoming IPC commands.

        Args:
            command: The command to handle

        Returns:
            Response to the command
        """
        logger.debug(f"Handling command: {command.type.value}")

        try:
            if command.type == CommandType.START_SEQUENCE:
                return await self._cmd_start_sequence(command)

            elif command.type == CommandType.STOP_SEQUENCE:
                return await self._cmd_stop_sequence(command)

            elif command.type == CommandType.GET_STATUS:
                return await self._cmd_get_status(command)

            elif command.type == CommandType.MANUAL_CONTROL:
                return await self._cmd_manual_control(command)

            elif command.type == CommandType.SHUTDOWN:
                return await self._cmd_shutdown(command)

            elif command.type == CommandType.PING:
                return IPCResponse.ok(command.request_id, {"pong": True})

            else:
                return IPCResponse.error(
                    command.request_id,
                    f"Unknown command type: {command.type.value}",
                )

        except Exception as e:
            logger.exception(f"Command handling error: {e}")
            return IPCResponse.error(command.request_id, str(e))

    async def _cmd_start_sequence(self, command: IPCCommand) -> IPCResponse:
        """
        Handle START_SEQUENCE command with Backend integration.

        Expected parameters:
        - wip_id: WIP ID string from barcode scan (required for Backend)
        - process_id: Process number 1-8 (required for Backend)
        - operator_id: Operator ID (required for Backend)
        - equipment_id: Equipment ID (optional)
        - Other sequence-specific parameters
        """
        if self._status == BatchStatus.RUNNING:
            return IPCResponse.error(
                command.request_id,
                "Sequence already running",
            )

        # Reset step results for new execution
        self._step_results = []

        parameters = command.params.get("parameters", {})

        # Extract WIP context from parameters
        wip_id_string = parameters.get("wip_id")
        process_id = parameters.get("process_id")
        operator_id = parameters.get("operator_id")
        equipment_id = parameters.get("equipment_id")

        # Generate execution ID
        self._current_execution_id = str(uuid.uuid4())[:8]

        # ═══════════════════════════════════════════════════════════════
        # Backend Integration: 착공 (Start Process)
        # ═══════════════════════════════════════════════════════════════
        if wip_id_string and process_id and operator_id:
            try:
                # 1. Lookup WIP to get int ID
                wip_lookup = await self._lookup_wip(wip_id_string, process_id)
                self._current_wip_id = wip_id_string
                self._current_wip_int_id = wip_lookup.id
                self._current_process_id = process_id
                self._current_operator_id = operator_id

                # 2. Call 착공 (start-process)
                self._process_start_time = datetime.now()
                await self._call_start_process(
                    wip_int_id=wip_lookup.id,
                    process_id=process_id,
                    operator_id=operator_id,
                    equipment_id=equipment_id,
                )
                logger.info(f"착공 completed: WIP={wip_id_string}, Process={process_id}")

            except WIPNotFoundError as e:
                logger.error(f"WIP not found: {e}")
                return IPCResponse.error(command.request_id, str(e))

            except BackendError as e:
                # Backend error but continue in offline mode
                logger.warning(f"Backend error during 착공, continuing offline: {e}")
                self._backend_online = False
                self._current_wip_id = wip_id_string
                self._current_process_id = process_id
                self._current_operator_id = operator_id
                self._process_start_time = datetime.now()

                # Queue for later sync
                await self._queue_for_offline_sync(
                    "wip_process",
                    wip_id_string,
                    "start_process",
                    {
                        "wip_int_id": self._current_wip_int_id,
                        "request": {
                            "process_id": process_id,
                            "operator_id": operator_id,
                            "equipment_id": equipment_id,
                            "started_at": self._process_start_time.isoformat(),
                        },
                    },
                )

        else:
            # No WIP context - running sequence without Backend integration
            logger.debug("Running sequence without Backend integration (no wip_id)")
            self._current_wip_id = None
            self._current_wip_int_id = None
            self._current_process_id = None
            self._current_operator_id = None

        # Create executor
        self._executor = SequenceExecutor(
            sequence_instance=self._sequence_instance,
            parameters=parameters,
            on_step_start=self._on_step_start,
            on_step_complete=self._on_step_complete,
            on_log=self._on_log,
            on_error=self._on_error,
        )

        # Set total steps from executor for progress tracking
        self._total_steps = self._executor.total_steps

        # Start execution task
        self._execution_task = asyncio.create_task(self._run_sequence())

        self._status = BatchStatus.RUNNING
        self._started_at = datetime.now()

        # Publish batch status update immediately so frontend knows we're running
        await self._ipc.status_update({
            "status": self._status.value,
            "execution_id": self._current_execution_id,
            "current_step": None,
            "step_index": 0,
            "total_steps": self._total_steps,
            "progress": 0.0,
        })

        return IPCResponse.ok(command.request_id, {
            "execution_id": self._current_execution_id,
            "status": "started",
            "wip_id": self._current_wip_id,
            "process_id": self._current_process_id,
            "backend_online": self._backend_online,
        })

    async def _cmd_stop_sequence(self, command: IPCCommand) -> IPCResponse:
        """Handle STOP_SEQUENCE command."""
        if self._executor:
            await self._executor.stop()

        if self._execution_task:
            self._execution_task.cancel()
            try:
                await self._execution_task
            except asyncio.CancelledError:
                pass
            self._execution_task = None

        self._status = BatchStatus.IDLE
        self._reset_execution_state()

        return IPCResponse.ok(command.request_id, {"status": "stopped"})

    async def _cmd_get_status(self, command: IPCCommand) -> IPCResponse:
        """Handle GET_STATUS command."""
        # When idle, use last run state if available for progress display
        is_idle = self._status == BatchStatus.IDLE
        has_last_run = self._last_run_passed is not None

        status = {
            "status": self._status.value,
            "sequence_name": getattr(self._sequence_instance, "name", None),
            "sequence_version": getattr(self._sequence_instance, "version", None),
            "current_step": self._current_step,
            "step_index": self._step_index if not is_idle else len(self._last_step_results),
            "total_steps": self._total_steps if not is_idle else len(self._last_step_results),
            # Use last run progress when idle (preserves 100% after completion)
            "progress": self._last_run_progress if (is_idle and has_last_run) else self._progress,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "execution_id": self._current_execution_id,
            # Use last run steps when idle
            "steps": self._last_step_results if (is_idle and has_last_run) else self._step_results,
            "last_run_passed": self._last_run_passed,
        }
        return IPCResponse.ok(command.request_id, status)

    async def _cmd_manual_control(self, command: IPCCommand) -> IPCResponse:
        """Handle MANUAL_CONTROL command."""
        if self._status == BatchStatus.RUNNING:
            return IPCResponse.error(
                command.request_id,
                "Cannot execute manual control during sequence execution",
            )

        hardware = command.params.get("hardware")
        cmd = command.params.get("command")
        params = command.params.get("params", {})

        if hardware not in self._drivers:
            return IPCResponse.error(
                command.request_id,
                f"Hardware '{hardware}' not found",
            )

        driver = self._drivers[hardware]
        method = getattr(driver, cmd, None)

        if not method or not callable(method):
            return IPCResponse.error(
                command.request_id,
                f"Command '{cmd}' not found on hardware '{hardware}'",
            )

        try:
            if asyncio.iscoroutinefunction(method):
                result = await method(**params)
            else:
                result = method(**params)

            return IPCResponse.ok(command.request_id, {"result": result})

        except Exception as e:
            return IPCResponse.error(command.request_id, str(e))

    async def _cmd_shutdown(self, command: IPCCommand) -> IPCResponse:
        """Handle SHUTDOWN command."""
        self._running = False

        # Stop any running sequence
        if self._executor:
            await self._executor.stop()

        return IPCResponse.ok(command.request_id, {"status": "shutdown"})

    async def _run_sequence(self) -> None:
        """Run the sequence execution with 완공 (complete process) integration."""
        wip_status = None
        can_convert = False

        try:
            result = await self._executor.run()

            # ═══════════════════════════════════════════════════════════════
            # Backend Integration: 완공 (Complete Process)
            # ═══════════════════════════════════════════════════════════════
            if (
                self._current_wip_int_id is not None
                and self._current_process_id is not None
                and self._current_operator_id is not None
            ):
                try:
                    # Determine result and extract data from execution
                    process_result = self._determine_process_result(result)
                    measurements = self._extract_measurements(result)
                    defects = self._extract_defects(result)

                    # Call 완공 (complete-process)
                    complete_response = await self._call_complete_process(
                        wip_int_id=self._current_wip_int_id,
                        process_id=self._current_process_id,
                        operator_id=self._current_operator_id,
                        result=process_result,
                        measurements=measurements,
                        defects=defects,
                        notes=f"Sequence: {result.sequence_name} v{result.sequence_version}",
                    )

                    # Check if WIP is now COMPLETED (all processes done)
                    wip_item = complete_response.get("wip_item", {})
                    wip_status = wip_item.get("status")
                    can_convert = wip_status == "COMPLETED"

                    logger.info(
                        f"완공 completed: WIP={self._current_wip_id}, "
                        f"Process={self._current_process_id}, Result={process_result}"
                    )

                except BackendError as e:
                    # Queue for offline sync
                    logger.warning(f"Backend error during 완공, queuing for sync: {e}")
                    process_result = self._determine_process_result(result)
                    measurements = self._extract_measurements(result)
                    defects = self._extract_defects(result)

                    await self._queue_for_offline_sync(
                        "wip_process",
                        self._current_wip_id,
                        "complete_process",
                        {
                            "wip_int_id": self._current_wip_int_id,
                            "process_id": self._current_process_id,
                            "operator_id": self._current_operator_id,
                            "request": {
                                "result": process_result,
                                "measurements": measurements,
                                "defects": defects,
                                "notes": f"Sequence: {result.sequence_name}",
                                "completed_at": datetime.now().isoformat(),
                            },
                        },
                    )

            # Publish completion event
            await self._ipc.sequence_complete(
                execution_id=self._current_execution_id,
                overall_pass=result.overall_pass,
                duration=result.duration or 0,
                result=result.to_dict(),
            )

            # Publish additional WIP status if available
            if self._current_wip_id:
                await self._ipc.publish_event(
                    "WIP_PROCESS_COMPLETE",
                    {
                        "wip_id": self._current_wip_id,
                        "process_id": self._current_process_id,
                        "result": self._determine_process_result(result) if result else "FAIL",
                        "wip_status": wip_status,
                        "can_convert": can_convert,
                    },
                )

        except asyncio.CancelledError:
            logger.info("Sequence execution cancelled")
            await self._ipc.log("info", "Sequence execution cancelled")

        except Exception as e:
            logger.exception(f"Sequence execution error: {e}")
            await self._ipc.error("EXECUTION_ERROR", str(e))

        finally:
            self._status = BatchStatus.IDLE
            self._save_last_run_state()
            self._reset_execution_state()

    def _save_last_run_state(self) -> None:
        """Save last run state before resetting (for UI display after completion)."""
        # Preserve progress at 100% if we had steps
        if self._total_steps > 0:
            self._last_run_progress = 1.0  # Always 100% when completed
        else:
            self._last_run_progress = self._progress

        # Preserve step results
        self._last_step_results = self._step_results.copy()

        # Determine pass/fail from step results
        if self._step_results:
            self._last_run_passed = all(
                step.get("status") == "completed" for step in self._step_results
            )
        else:
            self._last_run_passed = None

    def _reset_execution_state(self) -> None:
        """Reset execution state variables."""
        self._current_step = None
        self._step_index = 0
        self._total_steps = 0
        self._progress = 0.0
        self._started_at = None
        self._current_execution_id = None
        self._executor = None
        self._step_results = []  # Clear current step results

        # Reset WIP context
        self._current_wip_id = None
        self._current_wip_int_id = None
        self._current_process_id = None
        self._current_operator_id = None
        self._process_start_time = None

    def _on_step_start(self, step_name: str, step_meta: StepMeta) -> None:
        """Callback for step start."""
        self._current_step = step_name
        # Note: step_index and total_steps should come from executor context

        # Add new step to results list (use current length as index)
        self._step_results.append({
            "name": step_name,
            "status": "running",
            "duration": None,
            "result": None,
        })

        # Schedule async event publication
        asyncio.create_task(self._ipc.step_start(
            step_name=step_name,
            step_index=len(self._step_results) - 1,
            total_steps=self._total_steps,
            execution_id=self._current_execution_id or "",
        ))

        # Broadcast status update with current step
        asyncio.create_task(self._ipc.status_update({
            "status": self._status.value,
            "execution_id": self._current_execution_id,
            "current_step": step_name,
            "step_index": len(self._step_results) - 1,
            "total_steps": self._total_steps,
            "progress": self._progress,
        }))

    def _on_step_complete(self, step_name: str, step_result: StepResult) -> None:
        """Callback for step completion."""
        self._step_index = len(self._step_results)
        if self._total_steps > 0:
            self._progress = self._step_index / self._total_steps

        # Update the last step result (the one that just completed)
        if self._step_results:
            self._step_results[-1] = {
                "name": step_name,
                "status": "completed" if step_result.passed else "failed",
                "duration": step_result.duration,
                "result": step_result.to_dict() if step_result else None,
            }

        # Schedule async event publication
        asyncio.create_task(self._ipc.step_complete(
            step_name=step_name,
            step_index=len(self._step_results) - 1,
            duration=step_result.duration or 0,
            passed=step_result.passed,
            result=step_result.to_dict(),
            execution_id=self._current_execution_id or "",
        ))

        # Broadcast status update with new progress
        asyncio.create_task(self._ipc.status_update({
            "status": self._status.value,
            "execution_id": self._current_execution_id,
            "current_step": step_name,
            "step_index": self._step_index,
            "total_steps": self._total_steps,
            "progress": self._progress,
        }))

    def _on_log(self, level: str, message: str) -> None:
        """Callback for log messages."""
        asyncio.create_task(self._ipc.log(level, message))

    def _on_error(self, step_name: str, error: Exception) -> None:
        """Callback for errors."""
        asyncio.create_task(self._ipc.error(
            code=type(error).__name__,
            message=str(error),
            step=step_name,
        ))

    async def _load_sequence(self) -> None:
        """Load the sequence package."""
        from pathlib import Path

        from station_service.sequence.loader import SequenceLoader

        package_path = self._config.sequence_package

        logger.info(f"Loading sequence package: {package_path}")

        # Determine the package name and directory
        path = Path(package_path)

        if path.is_dir():
            # Path points to a directory - use it directly
            packages_dir = path.parent
            package_name = path.name
        else:
            # Path is a name - use default sequences directory
            packages_dir = Path("sequences")
            package_name = package_path

        try:
            loader = SequenceLoader(str(packages_dir))
            manifest = await loader.load_package(package_name)
            package_full_path = loader.get_package_path(package_name)

            # Load the sequence class
            sequence_class = await loader.load_sequence_class(manifest, package_full_path)

            # Create instance of the sequence
            self._sequence_instance = sequence_class()

            # Store manifest for reference
            self._manifest = manifest

            # Store loader for driver loading
            self._loader = loader
            self._package_path = package_full_path

            logger.info(f"Sequence package loaded: {manifest.name} v{manifest.version}")

        except Exception as e:
            logger.warning(f"Failed to load sequence package '{package_path}': {e}")
            logger.info("Using placeholder sequence")

            # Fallback to placeholder for development
            class PlaceholderSequence:
                name = package_path
                version = "1.0.0"

            self._sequence_instance = PlaceholderSequence()
            self._manifest = None
            self._loader = None
            self._package_path = None

    async def _initialize_drivers(self) -> None:
        """Initialize hardware drivers."""
        logger.info("Initializing hardware drivers")

        # If we have a manifest and loader, load drivers from package
        if self._manifest and self._loader and self._package_path:
            try:
                driver_classes = await self._loader.load_hardware_drivers(
                    self._manifest, self._package_path
                )

                for hw_name, driver_class in driver_classes.items():
                    hw_config = self._config.hardware.get(hw_name, {})
                    try:
                        # Instantiate driver with config
                        driver = driver_class(**hw_config)

                        # Connect if driver has connect method
                        if hasattr(driver, "connect"):
                            if asyncio.iscoroutinefunction(driver.connect):
                                await driver.connect()
                            else:
                                driver.connect()

                        self._drivers[hw_name] = driver
                        logger.info(f"Hardware driver initialized: {hw_name}")

                    except Exception as e:
                        logger.error(f"Failed to initialize driver {hw_name}: {e}")

            except Exception as e:
                logger.warning(f"Failed to load hardware drivers: {e}")

        # Log any configured hardware that wasn't loaded from package
        for hw_name, hw_config in self._config.hardware.items():
            if hw_name not in self._drivers:
                logger.info(f"Hardware configured (no driver loaded): {hw_name} = {hw_config}")

        logger.info(f"Hardware drivers initialized: {len(self._drivers)} active")

    async def _cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up worker resources")

        # Stop any running execution
        if self._executor:
            try:
                await self._executor.stop()
            except Exception as e:
                logger.warning(f"Error stopping executor: {e}")

        # Disconnect drivers
        for name, driver in self._drivers.items():
            try:
                if hasattr(driver, "disconnect"):
                    if asyncio.iscoroutinefunction(driver.disconnect):
                        await driver.disconnect()
                    else:
                        driver.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting driver {name}: {e}")

        self._drivers.clear()

        # Disconnect Backend client
        if self._backend_client:
            try:
                await self._backend_client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting Backend client: {e}")

        # Disconnect database
        if self._database:
            try:
                await self._database.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting database: {e}")

        # Disconnect IPC
        try:
            await self._ipc.disconnect()
        except Exception as e:
            logger.warning(f"Error disconnecting IPC: {e}")

        logger.info("Worker cleanup complete")

    # ================================================================
    # Database and Sync Methods
    # ================================================================

    async def _init_database(self) -> None:
        """Initialize SQLite database for persistent sync queue."""
        try:
            self._database = Database(db_path="data/station.db")
            await self._database.connect()
            self._sync_repo = SyncRepository(self._database)
            logger.info("Database initialized for offline sync queue")
        except Exception as e:
            logger.warning(f"Failed to initialize database: {e}")
            self._database = None
            self._sync_repo = None

    # ================================================================
    # Backend Integration Methods
    # ================================================================

    async def _init_backend_client(self) -> None:
        """Initialize and connect Backend client if configured."""
        if not self._backend_config or not self._backend_config.url:
            logger.info("Backend not configured, running without Backend integration")
            return

        try:
            self._backend_client = BackendClient(self._backend_config)
            await self._backend_client.connect()
            self._backend_online = await self._backend_client.health_check()

            if self._backend_online:
                logger.info(f"Backend client connected: {self._backend_config.url}")
            else:
                logger.warning("Backend client connected but health check failed")

        except Exception as e:
            logger.warning(f"Failed to initialize Backend client: {e}")
            self._backend_client = None
            self._backend_online = False

    async def _lookup_wip(
        self,
        wip_id_string: str,
        process_id: Optional[int] = None,
    ) -> WIPLookupResult:
        """
        Lookup WIP by string ID to get integer ID.

        Args:
            wip_id_string: WIP ID string from barcode
            process_id: Optional process ID for validation

        Returns:
            WIPLookupResult with int ID

        Raises:
            WIPNotFoundError: If WIP not found
            BackendConnectionError: If Backend not available
        """
        if not self._backend_client:
            raise BackendConnectionError("", "Backend client not initialized")

        return await self._backend_client.lookup_wip(wip_id_string, process_id)

    async def _call_start_process(
        self,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        equipment_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Call Backend start-process API (착공).

        Args:
            wip_int_id: WIP integer ID
            process_id: Process number
            operator_id: Operator ID
            equipment_id: Optional equipment ID

        Returns:
            Backend response

        Raises:
            BackendError: If API call fails
        """
        if not self._backend_client:
            raise BackendConnectionError("", "Backend client not initialized")

        request = ProcessStartRequest(
            process_id=process_id,
            operator_id=operator_id,
            equipment_id=equipment_id,
            started_at=datetime.now(),
        )

        return await self._backend_client.start_process(wip_int_id, request)

    async def _call_complete_process(
        self,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        result: str,
        measurements: Dict[str, Any],
        defects: List[str],
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Call Backend complete-process API (완공).

        Args:
            wip_int_id: WIP integer ID
            process_id: Process number
            operator_id: Operator ID
            result: PASS, FAIL, or REWORK
            measurements: Measurement data from sequence
            defects: Defect codes if failed
            notes: Operator notes

        Returns:
            Backend response

        Raises:
            BackendError: If API call fails
        """
        if not self._backend_client:
            raise BackendConnectionError("", "Backend client not initialized")

        request = ProcessCompleteRequest(
            result=result,
            measurements=measurements,
            defects=defects,
            notes=notes,
            completed_at=datetime.now(),
        )

        return await self._backend_client.complete_process(
            wip_int_id, process_id, operator_id, request
        )

    async def _queue_for_offline_sync(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: Dict[str, Any],
    ) -> None:
        """
        Queue operation for offline sync using SQLite.

        Args:
            entity_type: Type of entity (e.g., "wip_process")
            entity_id: Entity identifier
            action: Action type (e.g., "start_process", "complete_process")
            payload: Request data
        """
        if self._sync_repo:
            try:
                queue_id = await self._sync_repo.enqueue(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    payload=payload,
                )
                logger.info(f"Queued for offline sync: {action} for {entity_id} (id={queue_id})")
            except Exception as e:
                logger.error(f"Failed to queue for offline sync: {e}")
        else:
            logger.warning(f"No sync repo available, cannot queue {action} for {entity_id}")

    def _determine_process_result(self, execution_result: ExecutionResult) -> str:
        """
        Determine PASS/FAIL/REWORK from execution result.

        Args:
            execution_result: Sequence execution result

        Returns:
            "PASS", "FAIL", or "REWORK"
        """
        if execution_result.overall_pass:
            return "PASS"

        # Check if rework was requested
        if hasattr(execution_result, "rework_requested") and execution_result.rework_requested:
            return "REWORK"

        return "FAIL"

    def _extract_measurements(self, execution_result: ExecutionResult) -> Dict[str, Any]:
        """
        Extract measurements from sequence execution result.

        Args:
            execution_result: Sequence execution result

        Returns:
            Dict of measurement data
        """
        measurements: Dict[str, Any] = {}

        # Add cycle time
        if execution_result.duration:
            measurements["cycle_time_ms"] = int(execution_result.duration * 1000)

        # Extract measurements from each step
        for step in execution_result.steps:
            step_data = step.to_dict() if hasattr(step, "to_dict") else {}

            # Get measurements from step result
            step_measurements = step_data.get("measurements", {})
            if step_measurements:
                measurements.update(step_measurements)

            # Get outputs from step
            step_outputs = step_data.get("outputs", {})
            if step_outputs:
                measurements.update(step_outputs)

        return measurements

    def _extract_defects(self, execution_result: ExecutionResult) -> List[str]:
        """
        Extract defect codes from sequence execution result.

        Args:
            execution_result: Sequence execution result

        Returns:
            List of unique defect codes
        """
        defects: List[str] = []

        for step in execution_result.steps:
            if not step.passed:
                step_data = step.to_dict() if hasattr(step, "to_dict") else {}

                # Get defects from step result
                step_defects = step_data.get("defects", [])
                if step_defects:
                    defects.extend(step_defects)

                # Also check for error codes
                if step.error:
                    error_code = type(step.error).__name__
                    if error_code not in defects:
                        defects.append(error_code)

        # Return unique defects
        return list(set(defects))
