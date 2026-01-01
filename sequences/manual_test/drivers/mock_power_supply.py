"""
Mock Power Supply Driver Module

Provides a simulated programmable power supply for testing the manual control page.
Demonstrates various command types: measurement, control, and configuration.
"""

import asyncio
import random
from typing import Any, Dict, Optional

from .base import BaseDriver


class MockPowerSupply(BaseDriver):
    """
    Mock Programmable Power Supply Driver.

    Simulates a programmable DC power supply with voltage and current control.
    Designed for testing the enhanced manual control UI.

    Attributes:
        port: The simulated port address
        max_voltage: Maximum voltage limit (V)
        max_current: Maximum current limit (A)
    """

    def __init__(
        self,
        name: str = "MockPowerSupply",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Mock Power Supply driver.

        Args:
            name: The driver name for identification
            config: Configuration dictionary with optional settings
        """
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB0")
        self.max_voltage = self.config.get("max_voltage", 30.0)
        self.max_current = self.config.get("max_current", 5.0)

        # Internal state
        self._model = "MockPSU-3005"
        self._serial = f"PSU{random.randint(1000, 9999)}"
        self._output_enabled = False
        self._set_voltage = 0.0
        self._set_current = 1.0
        self._actual_voltage = 0.0
        self._actual_current = 0.0
        self._mode = "CV"  # CV (Constant Voltage) or CC (Constant Current)
        self._protection_triggered = False

    async def connect(self) -> bool:
        """
        Simulate connection to the power supply.

        Returns:
            bool: True if connection was successful
        """
        await asyncio.sleep(0.1)  # Simulate connection delay
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """
        Simulate disconnection from the power supply.
        Turns off output before disconnecting.
        """
        if self._output_enabled:
            await self.output_off()
        await asyncio.sleep(0.05)
        self._connected = False

    async def reset(self) -> None:
        """
        Reset the power supply to default state.
        Disables output and resets all settings.
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        await asyncio.sleep(0.1)
        self._output_enabled = False
        self._set_voltage = 0.0
        self._set_current = 1.0
        self._actual_voltage = 0.0
        self._actual_current = 0.0
        self._mode = "CV"
        self._protection_triggered = False

    async def identify(self) -> str:
        """
        Get the power supply identification string.

        Returns:
            str: The identification string in SCPI format
        """
        return f"MockInstruments,{self._model},{self._serial},1.0.0"

    # ========================================================================
    # Measurement Commands
    # ========================================================================

    async def measure_voltage(self) -> float:
        """
        Measure the actual output voltage.

        Returns:
            float: The measured voltage in volts
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        await asyncio.sleep(0.05)

        if self._output_enabled:
            # Add some realistic noise
            noise = random.uniform(-0.01, 0.01) * self._set_voltage
            self._actual_voltage = max(0, self._set_voltage + noise)
        else:
            self._actual_voltage = 0.0

        return round(self._actual_voltage, 3)

    async def measure_current(self) -> float:
        """
        Measure the actual output current.

        Returns:
            float: The measured current in amperes
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        await asyncio.sleep(0.05)

        if self._output_enabled and self._actual_voltage > 0:
            # Simulate load current (random for demo)
            load_current = random.uniform(0.1, 0.5) * self._set_current
            noise = random.uniform(-0.001, 0.001)
            self._actual_current = max(0, min(load_current + noise, self._set_current))
        else:
            self._actual_current = 0.0

        return round(self._actual_current, 4)

    async def measure_power(self) -> float:
        """
        Measure the actual output power.

        Returns:
            float: The measured power in watts
        """
        voltage = await self.measure_voltage()
        current = await self.measure_current()
        return round(voltage * current, 3)

    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the power supply.

        Returns:
            Dict with voltage, current, power, and status flags
        """
        return {
            "voltage": await self.measure_voltage(),
            "current": await self.measure_current(),
            "power": await self.measure_power(),
            "output_enabled": self._output_enabled,
            "mode": self._mode,
            "protection_triggered": self._protection_triggered,
            "set_voltage": self._set_voltage,
            "set_current": self._set_current,
        }

    # ========================================================================
    # Control Commands
    # ========================================================================

    async def output_on(self) -> bool:
        """
        Enable the power supply output.

        Returns:
            bool: True if output was enabled successfully
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        if self._protection_triggered:
            raise RuntimeError("Cannot enable output: protection triggered")

        await asyncio.sleep(0.05)
        self._output_enabled = True
        return True

    async def output_off(self) -> bool:
        """
        Disable the power supply output.

        Returns:
            bool: True if output was disabled successfully
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        await asyncio.sleep(0.05)
        self._output_enabled = False
        self._actual_voltage = 0.0
        self._actual_current = 0.0
        return True

    async def set_voltage(self, voltage: float) -> float:
        """
        Set the output voltage.

        Args:
            voltage: Target voltage in volts (0 to max_voltage)

        Returns:
            float: The actual set voltage
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        if voltage < 0 or voltage > self.max_voltage:
            raise ValueError(f"Voltage must be between 0 and {self.max_voltage}V")

        await asyncio.sleep(0.05)
        self._set_voltage = voltage
        return self._set_voltage

    async def set_current(self, current: float) -> float:
        """
        Set the current limit.

        Args:
            current: Target current limit in amperes (0 to max_current)

        Returns:
            float: The actual set current limit
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        if current < 0 or current > self.max_current:
            raise ValueError(f"Current must be between 0 and {self.max_current}A")

        await asyncio.sleep(0.05)
        self._set_current = current
        return self._set_current

    async def ramp_voltage(self, target: float, step: float = 0.5, delay: float = 0.1) -> float:
        """
        Gradually ramp voltage to target value.

        Args:
            target: Target voltage in volts
            step: Voltage step size in volts
            delay: Delay between steps in seconds

        Returns:
            float: Final voltage value
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        if target < 0 or target > self.max_voltage:
            raise ValueError(f"Target voltage must be between 0 and {self.max_voltage}V")

        current = self._set_voltage

        while abs(current - target) > step:
            if current < target:
                current = min(current + step, target)
            else:
                current = max(current - step, target)

            self._set_voltage = current
            await asyncio.sleep(delay)

        self._set_voltage = target
        return self._set_voltage

    # ========================================================================
    # Configuration Commands
    # ========================================================================

    async def set_ovp(self, voltage: float) -> float:
        """
        Set Over-Voltage Protection threshold.

        Args:
            voltage: OVP threshold in volts

        Returns:
            float: The set OVP threshold
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        if voltage < 0 or voltage > self.max_voltage * 1.1:
            raise ValueError(f"OVP must be between 0 and {self.max_voltage * 1.1}V")

        await asyncio.sleep(0.02)
        return voltage

    async def set_ocp(self, current: float) -> float:
        """
        Set Over-Current Protection threshold.

        Args:
            current: OCP threshold in amperes

        Returns:
            float: The set OCP threshold
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        if current < 0 or current > self.max_current * 1.1:
            raise ValueError(f"OCP must be between 0 and {self.max_current * 1.1}A")

        await asyncio.sleep(0.02)
        return current

    async def clear_protection(self) -> bool:
        """
        Clear protection status and allow output to be enabled again.

        Returns:
            bool: True if protection was cleared
        """
        if not self._connected:
            raise RuntimeError("Power supply is not connected")

        await asyncio.sleep(0.05)
        self._protection_triggered = False
        return True

    @property
    def output_enabled(self) -> bool:
        """Check if output is currently enabled."""
        return self._output_enabled

    @property
    def mode(self) -> str:
        """Get current operating mode (CV or CC)."""
        return self._mode
