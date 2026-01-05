"""
Mock Success Sequence

테스트용으로 항상 성공하는 시퀀스입니다.
3개의 스텝을 실행하고 PASS를 반환합니다.
"""

import asyncio
import random
import time
from typing import Any, Dict

from station_service_sdk import (
    SequenceBase,
    RunResult,
)


class MockSuccessSequence(SequenceBase):
    """항상 성공하는 Mock 시퀀스"""

    name = "mock_success"
    version = "1.0.0"
    description = "테스트용 Mock 시퀀스 - 항상 성공"

    STEP_COUNT = 3  # 고정 스텝 수

    async def setup(self) -> None:
        """시퀀스 초기화"""
        self.emit_log("info", "Initializing Mock Success sequence...")

        # 파라미터 로드
        self.delay_per_step = self.get_parameter("delay_per_step", 0.5)

        self.emit_log("info", f"Configuration: {self.STEP_COUNT} steps, {self.delay_per_step}s delay each")
        self.emit_log("info", "Setup completed successfully")

    async def run(self) -> RunResult:
        """Mock 테스트 실행"""
        measurements: Dict[str, Any] = {}
        total_start = time.time()

        for step_num in range(1, self.STEP_COUNT + 1):
            self.check_abort()

            step_name = f"mock_step_{step_num}"
            self.emit_step_start(step_name, step_num, self.STEP_COUNT, f"Mock Step {step_num}")
            step_start = time.time()

            # 시뮬레이션 지연
            await asyncio.sleep(self.delay_per_step)

            # Mock 측정값 생성
            mock_value = round(random.uniform(90.0, 100.0), 2)
            measurements[f"step_{step_num}_value"] = mock_value
            self.emit_measurement(f"step_{step_num}_value", mock_value, "%", passed=True)

            step_duration = time.time() - step_start
            self.emit_step_complete(step_name, step_num, True, step_duration)
            self.emit_log("info", f"Step {step_num} completed: value={mock_value}%")

        total_duration = time.time() - total_start
        measurements["total_duration"] = round(total_duration, 3)
        self.emit_measurement("total_duration", total_duration, "s", passed=True)

        self.emit_log("info", f"All {self.STEP_COUNT} steps completed successfully in {total_duration:.2f}s")

        return {
            "passed": True,
            "measurements": measurements,
        }

    async def teardown(self) -> None:
        """정리 작업"""
        self.emit_log("info", "Cleaning up...")
        self.emit_log("info", "Teardown completed")
