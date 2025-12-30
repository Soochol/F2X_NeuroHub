"""
Base Driver Abstract Class for Station Service.

This module defines the abstract base class that all hardware drivers
must implement. It provides a common interface for connection management,
command execution, and status reporting.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DriverError(Exception):
    """Base exception for driver errors."""

    def __init__(self, message: str, driver_name: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.driver_name = driver_name
        self.details = details or {}


class DriverConnectionError(DriverError):
    """Exception raised when connection to hardware fails."""

    pass


class DriverCommandError(DriverError):
    """Exception raised when a command execution fails."""

    pass


class DriverTimeoutError(DriverError):
    """Exception raised when an operation times out."""

    pass


class BaseDriver(ABC):
    """
    Abstract base class for hardware drivers.

    All hardware drivers must inherit from this class and implement
    the required abstract methods. Drivers can be either synchronous
    or asynchronous, but the interface uses async for consistency.

    Attributes:
        name: Driver instance name (used for logging and identification)
        config: Driver configuration dictionary
        connected: Whether the driver is currently connected

    Example:
        class MyDriver(BaseDriver):
            async def connect(self) -> bool:
                # Connect to hardware
                self._connected = True
                return True

            async def disconnect(self) -> None:
                # Disconnect from hardware
                self._connected = False

            async def is_connected(self) -> bool:
                return self._connected

            async def get_status(self) -> Dict[str, Any]:
                return {"connected": self._connected}
    """

    def __init__(self, name: str = "", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base driver.

        Args:
            name: Driver instance name for logging and identification
            config: Configuration dictionary for the driver
        """
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self._connected = False
        self._logger = logging.getLogger(f"{__name__}.{self.name}")

    @property
    def connected(self) -> bool:
        """Check if the driver is connected."""
        return self._connected

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the hardware device.

        This method should establish a connection to the hardware and
        perform any necessary initialization.

        Returns:
            True if connection was successful, False otherwise

        Raises:
            DriverConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from the hardware device.

        This method should safely close the connection and release
        any resources held by the driver.
        """
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if the driver is currently connected.

        Returns:
            True if connected, False otherwise
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the hardware.

        Returns:
            Dictionary containing status information
        """
        pass

    async def execute_command(self, command: str, **kwargs: Any) -> Any:
        """
        Execute a command on the hardware.

        This is a convenience method that dispatches to specific methods
        based on the command name. Drivers can override this or implement
        specific command methods.

        Args:
            command: The command name to execute
            **kwargs: Command parameters

        Returns:
            Command result

        Raises:
            DriverCommandError: If command execution fails
        """
        if not self._connected:
            raise DriverConnectionError(
                "Driver not connected",
                driver_name=self.name,
            )

        method = getattr(self, command, None)
        if method is None:
            raise DriverCommandError(
                f"Unknown command: {command}",
                driver_name=self.name,
                details={"available_commands": self.get_available_commands()},
            )

        try:
            return await method(**kwargs) if callable(method) else method
        except Exception as e:
            raise DriverCommandError(
                f"Command '{command}' failed: {e}",
                driver_name=self.name,
                details={"command": command, "kwargs": kwargs},
            ) from e

    def get_available_commands(self) -> list[str]:
        """
        Get list of available commands for this driver.

        Returns:
            List of command names that can be executed
        """
        # Return public methods that don't start with underscore
        # and are not part of the base interface
        base_methods = {
            "connect",
            "disconnect",
            "is_connected",
            "get_status",
            "execute_command",
            "get_available_commands",
        }
        return [
            name
            for name in dir(self)
            if not name.startswith("_")
            and callable(getattr(self, name))
            and name not in base_methods
        ]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, connected={self._connected})"
