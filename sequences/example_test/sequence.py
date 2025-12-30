"""
Example Test Sequence Module

Demonstrates the usage of @sequence and @step decorators
from the station_service.sequence framework for creating
structured test sequences with hardware integration.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from station_service.sequence.decorators import parameter, sequence, step

from .drivers.mock_dmm import MockDMM


logger = logging.getLogger(__name__)


@sequence(
    name="example_test",
    description="Example test sequence demonstrating voltage measurement",
    version="1.0.0"
)
class ExampleTestSequence:
    """
    Example Test Sequence demonstrating the sequence framework.

    This sequence shows how to:
    - Initialize hardware drivers
    - Perform measurements with proper error handling
    - Clean up resources in the finalize step

    Attributes:
        name: The sequence name
        dmm: The digital multimeter driver instance
        parameters: Test parameters from the manifest
        results: Collected test results
    """

    name = "Example Test Sequence"
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

        # Get the DMM driver or create a mock one
        self.dmm: Optional[MockDMM] = self.hardware.get("dmm")
        if self.dmm is None:
            self.dmm = MockDMM(config={"port": "/dev/ttyUSB0"})

        # Get parameters with defaults
        self.voltage_limit: float = self.parameters.get("voltage_limit", 5.0)
        self.test_count: int = self.parameters.get("test_count", 3)

        logger.debug(
            f"Initialized {self.name} with voltage_limit={self.voltage_limit}, "
            f"test_count={self.test_count}"
        )

    @step(order=1, timeout=30.0)
    async def initialize(self) -> Dict[str, Any]:
        """Initialize hardware and prepare for testing.

        Connects to hardware and prepares the test environment.

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
            # Connect to DMM
            if self.dmm:
                logger.debug("Connecting to DMM...")
                connected = await self.dmm.connect()
                if not connected:
                    result["status"] = "failed"
                    result["error"] = "Failed to connect to DMM"
                    logger.error("DMM connection failed")
                    return result

                # Get identification
                idn = await self.dmm.identify()
                result["data"]["dmm_idn"] = idn
                logger.info(f"DMM identified: {idn}")

                # Reset to default state
                await self.dmm.reset()
                result["data"]["dmm_reset"] = True

            result["data"]["voltage_limit"] = self.voltage_limit
            result["data"]["test_count"] = self.test_count
            logger.info("Initialization completed successfully")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Initialization failed: {e}")

        return result

    @step(order=2, timeout=60.0, retry=1)
    async def measure_voltage(self) -> Dict[str, Any]:
        """Measure voltage and validate against limits.

        Measures voltage multiple times based on test_count parameter
        and validates against voltage_limit.

        Returns:
            Dict containing measurement results
        """
        logger.info("Starting voltage measurement step")
        result: Dict[str, Any] = {
            "step": "measure_voltage",
            "status": "passed",
            "data": {
                "measurements": [],
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
            },
        }

        try:
            if not self.dmm:
                result["status"] = "failed"
                result["error"] = "DMM not available"
                logger.error("DMM not available for measurement")
                return result

            measurements: List[float] = []

            # Perform measurements
            logger.debug(f"Performing {self.test_count} measurements...")
            for i in range(self.test_count):
                voltage = await self.dmm.measure_voltage(mode="DC")
                measurements.append(voltage)
                logger.debug(f"Measurement {i + 1}: {voltage}V")

                # Small delay between measurements
                if i < self.test_count - 1:
                    await asyncio.sleep(0.05)

            # Calculate statistics
            avg_voltage = sum(measurements) / len(measurements)
            min_voltage = min(measurements)
            max_voltage = max(measurements)

            result["data"]["measurements"] = measurements
            result["data"]["average"] = round(avg_voltage, 4)
            result["data"]["min"] = round(min_voltage, 4)
            result["data"]["max"] = round(max_voltage, 4)

            logger.info(
                f"Measurements complete: avg={avg_voltage:.4f}V, "
                f"min={min_voltage:.4f}V, max={max_voltage:.4f}V"
            )

            # Validate against limit
            if max_voltage > self.voltage_limit:
                result["status"] = "failed"
                result["error"] = (
                    f"Voltage {max_voltage}V exceeds limit {self.voltage_limit}V"
                )
                logger.warning(result["error"])

            self.results.append(result)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Voltage measurement failed: {e}")

        return result

    @step(order=99, cleanup=True, timeout=30.0)
    async def finalize(self) -> Dict[str, Any]:
        """Finalize and clean up resources.

        Disconnects from hardware and cleans up resources.
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
            # Disconnect from DMM
            if self.dmm and await self.dmm.is_connected():
                logger.debug("Disconnecting from DMM...")
                await self.dmm.disconnect()

            result["data"]["cleanup_completed"] = True
            result["data"]["total_results"] = len(self.results)
            logger.info(
                f"Finalization completed. Total results: {len(self.results)}"
            )

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Finalization failed: {e}")

        return result

    @parameter(
        name="voltage_limit",
        display_name="Voltage Limit",
        unit="V",
        description="Maximum allowed voltage threshold"
    )
    def get_voltage_limit(self) -> float:
        """Get the current voltage limit parameter."""
        return self.voltage_limit

    @parameter(
        name="test_count",
        display_name="Test Count",
        unit="",
        description="Number of measurements to perform"
    )
    def get_test_count(self) -> int:
        """Get the current test count parameter."""
        return self.test_count
