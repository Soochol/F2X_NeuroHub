"""
BatchProcess wrapper for Station Service.

Provides a clean interface for managing a batch worker subprocess.
"""

import asyncio
import logging
import multiprocessing
import os
import signal
import sys
from typing import Any, Dict, Optional

from station_service.models.config import BatchConfig, BackendConfig, WorkflowConfig

logger = logging.getLogger(__name__)


class BatchProcess:
    """
    Wrapper for a batch worker subprocess.

    Manages the lifecycle of a batch process including starting,
    stopping, and monitoring.

    Usage:
        process = BatchProcess(
            batch_id="batch_1",
            config=batch_config,
            ipc_router_address="tcp://127.0.0.1:5555",
            ipc_sub_address="tcp://127.0.0.1:5557",
        )
        await process.start()

        if process.is_alive():
            await process.stop()
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
        Initialize the BatchProcess.

        Args:
            batch_id: The batch identifier
            config: Batch configuration
            ipc_router_address: IPC router address for commands
            ipc_sub_address: IPC sub address for events
            backend_config: Optional backend configuration for API integration
            workflow_config: Optional workflow configuration for 착공/완공
        """
        self._batch_id = batch_id
        self._config = config
        self._ipc_router_address = ipc_router_address
        self._ipc_sub_address = ipc_sub_address
        self._backend_config = backend_config
        self._workflow_config = workflow_config

        self._process: Optional[multiprocessing.Process] = None
        self._started_at: Optional[float] = None

    @property
    def batch_id(self) -> str:
        """Get the batch ID."""
        return self._batch_id

    @property
    def pid(self) -> Optional[int]:
        """Get the process ID."""
        if self._process:
            return self._process.pid
        return None

    @property
    def is_alive(self) -> bool:
        """Check if the process is alive."""
        return self._process is not None and self._process.is_alive()

    @property
    def exit_code(self) -> Optional[int]:
        """Get the process exit code."""
        if self._process and not self._process.is_alive():
            return self._process.exitcode
        return None

    async def start(self) -> None:
        """
        Start the batch worker process.

        Raises:
            RuntimeError: If process is already running
        """
        if self._process and self._process.is_alive():
            raise RuntimeError(f"Batch {self._batch_id} is already running")

        # Serialize configs for subprocess
        backend_config_dict = self._backend_config.model_dump() if self._backend_config else None
        workflow_config_dict = self._workflow_config.model_dump() if self._workflow_config else None

        # Create process
        self._process = multiprocessing.Process(
            target=self._run_worker,
            args=(
                self._batch_id,
                self._config.model_dump(),
                self._ipc_router_address,
                self._ipc_sub_address,
                backend_config_dict,
                workflow_config_dict,
            ),
            daemon=True,
            name=f"batch-{self._batch_id}",
        )

        # Start process
        self._process.start()
        self._started_at = asyncio.get_event_loop().time()

        # Wait briefly for process to initialize
        await asyncio.sleep(0.1)

        if not self._process.is_alive():
            raise RuntimeError(
                f"Batch {self._batch_id} process failed to start "
                f"(exit code: {self._process.exitcode})"
            )

        logger.info(f"Batch {self._batch_id} process started (PID: {self._process.pid})")

    async def stop(self, timeout: float = 1.0) -> None:
        """
        Stop the batch worker process.

        First attempts graceful shutdown, then forceful termination.

        Args:
            timeout: Timeout for graceful shutdown in seconds (default: 1.0)
        """
        if not self._process:
            return

        if not self._process.is_alive():
            self._cleanup()
            return

        # Try graceful shutdown by joining with timeout
        logger.info(f"Stopping batch {self._batch_id} (PID: {self._process.pid})")

        # Use asyncio to wait with timeout
        loop = asyncio.get_event_loop()
        try:
            await asyncio.wait_for(
                loop.run_in_executor(None, self._process.join, timeout),
                timeout=timeout + 0.5,
            )
        except asyncio.TimeoutError:
            pass

        # If still alive, terminate
        if self._process.is_alive():
            logger.warning(f"Batch {self._batch_id} did not stop gracefully, terminating")
            self._process.terminate()

            # Wait briefly for termination
            try:
                await asyncio.wait_for(
                    loop.run_in_executor(None, self._process.join, 1.0),
                    timeout=1.5,
                )
            except asyncio.TimeoutError:
                pass

        # If still alive, kill
        if self._process.is_alive():
            logger.error(f"Batch {self._batch_id} did not terminate, killing")
            self._process.kill()
            self._process.join(timeout=1.0)

        self._cleanup()
        logger.info(f"Batch {self._batch_id} stopped")

    def _cleanup(self) -> None:
        """Clean up process resources."""
        if self._process:
            try:
                self._process.close()
            except Exception:
                pass
        self._process = None

    @staticmethod
    def _run_worker(
        batch_id: str,
        config_dict: Dict[str, Any],
        ipc_router_address: str,
        ipc_sub_address: str,
        backend_config_dict: Optional[Dict[str, Any]] = None,
        workflow_config_dict: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Entry point for the worker subprocess.

        This method runs in a separate process.

        Args:
            batch_id: The batch ID
            config_dict: Serialized batch configuration
            ipc_router_address: IPC router address
            ipc_sub_address: IPC sub address
            backend_config_dict: Serialized backend configuration for API integration
            workflow_config_dict: Serialized workflow configuration for 착공/완공
        """
        # Import here to avoid circular imports and ensure
        # we're importing in the subprocess context
        import asyncio
        import logging

        # Configure logging for subprocess
        logging.basicConfig(
            level=logging.INFO,
            format=f"[{batch_id}] %(levelname)s: %(message)s",
        )

        logger = logging.getLogger(__name__)
        logger.info(f"Worker process starting for batch {batch_id}")

        try:
            # Import worker class
            from station_service.batch.worker import BatchWorker
            from station_service.models.config import BatchConfig, BackendConfig, WorkflowConfig

            # Reconstruct configs
            config = BatchConfig(**config_dict)
            backend_config = BackendConfig(**backend_config_dict) if backend_config_dict else None
            workflow_config = WorkflowConfig(**workflow_config_dict) if workflow_config_dict else None

            if backend_config:
                logger.info(f"Backend integration enabled: {backend_config.url}")
            else:
                logger.info("Backend integration disabled (no config)")

            # Create and run worker
            worker = BatchWorker(
                batch_id=batch_id,
                config=config,
                ipc_router_address=ipc_router_address,
                ipc_sub_address=ipc_sub_address,
                backend_config=backend_config,
                workflow_config=workflow_config,
            )

            # Run the async main loop
            asyncio.run(worker.run())

        except Exception as e:
            logger.exception(f"Worker process error: {e}")
            sys.exit(1)

        logger.info(f"Worker process exiting for batch {batch_id}")
