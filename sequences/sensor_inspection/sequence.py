"""
Sensor Inspection Sequence Module

Test sequence for sensor calibration and inspection with
pass/fail verification against tolerance thresholds.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from station_service.sequence.decorators import parameter, sequence, step

from .drivers.mock_sensor import MockSensorInterface


logger = logging.getLogger(__name__)


@sequence(
    name="sensor_inspection",
    description="Sensor calibration and inspection sequence for quality verification",
    version="1.0.0"
)
class SensorInspectionSequence:
    """
    Sensor Inspection Sequence for quality verification.

    This sequence performs sensor calibration, warmup, and verification
    against configurable tolerance thresholds.

    Attributes:
        name: The sequence name
        sensor_interface: The sensor interface driver instance
        parameters: Test parameters from the manifest
        results: Collected test results
    """

    name = "Sensor Inspection"
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
        self.calibration_data: Dict[str, Any] = {}
        self.verification_data: Dict[str, Any] = {}

        # Get the sensor interface driver or create a mock one
        self.sensor_interface: Optional[MockSensorInterface] = self.hardware.get(
            "sensor_interface"
        )
        if self.sensor_interface is None:
            self.sensor_interface = MockSensorInterface(
                config={"port": "/dev/ttyUSB1", "sample_rate": 100}
            )

        # Get parameters with defaults
        self.calibration_cycles: int = self.parameters.get("calibration_cycles", 3)
        self.tolerance_percent: float = self.parameters.get("tolerance_percent", 5.0)
        self.reference_value: float = self.parameters.get("reference_value", 100.0)
        self.warmup_time: float = self.parameters.get("warmup_time", 2.0)

        logger.debug(
            f"Initialized {self.name} with calibration_cycles={self.calibration_cycles}, "
            f"tolerance={self.tolerance_percent}%, reference={self.reference_value}"
        )

    @step(order=1, timeout=30.0)
    async def initialize(self) -> Dict[str, Any]:
        """Initialize hardware and prepare for inspection.

        Connects to the sensor interface and prepares the test environment.

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
            if self.sensor_interface:
                logger.debug("Connecting to sensor interface...")
                connected = await self.sensor_interface.connect()
                if not connected:
                    result["status"] = "failed"
                    result["error"] = "Failed to connect to sensor interface"
                    logger.error("Sensor interface connection failed")
                    return result

                # Get identification
                idn = await self.sensor_interface.identify()
                result["data"]["sensor_idn"] = idn
                logger.info(f"Sensor interface identified: {idn}")

                # Reset to default state
                await self.sensor_interface.reset()
                result["data"]["sensor_reset"] = True

            result["data"]["calibration_cycles"] = self.calibration_cycles
            result["data"]["tolerance_percent"] = self.tolerance_percent
            result["data"]["reference_value"] = self.reference_value
            result["data"]["warmup_time"] = self.warmup_time
            logger.info("Initialization completed successfully")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Initialization failed: {e}")

        return result

    @step(order=2, timeout=60.0)
    async def warmup_sensor(self) -> Dict[str, Any]:
        """Perform sensor warmup.

        Allows the sensor to stabilize before calibration.

        Returns:
            Dict containing warmup status
        """
        logger.info("Starting sensor warmup step")
        result: Dict[str, Any] = {
            "step": "warmup_sensor",
            "status": "passed",
            "data": {
                "warmup_duration": self.warmup_time,
            },
        }

        try:
            if not self.sensor_interface:
                result["status"] = "failed"
                result["error"] = "Sensor interface not available"
                return result

            logger.debug(f"Warming up sensor for {self.warmup_time} seconds...")
            warmup_success = await self.sensor_interface.warmup(self.warmup_time)

            if warmup_success:
                result["data"]["warmup_completed"] = True
                logger.info("Sensor warmup completed successfully")
            else:
                result["status"] = "failed"
                result["error"] = "Sensor warmup failed"
                logger.error("Sensor warmup failed")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Warmup failed: {e}")

        return result

    @step(order=3, timeout=120.0, retry=1)
    async def calibrate(self) -> Dict[str, Any]:
        """Run calibration cycles.

        Performs multiple calibration cycles and averages results.

        Returns:
            Dict containing calibration results
        """
        logger.info("Starting calibration step")
        result: Dict[str, Any] = {
            "step": "calibrate",
            "status": "passed",
            "data": {
                "cycles_completed": 0,
                "calibration_results": [],
            },
        }

        try:
            if not self.sensor_interface:
                result["status"] = "failed"
                result["error"] = "Sensor interface not available"
                return result

            calibration_results = []

            for cycle in range(self.calibration_cycles):
                logger.debug(f"Running calibration cycle {cycle + 1}/{self.calibration_cycles}")

                cal_result = await self.sensor_interface.calibrate(
                    reference_value=self.reference_value,
                    num_samples=10
                )
                calibration_results.append(cal_result)

                # Brief pause between cycles
                if cycle < self.calibration_cycles - 1:
                    await asyncio.sleep(0.5)

            # Calculate average offset across cycles
            avg_offset = sum(r["offset_applied"] for r in calibration_results) / len(
                calibration_results
            )

            result["data"]["cycles_completed"] = self.calibration_cycles
            result["data"]["calibration_results"] = calibration_results
            result["data"]["average_offset"] = round(avg_offset, 4)

            self.calibration_data = result["data"]
            logger.info(
                f"Calibration completed: {self.calibration_cycles} cycles, "
                f"avg offset={avg_offset:.4f}"
            )

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Calibration failed: {e}")

        return result

    @step(order=4, timeout=60.0)
    async def verify_readings(self) -> Dict[str, Any]:
        """Verify calibration accuracy.

        Compares sensor readings against tolerance threshold.

        Returns:
            Dict containing verification results
        """
        logger.info("Starting verification step")
        result: Dict[str, Any] = {
            "step": "verify_readings",
            "status": "passed",
            "data": {
                "verification_passed": False,
            },
        }

        try:
            if not self.sensor_interface:
                result["status"] = "failed"
                result["error"] = "Sensor interface not available"
                return result

            verification = await self.sensor_interface.verify_calibration(
                reference_value=self.reference_value,
                tolerance_percent=self.tolerance_percent,
                num_samples=20
            )

            result["data"]["verification"] = verification
            result["data"]["verification_passed"] = verification["passed"]
            result["data"]["measured_avg"] = verification["measured_avg"]
            result["data"]["deviation_percent"] = verification["deviation_percent"]

            self.verification_data = verification

            if verification["passed"]:
                logger.info(
                    f"Verification PASSED: deviation {verification['deviation_percent']:.2f}% "
                    f"<= tolerance {self.tolerance_percent}%"
                )
            else:
                result["status"] = "failed"
                result["error"] = (
                    f"Verification failed: deviation {verification['deviation_percent']:.2f}% "
                    f"> tolerance {self.tolerance_percent}%"
                )
                logger.warning(result["error"])

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Verification failed: {e}")

        return result

    @step(order=5, timeout=30.0)
    async def generate_report(self) -> Dict[str, Any]:
        """Generate inspection report.

        Creates a summary report of the inspection results.

        Returns:
            Dict containing report data
        """
        logger.info("Starting report generation step")
        result: Dict[str, Any] = {
            "step": "generate_report",
            "status": "passed",
            "data": {
                "report_generated": False,
            },
        }

        try:
            report = {
                "sequence_name": self.name,
                "sequence_version": self.version,
                "parameters": {
                    "calibration_cycles": self.calibration_cycles,
                    "tolerance_percent": self.tolerance_percent,
                    "reference_value": self.reference_value,
                    "warmup_time": self.warmup_time,
                },
                "calibration_summary": {
                    "cycles_completed": self.calibration_data.get("cycles_completed", 0),
                    "average_offset": self.calibration_data.get("average_offset", 0),
                },
                "verification_summary": {
                    "passed": self.verification_data.get("passed", False),
                    "measured_avg": self.verification_data.get("measured_avg", 0),
                    "deviation_percent": self.verification_data.get("deviation_percent", 0),
                    "tolerance_percent": self.tolerance_percent,
                },
                "overall_result": "PASS" if self.verification_data.get("passed") else "FAIL",
            }

            result["data"]["report"] = report
            result["data"]["report_generated"] = True
            self.results.append(result)

            logger.info(f"Report generated: {report['overall_result']}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Report generation failed: {e}")

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
            # Disconnect from sensor interface
            if self.sensor_interface and await self.sensor_interface.is_connected():
                logger.debug("Disconnecting from sensor interface...")
                await self.sensor_interface.disconnect()

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
        name="calibration_cycles",
        display_name="Calibration Cycles",
        unit="",
        description="Number of calibration cycles"
    )
    def get_calibration_cycles(self) -> int:
        """Get the current calibration cycles parameter."""
        return self.calibration_cycles

    @parameter(
        name="tolerance_percent",
        display_name="Tolerance Percentage",
        unit="%",
        description="Acceptable deviation percentage"
    )
    def get_tolerance_percent(self) -> float:
        """Get the current tolerance percentage parameter."""
        return self.tolerance_percent

    @parameter(
        name="reference_value",
        display_name="Reference Value",
        unit="",
        description="Reference calibration value"
    )
    def get_reference_value(self) -> float:
        """Get the current reference value parameter."""
        return self.reference_value

    @parameter(
        name="warmup_time",
        display_name="Warmup Time",
        unit="s",
        description="Sensor warmup duration"
    )
    def get_warmup_time(self) -> float:
        """Get the current warmup time parameter."""
        return self.warmup_time
