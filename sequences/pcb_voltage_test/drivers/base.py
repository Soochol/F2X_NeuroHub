"""
Base Driver Module

Provides the abstract base class for all hardware drivers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDriver(ABC):
    """
    Abstract base class for hardware drivers.

    All hardware drivers must inherit from this class and implement
    the required abstract methods for connection management.

    Attributes:
        name: The driver name for identification
        config: Configuration dictionary for the driver
    """

    def __init__(self, name: str = "BaseDriver", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base driver.

        Args:
            name: The driver name for identification
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self._connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the hardware.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Disconnect from the hardware.

        This method should clean up any resources and close the connection.
        """
        ...

    @abstractmethod
    async def reset(self) -> None:
        """
        Reset the hardware to its default state.

        This method should restore the hardware to a known good state.
        """
        ...

    async def identify(self) -> str:
        """
        Get the identification string of the hardware.

        Returns:
            str: The identification string of the hardware
        """
        return "Unknown"

    async def is_connected(self) -> bool:
        """
        Check if the driver is currently connected to the hardware.

        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, connected={self._connected})"
