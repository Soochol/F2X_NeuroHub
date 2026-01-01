"""
Mock GPIO Controller Driver Module

Provides a simulated GPIO controller for testing the manual control page.
Demonstrates digital I/O operations with multiple channels.
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from .base import BaseDriver


class MockGPIOController(BaseDriver):
    """
    Mock GPIO Controller Driver.

    Simulates a multi-channel GPIO controller with digital inputs and outputs.
    Designed for testing the enhanced manual control UI.

    Attributes:
        num_inputs: Number of digital input channels
        num_outputs: Number of digital output channels
    """

    def __init__(
        self,
        name: str = "MockGPIOController",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Mock GPIO Controller driver.

        Args:
            name: The driver name for identification
            config: Configuration dictionary with optional settings
        """
        super().__init__(name=name, config=config)
        self.num_inputs = self.config.get("num_inputs", 8)
        self.num_outputs = self.config.get("num_outputs", 8)

        # Internal state
        self._model = "MockGPIO-16CH"
        self._serial = f"GPIO{random.randint(1000, 9999)}"
        self._output_states: List[bool] = [False] * self.num_outputs
        self._input_states: List[bool] = [False] * self.num_inputs
        self._output_labels: List[str] = [f"OUT{i}" for i in range(self.num_outputs)]
        self._input_labels: List[str] = [f"IN{i}" for i in range(self.num_inputs)]

    async def connect(self) -> bool:
        """
        Simulate connection to the GPIO controller.

        Returns:
            bool: True if connection was successful
        """
        await asyncio.sleep(0.05)
        self._connected = True
        # Simulate initial input states
        self._input_states = [random.choice([True, False]) for _ in range(self.num_inputs)]
        return True

    async def disconnect(self) -> None:
        """
        Simulate disconnection from the GPIO controller.
        Turns off all outputs before disconnecting.
        """
        if self._connected:
            await self.all_outputs_off()
        await asyncio.sleep(0.02)
        self._connected = False

    async def reset(self) -> None:
        """
        Reset the GPIO controller to default state.
        Turns off all outputs and clears labels.
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        await asyncio.sleep(0.05)
        self._output_states = [False] * self.num_outputs
        self._output_labels = [f"OUT{i}" for i in range(self.num_outputs)]
        self._input_labels = [f"IN{i}" for i in range(self.num_inputs)]

    async def identify(self) -> str:
        """
        Get the GPIO controller identification string.

        Returns:
            str: The identification string
        """
        return f"MockDevices,{self._model},{self._serial},2.1.0"

    # ========================================================================
    # Measurement / Read Commands
    # ========================================================================

    async def read_input(self, channel: int) -> bool:
        """
        Read the state of a digital input channel.

        Args:
            channel: Input channel number (0 to num_inputs-1)

        Returns:
            bool: The input state (True = HIGH, False = LOW)
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_inputs:
            raise ValueError(f"Channel must be between 0 and {self.num_inputs - 1}")

        await asyncio.sleep(0.01)
        # Simulate some random state changes
        if random.random() < 0.1:
            self._input_states[channel] = not self._input_states[channel]
        return self._input_states[channel]

    async def read_all_inputs(self) -> Dict[int, bool]:
        """
        Read the state of all digital input channels.

        Returns:
            Dict mapping channel number to input state
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        await asyncio.sleep(0.02)
        return {i: state for i, state in enumerate(self._input_states)}

    async def read_output(self, channel: int) -> bool:
        """
        Read the current state of a digital output channel.

        Args:
            channel: Output channel number (0 to num_outputs-1)

        Returns:
            bool: The output state (True = HIGH, False = LOW)
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_outputs:
            raise ValueError(f"Channel must be between 0 and {self.num_outputs - 1}")

        await asyncio.sleep(0.01)
        return self._output_states[channel]

    async def read_all_outputs(self) -> Dict[int, bool]:
        """
        Read the current state of all digital output channels.

        Returns:
            Dict mapping channel number to output state
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        await asyncio.sleep(0.02)
        return {i: state for i, state in enumerate(self._output_states)}

    async def get_io_status(self) -> Dict[str, Any]:
        """
        Get comprehensive I/O status.

        Returns:
            Dict with all input and output states, plus labels
        """
        return {
            "inputs": await self.read_all_inputs(),
            "outputs": await self.read_all_outputs(),
            "input_labels": self._input_labels,
            "output_labels": self._output_labels,
        }

    # ========================================================================
    # Control Commands
    # ========================================================================

    async def set_output(self, channel: int, state: bool) -> bool:
        """
        Set the state of a digital output channel.

        Args:
            channel: Output channel number (0 to num_outputs-1)
            state: Desired state (True = HIGH, False = LOW)

        Returns:
            bool: The actual output state after setting
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_outputs:
            raise ValueError(f"Channel must be between 0 and {self.num_outputs - 1}")

        await asyncio.sleep(0.01)
        self._output_states[channel] = state
        return self._output_states[channel]

    async def toggle_output(self, channel: int) -> bool:
        """
        Toggle the state of a digital output channel.

        Args:
            channel: Output channel number (0 to num_outputs-1)

        Returns:
            bool: The new output state after toggling
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_outputs:
            raise ValueError(f"Channel must be between 0 and {self.num_outputs - 1}")

        await asyncio.sleep(0.01)
        self._output_states[channel] = not self._output_states[channel]
        return self._output_states[channel]

    async def pulse_output(self, channel: int, duration: float = 0.5) -> bool:
        """
        Generate a pulse on a digital output channel.

        Args:
            channel: Output channel number (0 to num_outputs-1)
            duration: Pulse duration in seconds

        Returns:
            bool: True if pulse was successful
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_outputs:
            raise ValueError(f"Channel must be between 0 and {self.num_outputs - 1}")

        if duration < 0.01 or duration > 10.0:
            raise ValueError("Duration must be between 0.01 and 10.0 seconds")

        original_state = self._output_states[channel]
        self._output_states[channel] = True
        await asyncio.sleep(duration)
        self._output_states[channel] = original_state
        return True

    async def set_multiple_outputs(self, states: Dict[int, bool]) -> Dict[int, bool]:
        """
        Set multiple output channels at once.

        Args:
            states: Dict mapping channel number to desired state

        Returns:
            Dict with actual states after setting
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        results = {}
        for channel, state in states.items():
            if 0 <= channel < self.num_outputs:
                self._output_states[channel] = state
                results[channel] = state

        await asyncio.sleep(0.02)
        return results

    async def all_outputs_on(self) -> bool:
        """
        Turn on all digital outputs.

        Returns:
            bool: True if successful
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        await asyncio.sleep(0.02)
        self._output_states = [True] * self.num_outputs
        return True

    async def all_outputs_off(self) -> bool:
        """
        Turn off all digital outputs.

        Returns:
            bool: True if successful
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        await asyncio.sleep(0.02)
        self._output_states = [False] * self.num_outputs
        return True

    # ========================================================================
    # Configuration Commands
    # ========================================================================

    async def set_output_label(self, channel: int, label: str) -> str:
        """
        Set a label for an output channel.

        Args:
            channel: Output channel number
            label: Label string (max 16 characters)

        Returns:
            str: The set label
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_outputs:
            raise ValueError(f"Channel must be between 0 and {self.num_outputs - 1}")

        if len(label) > 16:
            label = label[:16]

        await asyncio.sleep(0.01)
        self._output_labels[channel] = label
        return label

    async def set_input_label(self, channel: int, label: str) -> str:
        """
        Set a label for an input channel.

        Args:
            channel: Input channel number
            label: Label string (max 16 characters)

        Returns:
            str: The set label
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_inputs:
            raise ValueError(f"Channel must be between 0 and {self.num_inputs - 1}")

        if len(label) > 16:
            label = label[:16]

        await asyncio.sleep(0.01)
        self._input_labels[channel] = label
        return label

    async def configure_input_debounce(self, channel: int, debounce_ms: int) -> int:
        """
        Configure input debounce time.

        Args:
            channel: Input channel number
            debounce_ms: Debounce time in milliseconds (0-1000)

        Returns:
            int: The configured debounce time
        """
        if not self._connected:
            raise RuntimeError("GPIO controller is not connected")

        if channel < 0 or channel >= self.num_inputs:
            raise ValueError(f"Channel must be between 0 and {self.num_inputs - 1}")

        if debounce_ms < 0 or debounce_ms > 1000:
            raise ValueError("Debounce time must be between 0 and 1000ms")

        await asyncio.sleep(0.01)
        return debounce_ms
