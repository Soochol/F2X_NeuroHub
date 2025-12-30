"""
Mock DMM Driver Module

Provides a mock digital multimeter driver for testing purposes.
"""

import asyncio
import random
from typing import Any, Dict, Optional

from .base import BaseDriver


class MockDMM(BaseDriver):
    """
    Mock Digital Multimeter Driver for testing.

    This driver simulates a digital multimeter without requiring
    actual hardware. It generates random but realistic values
    for testing the sequence framework.

    Attributes:
        port: The simulated port address
        measurement_delay: Simulated measurement delay in seconds
    """

    def __init__(
        self,
        name: str = "MockDMM",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Mock DMM driver.

        Args:
            name: The driver name for identification
            config: Configuration dictionary with optional 'port' key
        """
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB0")
        self.measurement_delay = self.config.get("measurement_delay", 0.1)
        self._model = "MockDMM-3000"
        self._serial = f"MOCK{random.randint(1000, 9999)}"
        self._mode = "DC_VOLTAGE"

    async def connect(self) -> bool:
        """
        Simulate connection to the DMM.

        Returns:
            bool: True if connection was successful
        """
        await asyncio.sleep(0.05)  # Simulate connection delay
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """
        Simulate disconnection from the DMM.
        """
        await asyncio.sleep(0.02)  # Simulate disconnection delay
        self._connected = False

    async def reset(self) -> None:
        """
        Reset the DMM to default state.
        """
        if not self._connected:
            raise RuntimeError("DMM is not connected")

        await asyncio.sleep(0.05)  # Simulate reset delay
        self._mode = "DC_VOLTAGE"

    async def identify(self) -> str:
        """
        Get the DMM identification string.

        Returns:
            str: The identification string in SCPI format
        """
        return f"MockInstruments,{self._model},{self._serial},1.0.0"

    async def measure_voltage(
        self,
        mode: str = "DC",
        range_val: Optional[float] = None
    ) -> float:
        """
        Measure voltage.

        Args:
            mode: Measurement mode ('DC' or 'AC')
            range_val: Optional measurement range in volts

        Returns:
            float: The measured voltage value
        """
        if not self._connected:
            raise RuntimeError("DMM is not connected")

        await asyncio.sleep(self.measurement_delay)

        # Generate a realistic mock voltage value
        base_voltage = 3.3 if mode == "DC" else 120.0
        noise = random.uniform(-0.05, 0.05) * base_voltage
        return round(base_voltage + noise, 4)

    async def measure_current(
        self,
        mode: str = "DC",
        range_val: Optional[float] = None
    ) -> float:
        """
        Measure current.

        Args:
            mode: Measurement mode ('DC' or 'AC')
            range_val: Optional measurement range in amperes

        Returns:
            float: The measured current value
        """
        if not self._connected:
            raise RuntimeError("DMM is not connected")

        await asyncio.sleep(self.measurement_delay)

        # Generate a realistic mock current value
        base_current = 0.1 if mode == "DC" else 0.5
        noise = random.uniform(-0.01, 0.01) * base_current
        return round(base_current + noise, 6)

    async def measure_resistance(self, range_val: Optional[float] = None) -> float:
        """
        Measure resistance.

        Args:
            range_val: Optional measurement range in ohms

        Returns:
            float: The measured resistance value
        """
        if not self._connected:
            raise RuntimeError("DMM is not connected")

        await asyncio.sleep(self.measurement_delay)

        # Generate a realistic mock resistance value
        base_resistance = 1000.0  # 1k ohm
        noise = random.uniform(-0.01, 0.01) * base_resistance
        return round(base_resistance + noise, 2)

    async def set_mode(self, mode: str) -> None:
        """
        Set the measurement mode.

        Args:
            mode: The measurement mode to set
                  (DC_VOLTAGE, AC_VOLTAGE, DC_CURRENT, AC_CURRENT, RESISTANCE)
        """
        if not self._connected:
            raise RuntimeError("DMM is not connected")

        valid_modes = ["DC_VOLTAGE", "AC_VOLTAGE", "DC_CURRENT", "AC_CURRENT", "RESISTANCE"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")

        await asyncio.sleep(0.02)  # Simulate mode change delay
        self._mode = mode

    @property
    def current_mode(self) -> str:
        """Get the current measurement mode."""
        return self._mode
