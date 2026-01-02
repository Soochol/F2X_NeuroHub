"""
{{SEQUENCE_NAME}} Sequence Module

{{DESCRIPTION}}
"""

import logging
from typing import Any, Dict, List, Optional, Type

from station_service.sequence.decorators import parameter, sequence, step

logger = logging.getLogger(__name__)

# =============================================================================
# Lazy Import Pattern
# =============================================================================
# 드라이버를 lazy import하여 의존성 없이도 시퀀스 메타데이터 추출 가능.
# UI에서 step 목록 조회 시 드라이버 의존성 에러 방지.

{{DRIVER_CLASS}}: Optional[Type] = None


def _get_driver_class() -> Type:
    """
    Lazy load driver class.

    Returns:
        Driver class

    Raises:
        ImportError: Driver dependencies not available
    """
    global {{DRIVER_CLASS}}
    if {{DRIVER_CLASS}} is None:
        try:
            from .drivers.{{DRIVER_MODULE}} import {{DRIVER_CLASS}} as _DriverClass
            {{DRIVER_CLASS}} = _DriverClass
        except ImportError as e:
            raise ImportError(
                f"{{DRIVER_CLASS}} 로드 실패. 의존성 확인 필요: {e}"
            ) from e
    return {{DRIVER_CLASS}}


@sequence(
    name="{{SEQUENCE_NAME}}",
    description="{{DESCRIPTION}}",
    version="1.0.0"
)
class {{CLASS_NAME}}:
    """
    {{DESCRIPTION}}

    Tests {{DEVICE_DESCRIPTION}}.
    """

    def __init__(
        self,
        hardware: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize sequence.

        Args:
            hardware: Hardware driver instances dictionary
            parameters: Test parameters dictionary
        """
        self.hardware = hardware or {}
        self.parameters = parameters or {}
        self.results: List[Dict[str, Any]] = []

        # Get hardware driver (lazy loaded)
        self.device = self.hardware.get("{{DEVICE_ID}}")
        if self.device is None:
            # Create default driver if not provided (requires driver dependencies)
            DriverClass = _get_driver_class()
            self.device = DriverClass(config={
                "port": self.parameters.get("port", "/dev/ttyUSB0"),
                "baudrate": self.parameters.get("baudrate", 115200),
                "timeout": self.parameters.get("timeout", 5.0),
            })

        # Load parameters with defaults
        self.target_value: float = self.parameters.get("target_value", 10.0)
        self.tolerance_percent: float = self.parameters.get("tolerance_percent", 5.0)

        logger.debug(f"Initialized {{CLASS_NAME}}")
        logger.debug(f"Target: {self.target_value}, Tolerance: {self.tolerance_percent}%")

    # === Step Methods ===

    @step(order=1, timeout=30.0)
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize hardware and verify connection.

        Returns:
            Dict: Initialization result
        """
        logger.info("Step 1: Initializing hardware connection")
        result: Dict[str, Any] = {
            "step": "initialize",
            "status": "passed",
            "data": {},
        }

        try:
            if self.device:
                connected = await self.device.connect()
                if not connected:
                    result["status"] = "failed"
                    result["error"] = "Failed to connect to device"
                    return result

                # Get device info
                idn = await self.device.identify()
                result["data"]["device_idn"] = idn

                # Reset device
                await self.device.reset()
                result["data"]["device_reset"] = True

                logger.info(f"Connected: {idn}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Initialization failed: {e}")

        self.results.append(result)
        return result

    @step(order=2, timeout=60.0, retry=1)
    async def run_test(self) -> Dict[str, Any]:
        """
        Run main test.

        Returns:
            Dict: Test result
        """
        logger.info("Step 2: Running test")
        result: Dict[str, Any] = {
            "step": "run_test",
            "status": "passed",
            "data": {},
        }

        try:
            if not self.device or not await self.device.is_connected():
                result["status"] = "failed"
                result["error"] = "Device not connected"
                return result

            # Measure value
            measured = await self.device.measure()
            result["data"]["measured"] = measured
            result["data"]["target"] = self.target_value

            # Calculate deviation
            deviation = abs(measured - self.target_value) / self.target_value * 100
            result["data"]["deviation_percent"] = round(deviation, 2)

            # Pass/Fail judgment
            if deviation <= self.tolerance_percent:
                result["data"]["passed"] = True
                logger.info(f"Test PASSED: {measured} (deviation: {deviation:.2f}%)")
            else:
                result["status"] = "failed"
                result["data"]["passed"] = False
                result["error"] = f"Deviation {deviation:.2f}% exceeds tolerance {self.tolerance_percent}%"
                logger.warning(f"Test FAILED: {result['error']}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Test failed: {e}")

        self.results.append(result)
        return result

    @step(order=99, timeout=10.0, cleanup=True)
    async def finalize(self) -> Dict[str, Any]:
        """
        Clean up resources and disconnect.

        cleanup=True: Always runs even if previous steps failed.

        Returns:
            Dict: Cleanup result
        """
        logger.info("Step 99: Finalizing and cleaning up")
        result: Dict[str, Any] = {
            "step": "finalize",
            "status": "passed",
            "data": {"cleanup_completed": False},
        }

        try:
            if self.device and await self.device.is_connected():
                await self.device.disconnect()

            result["data"]["cleanup_completed"] = True
            result["data"]["total_steps"] = len(self.results)

            # Summarize results
            passed_count = sum(1 for r in self.results if r.get("status") == "passed")
            failed_count = sum(1 for r in self.results if r.get("status") == "failed")
            result["data"]["passed_steps"] = passed_count
            result["data"]["failed_steps"] = failed_count
            result["data"]["overall_passed"] = failed_count == 0

            logger.info(f"Cleanup completed. Passed: {passed_count}, Failed: {failed_count}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Finalization failed: {e}")

        self.results.append(result)
        return result

    # === Parameter Properties ===

    @parameter(
        name="target_value",
        display_name="목표값",
        unit="",
        description="테스트 목표값"
    )
    def get_target_value(self) -> float:
        """Target value parameter."""
        return self.target_value

    @parameter(
        name="tolerance_percent",
        display_name="허용 오차",
        unit="%",
        description="허용 오차 비율"
    )
    def get_tolerance_percent(self) -> float:
        """Tolerance parameter."""
        return self.tolerance_percent
