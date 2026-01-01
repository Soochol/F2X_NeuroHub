"""
Manual Test Sequence

A demonstration sequence designed for testing the enhanced manual control page.
Features multiple hardware devices with step-by-step execution support.
"""

import asyncio
from typing import Any, Dict, Optional

from station_service.sequence.decorators import sequence, step


@sequence(
    name="manual_test",
    description="Demonstration sequence for manual control page testing",
    version="1.0.0"
)
class ManualTestSequence:
    """
    Manual Test Sequence for testing the enhanced manual control page.

    This sequence demonstrates:
    - Multiple hardware devices (power supply, GPIO)
    - Various command types (measurement, control, configuration)
    - Manual mode step execution with skip/retry support
    - Parameter overrides at runtime
    """

    name = "Manual Test Sequence"
    version = "1.0.0"
    description = "Demonstration sequence for manual control page testing"

    def __init__(
        self,
        hardware: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the sequence."""
        self.hardware = hardware or {}
        self.parameters = parameters or {}
        self.power_supply = self.hardware.get("power_supply")
        self.gpio = self.hardware.get("gpio")
        self._test_results: Dict[str, Any] = {}

    @step(order=1, timeout=30.0)
    async def initialize_hardware(self) -> Dict[str, Any]:
        """
        Initialize and verify all hardware connections.

        Returns:
            Dict with hardware status information
        """
        results = {
            "power_supply": {"connected": False},
            "gpio": {"connected": False},
        }

        # Initialize power supply
        if self.power_supply:
            try:
                await self.power_supply.connect()
                idn = await self.power_supply.identify()
                results["power_supply"] = {
                    "connected": True,
                    "idn": idn,
                }
            except Exception as e:
                results["power_supply"]["error"] = str(e)

        # Initialize GPIO
        if self.gpio:
            try:
                await self.gpio.connect()
                idn = await self.gpio.identify()
                results["gpio"] = {
                    "connected": True,
                    "idn": idn,
                }
            except Exception as e:
                results["gpio"]["error"] = str(e)

        self._test_results["initialization"] = results
        return results

    @step(order=2, timeout=60.0, retry=1)
    async def test_power_supply(self) -> Dict[str, Any]:
        """
        Test the power supply with configurable voltage and current.

        Returns:
            Dict with test results
        """
        # Get parameters from sequence parameters
        test_voltage = self.parameters.get("test_voltage", 12.0)
        test_current = self.parameters.get("test_current", 1.0)

        if not self.power_supply:
            return {"passed": False, "error": "Power supply not available"}

        results = {
            "test_voltage": test_voltage,
            "test_current": test_current,
            "measurements": {},
        }

        try:
            # Configure power supply
            await self.power_supply.set_voltage(test_voltage)
            await self.power_supply.set_current(test_current)

            # Enable output
            await self.power_supply.output_on()
            await asyncio.sleep(0.5)  # Stabilization time

            # Take measurements
            measured_voltage = await self.power_supply.measure_voltage()
            measured_current = await self.power_supply.measure_current()
            measured_power = await self.power_supply.measure_power()

            results["measurements"] = {
                "voltage": measured_voltage,
                "current": measured_current,
                "power": measured_power,
            }

            # Validate voltage within tolerance
            voltage_tolerance = 0.05 * test_voltage  # 5% tolerance
            voltage_ok = abs(measured_voltage - test_voltage) <= voltage_tolerance

            results["voltage_ok"] = voltage_ok
            results["passed"] = voltage_ok

            # Disable output
            await self.power_supply.output_off()

        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)

        self._test_results["power_supply"] = results
        return results

    @step(order=3, timeout=45.0, retry=1)
    async def test_gpio_outputs(self) -> Dict[str, Any]:
        """
        Test GPIO output channels by toggling them.

        Returns:
            Dict with test results for each channel
        """
        channels_to_test = self.parameters.get("channels_to_test", 4)

        if not self.gpio:
            return {"passed": False, "error": "GPIO controller not available"}

        results = {
            "channels_tested": channels_to_test,
            "channel_results": {},
        }

        try:
            all_passed = True

            for channel in range(channels_to_test):
                channel_result = {
                    "channel": channel,
                    "tests": [],
                }

                # Test turning on
                await self.gpio.set_output(channel, True)
                await asyncio.sleep(0.1)
                state_on = await self.gpio.read_output(channel)
                channel_result["tests"].append({
                    "action": "set_high",
                    "expected": True,
                    "actual": state_on,
                    "passed": state_on == True,
                })

                # Test turning off
                await self.gpio.set_output(channel, False)
                await asyncio.sleep(0.1)
                state_off = await self.gpio.read_output(channel)
                channel_result["tests"].append({
                    "action": "set_low",
                    "expected": False,
                    "actual": state_off,
                    "passed": state_off == False,
                })

                # Test toggle
                await self.gpio.toggle_output(channel)
                toggled_state = await self.gpio.read_output(channel)
                channel_result["tests"].append({
                    "action": "toggle",
                    "expected": True,
                    "actual": toggled_state,
                    "passed": toggled_state == True,
                })

                # Return to off
                await self.gpio.set_output(channel, False)

                channel_passed = all(t["passed"] for t in channel_result["tests"])
                channel_result["passed"] = channel_passed
                results["channel_results"][channel] = channel_result

                if not channel_passed:
                    all_passed = False

            results["passed"] = all_passed

        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)

        self._test_results["gpio_outputs"] = results
        return results

    @step(order=4, timeout=30.0)
    async def test_gpio_inputs(self) -> Dict[str, Any]:
        """
        Read and report all GPIO input states.

        Returns:
            Dict with all input states
        """
        if not self.gpio:
            return {"passed": False, "error": "GPIO controller not available"}

        results = {}

        try:
            input_states = await self.gpio.read_all_inputs()
            results["inputs"] = input_states
            results["passed"] = True

            # Count highs and lows
            highs = sum(1 for v in input_states.values() if v)
            lows = len(input_states) - highs
            results["summary"] = {
                "total": len(input_states),
                "high": highs,
                "low": lows,
            }

        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)

        self._test_results["gpio_inputs"] = results
        return results

    @step(order=5, timeout=90.0, retry=2)
    async def combined_test(self) -> Dict[str, Any]:
        """
        Combined test using power supply and GPIO together.

        Sets power supply voltage and uses GPIO to control/monitor.

        Returns:
            Dict with combined test results
        """
        output_voltage = self.parameters.get("output_voltage", 5.0)
        gpio_channel = self.parameters.get("gpio_channel", 0)

        results = {
            "output_voltage": output_voltage,
            "gpio_channel": gpio_channel,
            "steps": [],
        }

        try:
            # Step 1: Set GPIO high to enable DUT power
            if self.gpio:
                await self.gpio.set_output(gpio_channel, True)
                results["steps"].append({
                    "action": "GPIO enable",
                    "passed": True,
                })

            await asyncio.sleep(0.2)

            # Step 2: Set and enable power supply
            if self.power_supply:
                await self.power_supply.set_voltage(output_voltage)
                await self.power_supply.set_current(2.0)
                await self.power_supply.output_on()
                results["steps"].append({
                    "action": "Power supply enable",
                    "passed": True,
                })

            await asyncio.sleep(0.5)

            # Step 3: Measure power
            if self.power_supply:
                voltage = await self.power_supply.measure_voltage()
                current = await self.power_supply.measure_current()
                power = await self.power_supply.measure_power()
                results["measurements"] = {
                    "voltage": voltage,
                    "current": current,
                    "power": power,
                }
                results["steps"].append({
                    "action": "Measure power",
                    "passed": True,
                })

            # Step 4: Read GPIO inputs
            if self.gpio:
                inputs = await self.gpio.read_all_inputs()
                results["gpio_inputs"] = inputs
                results["steps"].append({
                    "action": "Read GPIO inputs",
                    "passed": True,
                })

            # Cleanup: Disable power and GPIO
            if self.power_supply:
                await self.power_supply.output_off()

            if self.gpio:
                await self.gpio.set_output(gpio_channel, False)

            results["passed"] = all(s["passed"] for s in results["steps"])

        except Exception as e:
            results["passed"] = False
            results["error"] = str(e)

            # Cleanup on error
            try:
                if self.power_supply:
                    await self.power_supply.output_off()
                if self.gpio:
                    await self.gpio.set_output(gpio_channel, False)
            except Exception:
                pass

        self._test_results["combined"] = results
        return results

    @step(order=99, timeout=30.0, cleanup=True)
    async def cleanup(self) -> Dict[str, Any]:
        """
        Clean up all hardware and generate final report.

        This step always runs, even if previous steps failed.

        Returns:
            Dict with cleanup status and final summary
        """
        results = {
            "cleanup": [],
            "summary": {},
        }

        # Reset power supply
        if self.power_supply:
            try:
                await self.power_supply.output_off()
                await self.power_supply.reset()
                results["cleanup"].append({"device": "power_supply", "status": "ok"})
            except Exception as e:
                results["cleanup"].append({"device": "power_supply", "status": "error", "error": str(e)})

        # Reset GPIO
        if self.gpio:
            try:
                await self.gpio.all_outputs_off()
                await self.gpio.reset()
                results["cleanup"].append({"device": "gpio", "status": "ok"})
            except Exception as e:
                results["cleanup"].append({"device": "gpio", "status": "error", "error": str(e)})

        # Generate summary
        results["summary"] = {
            "total_tests": len(self._test_results),
            "test_results": self._test_results,
        }

        return results
