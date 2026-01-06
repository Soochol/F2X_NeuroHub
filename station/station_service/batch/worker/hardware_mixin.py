"""
Hardware integration mixin for BatchWorker.

Handles hardware driver initialization, barcode scanner management,
and manual control operations.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, TYPE_CHECKING

import yaml

from station_service.batch.worker.exceptions import (
    DriverNotFoundError,
    DriverCommandError,
    BarcodeScannerError,
)

if TYPE_CHECKING:
    from station_service.ipc import IPCClient
    from station_service.ipc.messages import IPCCommand, CommandType
    from station_service.models.batch import BatchStatus
    from station_service.models.config import BatchConfig, WorkflowConfig
    from station_service.batch.worker.state import WorkerState

logger = logging.getLogger(__name__)


class HardwareMixinProtocol(Protocol):
    """Protocol for classes that use HardwareMixin."""

    _config: "BatchConfig"
    _workflow_config: "WorkflowConfig"
    _ipc: "IPCClient"
    _drivers: Dict[str, Any]
    _barcode_scanner: Optional[Any]
    _pending_barcode: Optional[str]
    _state: "WorkerState"

    @property
    def batch_id(self) -> str: ...

    # Command handler method needed for auto-start
    async def _cmd_start_sequence(self, command: "IPCCommand") -> Any: ...


class HardwareMixin:
    """
    Mixin providing hardware integration methods.

    Handles:
    - Hardware driver initialization
    - Barcode scanner lifecycle
    - Manual control commands
    - Driver discovery
    """

    async def initialize_drivers(self: HardwareMixinProtocol) -> None:
        """
        Initialize hardware drivers from configuration.

        In CLI mode, hardware drivers are initialized by the subprocess.
        The BatchWorker only tracks hardware configuration for manual control.
        """
        logger.info("Initializing hardware drivers for manual control")

        # For CLI-based execution, drivers are managed by the subprocess
        # We only initialize drivers explicitly configured in the batch config
        # for manual control purposes when sequence is not running

        # Log configured hardware
        for hw_name, hw_config in self._config.hardware.items():
            logger.info(f"Hardware configured: {hw_name} = {hw_config}")

        logger.info(f"Hardware configuration loaded: {len(self._config.hardware)} entries")

    async def handle_manual_control(
        self: HardwareMixinProtocol,
        hardware: str,
        command: str,
        params: Dict[str, Any],
    ) -> Any:
        """
        Execute a manual control command on hardware.

        Args:
            hardware: Hardware name
            command: Command to execute
            params: Command parameters

        Returns:
            Command result

        Raises:
            DriverNotFoundError: If hardware not found
            DriverCommandError: If command execution fails
        """
        if hardware not in self._drivers:
            raise DriverNotFoundError(hardware, self.batch_id)

        driver = self._drivers[hardware]
        method = getattr(driver, command, None)

        if not method or not callable(method):
            raise DriverCommandError(
                hardware_name=hardware,
                command=command,
                batch_id=self.batch_id,
                error=f"Command '{command}' not found",
            )

        try:
            if asyncio.iscoroutinefunction(method):
                result = await method(**params)
            else:
                result = method(**params)

            return result

        except Exception as e:
            raise DriverCommandError(
                hardware_name=hardware,
                command=command,
                batch_id=self.batch_id,
                error=str(e),
            ) from e

    async def cleanup_drivers(self: HardwareMixinProtocol) -> None:
        """Cleanup and disconnect all hardware drivers."""
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

    # ================================================================
    # Barcode Scanner Methods
    # ================================================================

    async def init_barcode_scanner(self: HardwareMixinProtocol) -> None:
        """Initialize barcode scanner if configured for barcode input mode."""
        # Check if workflow is enabled and using barcode input
        if not self._workflow_config.enabled:
            logger.debug("Workflow disabled, skipping barcode scanner init")
            return

        if self._workflow_config.input_mode != "barcode":
            logger.debug("Workflow input mode is not barcode, skipping scanner init")
            return

        # Check for batch-specific barcode scanner config
        scanner_config = self._config.barcode_scanner
        if not scanner_config:
            logger.info("No barcode scanner configured for this batch")
            return

        try:
            # Dynamically import the driver
            from station_service.drivers.barcode_scanner import (
                SerialBarcodeScannerDriver,
                MockBarcodeScannerDriver,
            )

            driver_name = scanner_config.driver
            driver_config = scanner_config.config

            # Select driver based on type
            if scanner_config.type == "serial":
                if driver_name == "MockBarcodeScannerDriver":
                    self._barcode_scanner = MockBarcodeScannerDriver(
                        name=f"{self.batch_id}_scanner",
                        config=driver_config,
                    )
                else:
                    self._barcode_scanner = SerialBarcodeScannerDriver(
                        name=f"{self.batch_id}_scanner",
                        config=driver_config,
                    )
            else:
                # For other types, use mock for now
                logger.warning(f"Scanner type '{scanner_config.type}' not fully implemented, using mock")
                self._barcode_scanner = MockBarcodeScannerDriver(
                    name=f"{self.batch_id}_scanner",
                    config=driver_config,
                )

            # Connect and start listening
            await self._barcode_scanner.connect()
            self._barcode_scanner.on_scan(self._on_barcode_scanned)
            await self._barcode_scanner.start_listening()

            logger.info(f"Barcode scanner initialized for batch {self.batch_id}")

        except ImportError as e:
            logger.warning(f"Barcode scanner driver not available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize barcode scanner: {e}")
            self._barcode_scanner = None

    async def _on_barcode_scanned(
        self: HardwareMixinProtocol,
        barcode: str,
    ) -> None:
        """
        Handle barcode scan event.

        If auto_sequence_start is enabled, automatically starts the sequence
        with the scanned WIP ID.

        Args:
            barcode: The scanned barcode (WIP ID)
        """
        logger.info(f"Barcode scanned: {barcode}")

        # Publish barcode scanned event
        await self._ipc.barcode_scanned(barcode)

        # Check if we should auto-start sequence
        if not self._workflow_config.auto_sequence_start:
            # Just store the barcode for manual start
            self._pending_barcode = barcode
            logger.info(f"Barcode stored for manual start: {barcode}")
            return

        # Check if sequence is already running
        from station_service.models.batch import BatchStatus

        if self._state.status == BatchStatus.RUNNING:
            logger.warning(f"Sequence already running, ignoring barcode: {barcode}")
            await self._ipc.log(
                "warning",
                f"Sequence already running, barcode ignored: {barcode}",
            )
            return

        # Auto-start sequence with the scanned WIP ID
        logger.info(f"Auto-starting sequence with WIP ID: {barcode}")

        # Create a synthetic START_SEQUENCE command
        from station_service.ipc.messages import IPCCommand, CommandType

        # Get operator ID from current execution state if available
        current_operator_id = None
        if self._state.execution:
            current_operator_id = self._state.execution.operator_id

        command = IPCCommand(
            type=CommandType.START_SEQUENCE,
            batch_id=self.batch_id,
            params={
                "parameters": {
                    "wip_id": barcode,
                    "process_id": self._config.process_id,
                    "operator_id": current_operator_id,
                },
            },
        )

        # Check if operator login is required but not provided
        if self._workflow_config.require_operator_login and not current_operator_id:
            logger.warning("Operator login required but no operator logged in")
            await self._ipc.log(
                "warning",
                f"Cannot auto-start: operator login required. Barcode stored: {barcode}",
            )
            self._pending_barcode = barcode
            return

        # Start the sequence
        response = await self._cmd_start_sequence(command)

        if response.status != "ok":
            logger.error(f"Failed to auto-start sequence: {response.error}")
            await self._ipc.error(
                "AUTO_START_FAILED",
                response.error or "Unknown error",
            )

    async def cleanup_barcode_scanner(self: HardwareMixinProtocol) -> None:
        """Clean up barcode scanner resources."""
        if self._barcode_scanner:
            try:
                await self._barcode_scanner.stop_listening()
                await self._barcode_scanner.disconnect()
            except Exception as e:
                logger.warning(f"Error cleaning up barcode scanner: {e}")
            self._barcode_scanner = None

    # ================================================================
    # Sequence Loading
    # ================================================================

    async def load_sequence(self: HardwareMixinProtocol) -> None:
        """
        Load the sequence package for CLI execution.

        For CLI-based sequences, we only need to verify the sequence exists
        and has a main.py entry point. The actual loading happens in subprocess.
        """
        package_path = self._config.sequence_package
        logger.info(f"Loading sequence package: {package_path}")

        # Determine the package name and directory
        path = Path(package_path)

        if path.is_dir():
            sequences_dir = path.parent
            package_name = path.name
        else:
            sequences_dir = Path("sequences")
            package_name = package_path

        package_dir = sequences_dir / package_name

        # Check if sequence package exists
        if not package_dir.exists():
            logger.error(f"Sequence package not found: {package_dir}")
            self._state.sequence_name = package_name
            self._state.sequence_version = "0.0.0"
            return

        # Check for CLI entry point (main.py)
        main_py = package_dir / "main.py"
        if not main_py.exists():
            logger.error(f"CLI entry point not found: {main_py}")
            logger.error("Sequences must have a main.py for CLI execution")
            self._state.sequence_name = package_name
            self._state.sequence_version = "0.0.0"
            return

        # Install dependencies from pyproject.toml if exists
        pyproject_path = package_dir / "pyproject.toml"
        if pyproject_path.exists():
            try:
                from station_service.utils.dependency_installer import (
                    install_sequence_dependencies,
                )

                installed = install_sequence_dependencies(package_dir)
                if installed:
                    logger.info(f"Installed dependencies: {installed}")
            except Exception as e:
                logger.warning(f"Failed to install dependencies: {e}")

        # Load manifest for metadata
        manifest_path = package_dir / "manifest.yaml"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = yaml.safe_load(f)
                self._state.sequence_name = manifest_data.get("name", package_name)
                self._state.sequence_version = manifest_data.get("version", "1.0.0")
                self._state.manifest = manifest_data
                logger.info(f"Sequence loaded: {self._state.sequence_name} v{self._state.sequence_version}")
            except Exception as e:
                logger.warning(f"Failed to load manifest: {e}")
                self._state.sequence_name = package_name
                self._state.sequence_version = "1.0.0"
        else:
            self._state.sequence_name = package_name
            self._state.sequence_version = "1.0.0"
            logger.info(f"Sequence loaded (no manifest): {self._state.sequence_name}")
