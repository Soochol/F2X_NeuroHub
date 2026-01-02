"""
PSA Sensor Test Sequence Module

Automated test sequence for VL53L0X ToF distance sensor and
MLX90640 IR thermal sensor via STM32H723 MCU.
"""

import logging
from typing import Any, Dict, List, Optional

from station_service.sequence.decorators import parameter, sequence, step

logger = logging.getLogger(__name__)

# Lazy import for driver - allows metadata extraction without dependencies
PSAMCUDriver = None


def _get_driver_class():
    """Load driver class at runtime."""
    global PSAMCUDriver
    if PSAMCUDriver is None:
        try:
            from .drivers.psa_mcu import PSAMCUDriver as _Driver
            PSAMCUDriver = _Driver
        except ImportError as e:
            raise ImportError(
                f"PSAMCUDriver 로드 실패. psa_protocol 의존성 확인 필요: {e}"
            )
    return PSAMCUDriver


@sequence(
    name="psa_sensor_test",
    description="PSA 센서 테스트 시퀀스 (VL53L0X ToF, MLX90640 IR)",
    version="1.0.0"
)
class PSASensorTestSequence:
    """
    PSA Sensor Test Sequence.

    Tests VL53L0X (ToF distance) and MLX90640 (IR thermal) sensors
    connected to STM32H723 MCU via UART protocol.
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

        # Load parameters with defaults
        self.port: str = self.parameters.get("port", "/dev/ttyUSB0")

        # Get hardware driver (lazy load if not provided)
        self.mcu = self.hardware.get("psa_mcu")
        if self.mcu is None:
            driver_class = _get_driver_class()
            self.mcu = driver_class(config={
                "port": self.port,
                "baudrate": self.parameters.get("baudrate", 115200),
                "timeout": self.parameters.get("timeout", 5.0),
            })
        self.vl53l0x_target_mm: int = self.parameters.get("vl53l0x_target_mm", 500)
        self.vl53l0x_tolerance_mm: int = self.parameters.get("vl53l0x_tolerance_mm", 100)
        self.mlx90640_target_celsius: float = self.parameters.get("mlx90640_target_celsius", 25.0)
        self.mlx90640_tolerance_celsius: float = self.parameters.get("mlx90640_tolerance_celsius", 10.0)

        # 센서별 활성화 설정
        self.test_vl53l0x_enabled: bool = self.parameters.get("test_vl53l0x_enabled", True)
        self.test_mlx90640_enabled: bool = self.parameters.get("test_mlx90640_enabled", True)

        logger.debug(f"Initialized psa_sensor_test v1.0.0")
        logger.debug(f"VL53L0X: target={self.vl53l0x_target_mm}mm, tolerance={self.vl53l0x_tolerance_mm}mm")
        logger.debug(f"MLX90640: target={self.mlx90640_target_celsius}C, tolerance={self.mlx90640_tolerance_celsius}C")

    # === Step Methods ===

    @step(order=1, timeout=30.0)
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize hardware and verify connection.

        Step 1: Connect to MCU and verify firmware version.
        """
        logger.info("Step 1: Initializing PSA MCU connection")
        result: Dict[str, Any] = {
            "step": "initialize",
            "status": "passed",
            "data": {},
        }

        try:
            if self.mcu:
                connected = await self.mcu.connect()
                if not connected:
                    result["status"] = "failed"
                    result["error"] = "Failed to connect to PSA MCU"
                    return result

                # Get device info
                idn = await self.mcu.identify()
                result["data"]["device_idn"] = idn

                # Get firmware version
                version = await self.mcu.ping()
                result["data"]["firmware_version"] = version

                # Get sensor list
                sensors = await self.mcu.get_sensor_list()
                result["data"]["sensors"] = sensors
                result["data"]["sensor_count"] = len(sensors)

                logger.info(f"Connected: {idn}")
                logger.info(f"Sensors: {[s['name'] for s in sensors]}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Initialization failed: {e}")

        self.results.append(result)
        return result

    @step(order=2, timeout=15.0, retry=1)
    async def test_vl53l0x(self) -> Dict[str, Any]:
        """
        Test VL53L0X ToF distance sensor.

        Step 2: Set spec and run distance measurement test.
        """
        logger.info("Step 2: Testing VL53L0X ToF sensor")

        # Skip if disabled
        if not self.test_vl53l0x_enabled:
            logger.info("VL53L0X test skipped (disabled)")
            return {"step": "test_vl53l0x", "status": "skipped", "data": {"reason": "disabled"}}

        result: Dict[str, Any] = {
            "step": "test_vl53l0x",
            "status": "passed",
            "data": {},
        }

        try:
            if not self.mcu or not await self.mcu.is_connected():
                result["status"] = "failed"
                result["error"] = "MCU not connected"
                return result

            # Run VL53L0X test
            test_result = await self.mcu.test_vl53l0x(
                target_mm=self.vl53l0x_target_mm,
                tolerance_mm=self.vl53l0x_tolerance_mm
            )

            result["data"] = test_result

            # Check pass/fail
            if not test_result.get("passed", False):
                result["status"] = "failed"
                result["error"] = f"VL53L0X test failed: {test_result.get('status_name', 'Unknown')}"
                if "measured_mm" in test_result:
                    result["error"] += f" (measured={test_result['measured_mm']}mm)"

            logger.info(f"VL53L0X result: {test_result}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"VL53L0X test failed: {e}")

        self.results.append(result)
        return result

    @step(order=3, timeout=20.0, retry=1)
    async def test_mlx90640(self) -> Dict[str, Any]:
        """
        Test MLX90640 IR thermal sensor.

        Step 3: Set spec and run temperature measurement test.
        """
        logger.info("Step 3: Testing MLX90640 IR thermal sensor")

        # Skip if disabled
        if not self.test_mlx90640_enabled:
            logger.info("MLX90640 test skipped (disabled)")
            return {"step": "test_mlx90640", "status": "skipped", "data": {"reason": "disabled"}}

        result: Dict[str, Any] = {
            "step": "test_mlx90640",
            "status": "passed",
            "data": {},
        }

        try:
            if not self.mcu or not await self.mcu.is_connected():
                result["status"] = "failed"
                result["error"] = "MCU not connected"
                return result

            # Run MLX90640 test
            test_result = await self.mcu.test_mlx90640(
                target_celsius=self.mlx90640_target_celsius,
                tolerance_celsius=self.mlx90640_tolerance_celsius
            )

            result["data"] = test_result

            # Check pass/fail
            if not test_result.get("passed", False):
                result["status"] = "failed"
                result["error"] = f"MLX90640 test failed: {test_result.get('status_name', 'Unknown')}"
                if "measured_celsius" in test_result:
                    result["error"] += f" (measured={test_result['measured_celsius']:.1f}C)"

            logger.info(f"MLX90640 result: {test_result}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"MLX90640 test failed: {e}")

        self.results.append(result)
        return result

    @step(order=99, timeout=10.0, cleanup=True)
    async def finalize(self) -> Dict[str, Any]:
        """
        Clean up resources and disconnect.

        Step 99 (cleanup): Always runs, even if previous steps failed.
        """
        logger.info("Step 99: Finalizing and cleaning up")
        result: Dict[str, Any] = {
            "step": "finalize",
            "status": "passed",
            "data": {"cleanup_completed": False},
        }

        try:
            if self.mcu and await self.mcu.is_connected():
                await self.mcu.disconnect()

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
        name="port",
        display_name="시리얼 포트",
        unit="",
        description="MCU 시리얼 포트 (예: /dev/ttyUSB0, COM3)"
    )
    def get_port(self) -> str:
        """Serial port parameter."""
        return self.port

    @parameter(
        name="vl53l0x_target_mm",
        display_name="VL53L0X 목표 거리",
        unit="mm",
        description="ToF 센서 목표 거리"
    )
    def get_vl53l0x_target_mm(self) -> int:
        """VL53L0X target distance parameter."""
        return self.vl53l0x_target_mm

    @parameter(
        name="vl53l0x_tolerance_mm",
        display_name="VL53L0X 허용 오차",
        unit="mm",
        description="ToF 센서 허용 오차"
    )
    def get_vl53l0x_tolerance_mm(self) -> int:
        """VL53L0X tolerance parameter."""
        return self.vl53l0x_tolerance_mm

    @parameter(
        name="mlx90640_target_celsius",
        display_name="MLX90640 목표 온도",
        unit="C",
        description="IR 센서 목표 온도 (섭씨)"
    )
    def get_mlx90640_target_celsius(self) -> float:
        """MLX90640 target temperature parameter."""
        return self.mlx90640_target_celsius

    @parameter(
        name="mlx90640_tolerance_celsius",
        display_name="MLX90640 허용 오차",
        unit="C",
        description="IR 센서 허용 오차 (섭씨)"
    )
    def get_mlx90640_tolerance_celsius(self) -> float:
        """MLX90640 tolerance parameter."""
        return self.mlx90640_tolerance_celsius

    # === Context Manager Support ===

    async def __aenter__(self) -> "PSASensorTestSequence":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit - ensures cleanup on any exit.

        Called on normal exit, exceptions, or cancellation.
        """
        await self._ensure_disconnect()
        return None  # Don't suppress exceptions

    async def _ensure_disconnect(self) -> None:
        """Ensure MCU is disconnected (safe to call multiple times)."""
        try:
            if self.mcu and await self.mcu.is_connected():
                await self.mcu.disconnect()
                logger.info("MCU disconnected via cleanup")
        except Exception as e:
            logger.warning(f"Cleanup disconnect failed: {e}")
