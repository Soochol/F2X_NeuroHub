"""
Core BatchWorker implementation.

Combines all mixins into a complete BatchWorker class with proper
lifecycle management, IPC connection, and signal handling.
"""

import asyncio
import logging
import signal
from typing import Any, Dict, Optional

from station_service.ipc import IPCClient
from station_service.models.config import BackendConfig, BatchConfig, WorkflowConfig
from station_service.storage.database import Database
from station_service.storage.repositories.execution_repository import ExecutionRepository
from station_service.storage.repositories.sync_repository import SyncRepository

from station_service.batch.worker.state import WorkerState, WorkerPhase
from station_service.batch.worker.backend_mixin import BackendMixin
from station_service.batch.worker.execution_mixin import ExecutionMixin
from station_service.batch.worker.hardware_mixin import HardwareMixin
from station_service.batch.worker.commands_mixin import CommandsMixin

logger = logging.getLogger(__name__)


class BatchWorker(BackendMixin, ExecutionMixin, HardwareMixin, CommandsMixin):
    """
    Batch worker that runs in a subprocess.

    Handles:
    - IPC communication with master process
    - Sequence loading and execution
    - Hardware driver management
    - Backend integration for 착공/완공
    - Command processing

    Architecture:
    - Core: Lifecycle, IPC connection, signal handling
    - BackendMixin: 착공/완공, WIP lookup, process headers
    - ExecutionMixin: CLI worker callbacks, result persistence
    - HardwareMixin: Driver init, barcode scanner, sequence loading
    - CommandsMixin: IPC command handlers

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
        workflow_config: Optional[WorkflowConfig] = None,
    ) -> None:
        """
        Initialize the BatchWorker.

        Args:
            batch_id: The batch identifier
            config: Batch configuration
            ipc_router_address: IPC router address for commands
            ipc_sub_address: IPC sub address for events
            backend_config: Optional backend configuration for API calls
            workflow_config: Optional workflow configuration for 착공/완공
        """
        self._batch_id = batch_id
        self._config = config
        self._backend_config = backend_config
        self._workflow_config = workflow_config or WorkflowConfig()

        # IPC client
        self._ipc = IPCClient(
            batch_id=batch_id,
            router_address=ipc_router_address,
            sub_address=ipc_sub_address,
        )

        # Unified state management
        self._state = WorkerState(batch_id=batch_id)
        if backend_config:
            self._state.backend.station_id = backend_config.station_id

        # Lifecycle control
        self._running = True

        # CLI worker and execution task
        self._cli_worker = None
        self._execution_task: Optional[asyncio.Task] = None

        # Hardware drivers
        self._drivers: Dict[str, Any] = {}

        # Barcode scanner
        self._barcode_scanner = None
        self._pending_barcode: Optional[str] = None

        # Backend client
        self._backend_client = None

        # SQLite database and repositories
        self._database: Optional[Database] = None
        self._sync_repo: Optional[SyncRepository] = None
        self._execution_repo: Optional[ExecutionRepository] = None

    @property
    def batch_id(self) -> str:
        """Get the batch ID."""
        return self._batch_id

    @property
    def state(self) -> WorkerState:
        """Get the worker state."""
        return self._state

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
            self._ipc.on_command(self.handle_command)

            # Initialize SQLite database for persistent sync queue
            await self._init_database()

            # Initialize Backend client if configured
            await self.init_backend_client()

            # Load sequence package
            await self.load_sequence()

            # Initialize drivers
            await self.initialize_drivers()

            # Initialize barcode scanner if configured
            await self.init_barcode_scanner()

            self._state.phase = WorkerPhase.READY
            logger.info(f"BatchWorker {self._batch_id} ready")

            # Main loop
            while self._running:
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.exception(f"BatchWorker error: {e}")
            self._state.phase = WorkerPhase.ERROR
            await self._ipc.error("WORKER_ERROR", str(e))

        finally:
            await self._cleanup()

        logger.info(f"BatchWorker {self._batch_id} exiting")

    def _handle_signal(self) -> None:
        """Handle shutdown signals."""
        logger.info(f"BatchWorker {self._batch_id} received shutdown signal")
        self._running = False

    async def _init_database(self) -> None:
        """Initialize SQLite database for persistent data and sync queue."""
        try:
            # Use batch-specific database to avoid concurrent write conflicts
            self._database = await Database.create(db_path=f"data/batch_{self._batch_id}.db")
            await self._database.init_db()
            self._sync_repo = SyncRepository(self._database)
            self._execution_repo = ExecutionRepository(self._database)
            logger.info(f"Database initialized for batch {self._batch_id}")
        except Exception as e:
            logger.warning(f"Failed to initialize database: {e}")
            self._database = None
            self._sync_repo = None
            self._execution_repo = None

    async def _cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up worker resources")
        self._state.phase = WorkerPhase.STOPPING

        # Close process header if open
        await self.close_process_header(status="CANCELLED")

        # Stop any running CLI execution
        await self.stop_cli_worker()

        # Cancel execution task
        if self._execution_task:
            self._execution_task.cancel()
            try:
                await self._execution_task
            except asyncio.CancelledError:
                pass
            self._execution_task = None

        # Cleanup drivers
        await self.cleanup_drivers()

        # Cleanup barcode scanner
        await self.cleanup_barcode_scanner()

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

        self._state.phase = WorkerPhase.STOPPED
        logger.info("Worker cleanup complete")
