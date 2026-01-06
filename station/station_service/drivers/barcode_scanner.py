"""
Barcode Scanner Driver for Station Service.

Provides serial-based barcode scanner integration for WIP ID scanning
in the 착공/완공 (process start/complete) workflow.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from station_service.drivers.base import (
    BaseDriver,
    DriverConnectionError,
    DriverError,
)

logger = logging.getLogger(__name__)


class BarcodeScannerError(DriverError):
    """Exception for barcode scanner errors."""

    pass


class SerialBarcodeScannerDriver(BaseDriver):
    """
    Serial-based barcode scanner driver.

    Connects to a barcode scanner via serial port and reads scanned barcodes.
    Supports various termination characters (CR, LF, CRLF).

    Configuration:
        port: Serial port (e.g., "COM3", "/dev/ttyUSB0")
        baudrate: Serial baudrate (default: 9600)
        terminator: Line terminator (default: "\\r\\n")
        timeout: Read timeout in seconds (default: 0.1)

    Usage:
        scanner = SerialBarcodeScannerDriver(
            name="wip_scanner",
            config={"port": "COM3", "baudrate": 9600}
        )
        scanner.on_scan(lambda barcode: print(f"Scanned: {barcode}"))
        await scanner.connect()
        await scanner.start_listening()
    """

    def __init__(
        self,
        name: str = "",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the barcode scanner driver.

        Args:
            name: Driver instance name
            config: Configuration dictionary with serial port settings
        """
        super().__init__(name, config)

        # Serial configuration
        self._port = self.config.get("port", "COM3")
        self._baudrate = self.config.get("baudrate", 9600)
        self._terminator = self.config.get("terminator", "\r\n")
        self._timeout = self.config.get("timeout", 0.1)

        # Serial connection (using pyserial)
        self._serial = None
        self._reader = None
        self._writer = None

        # Listener state
        self._listening = False
        self._listen_task: Optional[asyncio.Task] = None
        self._scan_callbacks: List[Callable[[str], None]] = []

        # Statistics
        self._scan_count = 0
        self._last_scan: Optional[str] = None
        self._last_scan_time: Optional[datetime] = None
        self._errors: List[Dict[str, Any]] = []

    @property
    def port(self) -> str:
        """Get the configured serial port."""
        return self._port

    @property
    def is_listening(self) -> bool:
        """Check if actively listening for scans."""
        return self._listening

    async def connect(self) -> bool:
        """
        Connect to the serial barcode scanner.

        Returns:
            True if connection successful

        Raises:
            DriverConnectionError: If connection fails
        """
        try:
            import serial_asyncio
        except ImportError:
            import asyncio
            import sys

            self._logger.info("pyserial-asyncio not found, installing...")
            try:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "pyserial-asyncio",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await proc.communicate()
                if proc.returncode != 0:
                    raise DriverConnectionError(
                        f"Failed to install pyserial-asyncio: {stderr.decode()}",
                        driver_name=self.name,
                    )
                import serial_asyncio
            except DriverConnectionError:
                raise
            except Exception as e:
                raise DriverConnectionError(
                    "pyserial-asyncio not installed and auto-install failed",
                    driver_name=self.name,
                    details={"error": str(e)},
                )

        try:
            self._logger.info(f"Connecting to barcode scanner on {self._port}")

            # Create serial connection using asyncio
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self._port,
                baudrate=self._baudrate,
            )

            self._connected = True
            self._logger.info(f"Barcode scanner connected on {self._port}")

            return True

        except Exception as e:
            raise DriverConnectionError(
                f"Failed to connect to barcode scanner on {self._port}: {e}",
                driver_name=self.name,
                details={"port": self._port, "baudrate": self._baudrate},
            )

    async def disconnect(self) -> None:
        """Disconnect from the barcode scanner."""
        await self.stop_listening()

        if self._writer:
            self._writer.close()
            # Wait for writer to close
            try:
                await asyncio.wait_for(self._writer.wait_closed(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

        self._reader = None
        self._writer = None
        self._connected = False

        self._logger.info(f"Barcode scanner disconnected: {self._port}")

    async def is_connected(self) -> bool:
        """Check if connected to the scanner."""
        return self._connected and self._writer is not None

    async def get_status(self) -> Dict[str, Any]:
        """
        Get barcode scanner status.

        Returns:
            Dictionary with status information
        """
        return {
            "connected": self._connected,
            "listening": self._listening,
            "port": self._port,
            "baudrate": self._baudrate,
            "scan_count": self._scan_count,
            "last_scan": self._last_scan,
            "last_scan_time": self._last_scan_time.isoformat() if self._last_scan_time else None,
            "error_count": len(self._errors),
        }

    def on_scan(self, callback: Callable[[str], None]) -> None:
        """
        Register a callback for barcode scans.

        Args:
            callback: Function to call with scanned barcode string
        """
        self._scan_callbacks.append(callback)
        self._logger.debug(f"Registered scan callback: {callback.__name__}")

    def remove_scan_callback(self, callback: Callable[[str], None]) -> bool:
        """
        Remove a scan callback.

        Args:
            callback: The callback to remove

        Returns:
            True if callback was found and removed
        """
        try:
            self._scan_callbacks.remove(callback)
            return True
        except ValueError:
            return False

    async def start_listening(self) -> None:
        """
        Start listening for barcode scans.

        Creates a background task that continuously reads from the serial port.
        """
        if not self._connected:
            raise DriverConnectionError(
                "Cannot start listening: not connected",
                driver_name=self.name,
            )

        if self._listening:
            self._logger.warning("Already listening for scans")
            return

        self._listening = True
        self._listen_task = asyncio.create_task(self._listen_loop())
        self._logger.info(f"Started listening for barcode scans on {self._port}")

    async def stop_listening(self) -> None:
        """Stop listening for barcode scans."""
        self._listening = False

        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None

        self._logger.info("Stopped listening for barcode scans")

    async def _listen_loop(self) -> None:
        """
        Background loop that reads barcodes from the serial port.

        Runs until stop_listening() is called or connection is lost.
        """
        buffer = b""
        terminator_bytes = self._terminator.encode("utf-8")

        while self._listening and self._reader:
            try:
                # Read available data (non-blocking with timeout)
                try:
                    data = await asyncio.wait_for(
                        self._reader.read(256),
                        timeout=0.5,
                    )
                except asyncio.TimeoutError:
                    continue

                if not data:
                    # Connection closed
                    self._logger.warning("Serial connection closed")
                    break

                buffer += data

                # Check for complete barcodes (terminated by terminator)
                while terminator_bytes in buffer:
                    line, buffer = buffer.split(terminator_bytes, 1)
                    barcode = line.decode("utf-8", errors="replace").strip()

                    if barcode:
                        await self._handle_scan(barcode)

            except asyncio.CancelledError:
                break

            except Exception as e:
                self._logger.error(f"Error reading from scanner: {e}")
                self._errors.append({
                    "time": datetime.now().isoformat(),
                    "error": str(e),
                })

                # Small delay before retrying
                await asyncio.sleep(0.5)

        self._listening = False
        self._logger.debug("Listen loop ended")

    async def _handle_scan(self, barcode: str) -> None:
        """
        Handle a scanned barcode.

        Args:
            barcode: The scanned barcode string
        """
        self._scan_count += 1
        self._last_scan = barcode
        self._last_scan_time = datetime.now()

        self._logger.info(f"Barcode scanned: {barcode}")

        # Call all registered callbacks
        for callback in self._scan_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(barcode)
                else:
                    callback(barcode)
            except Exception as e:
                self._logger.error(f"Scan callback error: {e}")

    async def simulate_scan(self, barcode: str) -> None:
        """
        Simulate a barcode scan (for testing).

        Args:
            barcode: The barcode string to simulate
        """
        self._logger.debug(f"Simulating barcode scan: {barcode}")
        await self._handle_scan(barcode)

    def get_available_commands(self) -> List[str]:
        """Get list of available commands."""
        return ["simulate_scan", "start_listening", "stop_listening"]


class MockBarcodeScannerDriver(BaseDriver):
    """
    Mock barcode scanner driver for testing without hardware.

    Simulates barcode scanning with configurable behavior.
    """

    def __init__(
        self,
        name: str = "",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the mock barcode scanner.

        Args:
            name: Driver instance name
            config: Configuration dictionary
        """
        super().__init__(name, config)

        self._scan_callbacks: List[Callable[[str], None]] = []
        self._scan_count = 0
        self._last_scan: Optional[str] = None
        self._last_scan_time: Optional[datetime] = None
        self._listening = False

    async def connect(self) -> bool:
        """Simulate connection."""
        self._logger.info("Mock barcode scanner connected")
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """Simulate disconnection."""
        self._listening = False
        self._connected = False
        self._logger.info("Mock barcode scanner disconnected")

    async def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected

    async def get_status(self) -> Dict[str, Any]:
        """Get status."""
        return {
            "connected": self._connected,
            "listening": self._listening,
            "type": "mock",
            "scan_count": self._scan_count,
            "last_scan": self._last_scan,
            "last_scan_time": self._last_scan_time.isoformat() if self._last_scan_time else None,
        }

    def on_scan(self, callback: Callable[[str], None]) -> None:
        """Register scan callback."""
        self._scan_callbacks.append(callback)

    async def start_listening(self) -> None:
        """Start listening (no-op for mock)."""
        self._listening = True
        self._logger.info("Mock scanner listening")

    async def stop_listening(self) -> None:
        """Stop listening."""
        self._listening = False

    async def simulate_scan(self, barcode: str) -> None:
        """
        Simulate a barcode scan.

        Args:
            barcode: The barcode string to simulate
        """
        if not self._connected:
            raise DriverConnectionError(
                "Cannot scan: not connected",
                driver_name=self.name,
            )

        self._scan_count += 1
        self._last_scan = barcode
        self._last_scan_time = datetime.now()

        self._logger.info(f"Mock scan: {barcode}")

        for callback in self._scan_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(barcode)
                else:
                    callback(barcode)
            except Exception as e:
                self._logger.error(f"Scan callback error: {e}")

    def get_available_commands(self) -> List[str]:
        """Get available commands."""
        return ["simulate_scan", "start_listening", "stop_listening"]
