"""
PCB Voltage Test Sequence Module

Test sequence for measuring and validating PCB voltage levels
at multiple test points with pass/fail determination.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from station_service.sequence.decorators import parameter, sequence, step

from .drivers.mock_multimeter import MockMultimeter


logger = logging.getLogger(__name__)


@sequence(
    name="pcb_voltage_test",
    description="PCB voltage measurement test sequence for quality assurance",
    version="1.0.0"
)
class PCBVoltageTestSequence:
    """
    PCB Voltage Test Sequence for quality assurance.

    This sequence performs voltage measurements at multiple test points
    on a PCB and validates them against configurable thresholds.

    Attributes:
        name: The sequence name
        multimeter: The digital multimeter driver instance
        parameters: Test parameters from the manifest
        results: Collected test results
    """

    name = "PCB Voltage Test"
    version = "1.0.0"

    def __init__(
        self,
        hardware: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the test sequence.

        Args:
            hardware: Dictionary of hardware driver instances
            parameters: Dictionary of test parameters
        """
        self.hardware = hardware or {}
        self.parameters = parameters or {}
        self.results: List[Dict[str, Any]] = []
        self.measurements: Dict[int, float] = {}

        # Get the multimeter driver or create a mock one
        self.multimeter: Optional[MockMultimeter] = self.hardware.get("multimeter")
        if self.multimeter is None:
            self.multimeter = MockMultimeter(config={"port": "/dev/ttyUSB0"})

        # Get parameters with defaults
        self.voltage_threshold: float = self.parameters.get("voltage_threshold", 5.0)
        self.test_points: int = self.parameters.get("test_points", 5)
        self.min_voltage: float = self.parameters.get("min_voltage", 3.0)

        logger.debug(
            f"Initialized {self.name} with voltage_threshold={self.voltage_threshold}V, "
            f"test_points={self.test_points}, min_voltage={self.min_voltage}V"
        )

    @step(order=1, timeout=30.0)
    async def initialize(self) -> Dict[str, Any]:
        """Initialize hardware and prepare for testing.

        Connects to the multimeter and configures it for PCB testing.

        Returns:
            Dict containing initialization status
        """
        logger.info("Starting initialization step")
        result: Dict[str, Any] = {
            "step": "initialize",
            "status": "passed",
            "data": {},
        }

        try:
            if self.multimeter:
                logger.debug("Connecting to multimeter...")
                connected = await self.multimeter.connect()
                if not connected:
                    result["status"] = "failed"
                    result["error"] = "Failed to connect to multimeter"
                    logger.error("Multimeter connection failed")
                    return result

                # Get identification
                idn = await self.multimeter.identify()
                result["data"]["multimeter_idn"] = idn
                logger.info(f"Multimeter identified: {idn}")

                # Reset to default state
                await self.multimeter.reset()
                result["data"]["multimeter_reset"] = True

                # Set measurement range
                await self.multimeter.set_range("AUTO")
                result["data"]["range"] = "AUTO"

            result["data"]["voltage_threshold"] = self.voltage_threshold
            result["data"]["test_points"] = self.test_points
            result["data"]["min_voltage"] = self.min_voltage
            logger.info("Initialization completed successfully")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Initialization failed: {e}")

        return result

    @step(order=2, timeout=120.0, retry=1)
    async def measure_voltage(self) -> Dict[str, Any]:
        """Measure voltage at all test points.

        Performs voltage measurements at each configured test point
        on the PCB.

        Returns:
            Dict containing measurement results
        """
        logger.info("Starting voltage measurement step")
        result: Dict[str, Any] = {
            "step": "measure_voltage",
            "status": "passed",
            "data": {
                "measurements": {},
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
            },
        }

        try:
            if not self.multimeter:
                result["status"] = "failed"
                result["error"] = "Multimeter not available"
                logger.error("Multimeter not available for measurement")
                return result

            # Measure all test points
            logger.debug(f"Measuring {self.test_points} test points...")
            self.measurements = await self.multimeter.measure_all_points(self.test_points)

            # Calculate statistics
            values = list(self.measurements.values())
            avg_voltage = sum(values) / len(values)
            min_voltage = min(values)
            max_voltage = max(values)

            result["data"]["measurements"] = self.measurements
            result["data"]["average"] = round(avg_voltage, 4)
            result["data"]["min"] = round(min_voltage, 4)
            result["data"]["max"] = round(max_voltage, 4)

            logger.info(
                f"Measurements complete: avg={avg_voltage:.4f}V, "
                f"min={min_voltage:.4f}V, max={max_voltage:.4f}V"
            )

            self.results.append(result)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Voltage measurement failed: {e}")

        return result

    @step(order=3, timeout=30.0)
    async def validate_results(self) -> Dict[str, Any]:
        """Validate measurements against thresholds.

        Checks all measured voltages against min/max thresholds
        to determine pass/fail status.

        Returns:
            Dict containing validation results
        """
        logger.info("Starting validation step")
        result: Dict[str, Any] = {
            "step": "validate_results",
            "status": "passed",
            "data": {
                "passed_points": [],
                "failed_points": [],
                "overall_pass": True,
            },
        }

        try:
            passed_points = []
            failed_points = []

            for point, voltage in self.measurements.items():
                if self.min_voltage <= voltage <= self.voltage_threshold:
                    passed_points.append({"point": point, "voltage": voltage})
                    logger.debug(f"Point {point}: {voltage}V - PASS")
                else:
                    failed_points.append({
                        "point": point,
                        "voltage": voltage,
                        "reason": (
                            f"Out of range [{self.min_voltage}V - {self.voltage_threshold}V]"
                        )
                    })
                    logger.warning(f"Point {point}: {voltage}V - FAIL")

            result["data"]["passed_points"] = passed_points
            result["data"]["failed_points"] = failed_points
            result["data"]["pass_count"] = len(passed_points)
            result["data"]["fail_count"] = len(failed_points)

            if failed_points:
                result["status"] = "failed"
                result["data"]["overall_pass"] = False
                result["error"] = f"{len(failed_points)} test point(s) failed validation"
                logger.warning(f"Validation failed: {len(failed_points)} points out of range")
            else:
                logger.info(f"All {len(passed_points)} test points passed validation")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Validation failed: {e}")

        return result

    @step(order=99, cleanup=True, timeout=30.0)
    async def finalize(self) -> Dict[str, Any]:
        """Finalize and clean up resources.

        Disconnects from hardware and generates final report.
        This step always runs, even if previous steps failed.

        Returns:
            Dict containing finalization status
        """
        logger.info("Starting finalization step")
        result: Dict[str, Any] = {
            "step": "finalize",
            "status": "passed",
            "data": {
                "cleanup_completed": False,
            },
        }

        try:
            # Disconnect from multimeter
            if self.multimeter and await self.multimeter.is_connected():
                logger.debug("Disconnecting from multimeter...")
                await self.multimeter.disconnect()

            result["data"]["cleanup_completed"] = True
            result["data"]["total_measurements"] = len(self.measurements)
            result["data"]["total_results"] = len(self.results)
            logger.info(
                f"Finalization completed. Total measurements: {len(self.measurements)}"
            )

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Finalization failed: {e}")

        return result

    @parameter(
        name="voltage_threshold",
        display_name="Voltage Threshold",
        unit="V",
        description="Maximum allowed voltage threshold"
    )
    def get_voltage_threshold(self) -> float:
        """Get the current voltage threshold parameter."""
        return self.voltage_threshold

    @parameter(
        name="test_points",
        display_name="Test Points",
        unit="",
        description="Number of test points to measure"
    )
    def get_test_points(self) -> int:
        """Get the current test points parameter."""
        return self.test_points

    @parameter(
        name="min_voltage",
        display_name="Minimum Voltage",
        unit="V",
        description="Minimum expected voltage"
    )
    def get_min_voltage(self) -> float:
        """Get the current minimum voltage parameter."""
        return self.min_voltage
