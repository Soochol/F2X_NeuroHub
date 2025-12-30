"""
Mock Sensor Interface Driver Module

Provides a mock sensor interface driver for calibration and inspection testing.
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from .base import BaseDriver


class MockSensorInterface(BaseDriver):
    """
    Mock Sensor Interface Driver for calibration and inspection testing.

    This driver simulates a sensor interface unit without requiring
    actual hardware. It generates random but realistic values
    for testing the sequence framework.

    Attributes:
        port: The simulated port address
        sample_rate: Sample rate in Hz
    """

    def __init__(
        self,
        name: str = "MockSensorInterface",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Mock Sensor Interface driver.

        Args:
            name: The driver name for identification
            config: Configuration dictionary
        """
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB1")
        self.sample_rate = self.config.get("sample_rate", 100)
        self._model = "MockSensor-2000"
        self._serial = f"SNS{random.randint(1000, 9999)}"
        self._calibration_offset = 0.0
        self._is_warmed_up = False

    async def connect(self) -> bool:
        """
        Simulate connection to the sensor interface.

        Returns:
            bool: True if connection was successful
        """
        await asyncio.sleep(0.1)  # Simulate connection delay
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """
        Simulate disconnection from the sensor interface.
        """
        await asyncio.sleep(0.02)  # Simulate disconnection delay
        self._connected = False
        self._is_warmed_up = False

    async def reset(self) -> None:
        """
        Reset the sensor interface to default state.
        """
        if not self._connected:
            raise RuntimeError("Sensor interface is not connected")

        await asyncio.sleep(0.05)  # Simulate reset delay
        self._calibration_offset = 0.0
        self._is_warmed_up = False

    async def identify(self) -> str:
        """
        Get the sensor interface identification string.

        Returns:
            str: The identification string
        """
        return f"MockSensors,{self._model},{self._serial},1.5.0"

    async def warmup(self, duration: float = 2.0) -> bool:
        """
        Perform sensor warmup.

        Args:
            duration: Warmup duration in seconds

        Returns:
            bool: True if warmup completed successfully
        """
        if not self._connected:
            raise RuntimeError("Sensor interface is not connected")

        await asyncio.sleep(duration)
        self._is_warmed_up = True
        return True

    async def read_sensor(self, reference: float = 100.0) -> float:
        """
        Read a single sensor value.

        Args:
            reference: Reference value for generating realistic readings

        Returns:
            float: The sensor reading
        """
        if not self._connected:
            raise RuntimeError("Sensor interface is not connected")

        await asyncio.sleep(1.0 / self.sample_rate)  # Simulate sample time

        # Generate realistic sensor value with some noise
        base_value = reference + self._calibration_offset
        noise = random.gauss(0, reference * 0.02)  # 2% noise
        drift = random.uniform(-reference * 0.01, reference * 0.01)  # 1% drift

        return round(base_value + noise + drift, 4)

    async def read_samples(
        self,
        num_samples: int = 10,
        reference: float = 100.0
    ) -> List[float]:
        """
        Read multiple sensor samples.

        Args:
            num_samples: Number of samples to read
            reference: Reference value

        Returns:
            List of sensor readings
        """
        samples = []
        for _ in range(num_samples):
            sample = await self.read_sensor(reference)
            samples.append(sample)
        return samples

    async def calibrate(
        self,
        reference_value: float,
        num_samples: int = 10
    ) -> Dict[str, Any]:
        """
        Perform calibration against a reference value.

        Args:
            reference_value: The known reference value
            num_samples: Number of samples for calibration

        Returns:
            Dict with calibration results
        """
        if not self._connected:
            raise RuntimeError("Sensor interface is not connected")

        if not self._is_warmed_up:
            raise RuntimeError("Sensor must be warmed up before calibration")

        # Take calibration samples
        samples = await self.read_samples(num_samples, reference_value)
        avg_reading = sum(samples) / len(samples)

        # Calculate and apply offset
        offset = reference_value - avg_reading
        self._calibration_offset = offset

        return {
            "reference": reference_value,
            "measured_avg": round(avg_reading, 4),
            "offset_applied": round(offset, 4),
            "samples": samples,
        }

    async def verify_calibration(
        self,
        reference_value: float,
        tolerance_percent: float = 5.0,
        num_samples: int = 10
    ) -> Dict[str, Any]:
        """
        Verify calibration accuracy.

        Args:
            reference_value: The expected reference value
            tolerance_percent: Acceptable deviation percentage
            num_samples: Number of samples for verification

        Returns:
            Dict with verification results
        """
        if not self._connected:
            raise RuntimeError("Sensor interface is not connected")

        # Take verification samples
        samples = await self.read_samples(num_samples, reference_value)
        avg_reading = sum(samples) / len(samples)
        std_dev = (sum((s - avg_reading) ** 2 for s in samples) / len(samples)) ** 0.5

        # Calculate deviation
        deviation = abs(avg_reading - reference_value)
        deviation_percent = (deviation / reference_value) * 100 if reference_value != 0 else 0

        passed = deviation_percent <= tolerance_percent

        return {
            "reference": reference_value,
            "measured_avg": round(avg_reading, 4),
            "std_dev": round(std_dev, 4),
            "deviation": round(deviation, 4),
            "deviation_percent": round(deviation_percent, 2),
            "tolerance_percent": tolerance_percent,
            "passed": passed,
            "samples": samples,
        }

    @property
    def is_warmed_up(self) -> bool:
        """Check if sensor is warmed up."""
        return self._is_warmed_up

    @property
    def calibration_offset(self) -> float:
        """Get current calibration offset."""
        return self._calibration_offset
