"""
Mock Multimeter Driver Module

Provides a mock digital multimeter driver for PCB voltage testing.
"""

import asyncio
import random
from typing import Any, Dict, Optional

from .base import BaseDriver


class MockMultimeter(BaseDriver):
    """
    Mock Digital Multimeter Driver for PCB voltage testing.

    This driver simulates a digital multimeter without requiring
    actual hardware. It generates random but realistic values
    for testing the sequence framework.

    Attributes:
        port: The simulated port address
        measurement_delay: Simulated measurement delay in seconds
    """

    def __init__(
        self,
        name: str = "MockMultimeter",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Mock Multimeter driver.

        Args:
            name: The driver name for identification
            config: Configuration dictionary with optional 'port' key
        """
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB0")
        self.measurement_delay = self.config.get("measurement_delay", 0.1)
        self._model = "MockMultimeter-5000"
        self._serial = f"PCB{random.randint(1000, 9999)}"
        self._mode = "DC_VOLTAGE"
        self._range = "AUTO"

    async def connect(self) -> bool:
        """
        Simulate connection to the multimeter.

        Returns:
            bool: True if connection was successful
        """
        await asyncio.sleep(0.05)  # Simulate connection delay
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """
        Simulate disconnection from the multimeter.
        """
        await asyncio.sleep(0.02)  # Simulate disconnection delay
        self._connected = False

    async def reset(self) -> None:
        """
        Reset the multimeter to default state.
        """
        if not self._connected:
            raise RuntimeError("Multimeter is not connected")

        await asyncio.sleep(0.05)  # Simulate reset delay
        self._mode = "DC_VOLTAGE"
        self._range = "AUTO"

    async def identify(self) -> str:
        """
        Get the multimeter identification string.

        Returns:
            str: The identification string in SCPI format
        """
        return f"MockInstruments,{self._model},{self._serial},2.0.0"

    async def measure_voltage(
        self,
        mode: str = "DC",
        test_point: int = 1
    ) -> float:
        """
        Measure voltage at a specific test point.

        Args:
            mode: Measurement mode ('DC' or 'AC')
            test_point: Test point number (1-20)

        Returns:
            float: The measured voltage value
        """
        if not self._connected:
            raise RuntimeError("Multimeter is not connected")

        await asyncio.sleep(self.measurement_delay)

        # Generate realistic PCB voltage values based on test point
        # Simulate different components having different expected voltages
        base_voltages = {
            1: 3.3,   # Logic level
            2: 5.0,   # USB power
            3: 12.0,  # Main power
            4: 1.8,   # Low voltage logic
            5: 3.3,   # Logic level
        }

        base = base_voltages.get(test_point % 5 + 1, 3.3)
        noise = random.uniform(-0.05, 0.05) * base
        return round(base + noise, 4)

    async def measure_all_points(self, num_points: int = 5) -> Dict[int, float]:
        """
        Measure voltage at all test points.

        Args:
            num_points: Number of test points to measure

        Returns:
            Dict mapping test point number to voltage reading
        """
        results = {}
        for i in range(1, num_points + 1):
            results[i] = await self.measure_voltage(test_point=i)
        return results

    async def set_range(self, range_val: str) -> None:
        """
        Set the measurement range.

        Args:
            range_val: Range setting ('AUTO', '2V', '20V', '200V')
        """
        if not self._connected:
            raise RuntimeError("Multimeter is not connected")

        valid_ranges = ["AUTO", "2V", "20V", "200V"]
        if range_val not in valid_ranges:
            raise ValueError(f"Invalid range: {range_val}. Must be one of {valid_ranges}")

        await asyncio.sleep(0.02)
        self._range = range_val

    @property
    def current_range(self) -> str:
        """Get the current measurement range."""
        return self._range
