# Sequence Development Guide

테스트 시퀀스 개발을 위한 종합 가이드입니다. 본 문서는 NeuroHub Station Service에서 사용하는 시퀀스 패키지의 구조, 작성 방법, SDK 사용법, 드라이버 구현 등을 상세히 설명합니다.

---

## 목차

1. [개요](#1-개요)
2. [시퀀스 패키지 구조](#2-시퀀스-패키지-구조)
3. [manifest.yaml 작성](#3-manifestyaml-작성)
4. [**SDK 기반 시퀀스 (권장)**](#4-sdk-기반-시퀀스-권장)
5. [드라이버 구현](#5-드라이버-구현)
6. [CLI 실행 및 JSON Lines 프로토콜](#6-cli-실행-및-json-lines-프로토콜)
7. [예제: 새 시퀀스 만들기](#7-예제-새-시퀀스-만들기)
8. [베스트 프랙티스](#8-베스트-프랙티스)
9. [레거시: 데코레이터 방식](#9-레거시-데코레이터-방식)

---

## 1. 개요

### 1.1 시퀀스란?

시퀀스(Sequence)는 테스트 장비의 자동화된 검사/테스트 절차를 정의하는 Python 패키지입니다. 각 시퀀스는:

- 하드웨어 제어 드라이버
- 테스트 스텝 정의
- 파라미터 설정
- 결과 수집 로직

을 포함합니다.

### 1.2 핵심 개념

| 개념 | 설명 |
|------|------|
| **Sequence** | 테스트 절차를 정의하는 클래스 |
| **Step** | 개별 테스트 단계 (메서드) |
| **Driver** | 하드웨어 제어 인터페이스 |
| **Manifest** | 시퀀스 메타데이터 (YAML) |
| **Parameter** | 런타임에 조정 가능한 설정값 |

---

## 2. 시퀀스 패키지 구조

### 2.1 기본 폴더 구조

```
sequences/
├── __init__.py                 # 패키지 초기화
└── my_sequence/                # 시퀀스 이름 (Python 식별자)
    ├── __init__.py             # 모듈 초기화
    ├── manifest.yaml           # 시퀀스 메타데이터 정의
    ├── main.py                 # CLI 진입점 (SDK 방식)
    ├── sequence.py             # 시퀀스 클래스 구현
    └── drivers/                # 하드웨어 드라이버
        ├── __init__.py
        ├── base.py             # BaseDriver 추상 클래스
        └── my_device.py        # 실제 장치 드라이버
```

### 2.2 파일별 역할

| 파일 | 역할 |
|------|------|
| `manifest.yaml` | 시퀀스 설정, 하드웨어, 파라미터 정의 |
| `main.py` | CLI 진입점 (SDK 기반 실행) |
| `sequence.py` | 테스트 로직 구현 |
| `drivers/*.py` | 하드웨어 통신 인터페이스 |
| `__init__.py` | Python 모듈 인식용 |

---

## 3. manifest.yaml 작성

manifest.yaml은 시퀀스의 메타데이터와 설정을 정의합니다.

### 3.1 기본 구조

```yaml
# 시퀀스 기본 정보
name: my_sequence           # Python 식별자 (필수)
version: "1.0.0"            # X.Y.Z 형식 (필수)
author: "개발팀"            # 작성자
description: |              # 시퀀스 설명 (여러 줄 가능)
  시퀀스에 대한 상세 설명을 작성합니다.

# 실행 모드 설정
modes:
  automatic: true           # 자동 순차 실행
  manual: true              # 수동 스텝별 실행
  interactive: false        # 인터랙티브 모드 (예약)

# 진입점 설정
entry_point:
  module: sequence          # Python 모듈 이름
  class: MySequenceClass    # 시퀀스 클래스 이름

# 하드웨어 정의
hardware:
  device_name:              # 장치 식별자 (코드에서 참조)
    display_name: "장치 표시명"
    driver: driver_module   # drivers/ 하위 모듈명
    class: DriverClassName  # 드라이버 클래스명
    description: "장치 설명"
    config_schema:          # 설정 스키마
      port:
        type: string
        required: false
        default: "/dev/ttyUSB0"
        description: "시리얼 포트"

# 시퀀스 파라미터
parameters:
  param_name:
    display_name: "파라미터 표시명"
    type: float             # string, integer, float, boolean
    default: 10.0
    min: 0.0
    max: 100.0
    unit: "V"
    description: "파라미터 설명"

# Python 의존성
dependencies:
  python:
    - pyserial>=3.5
    - numpy>=1.20
```

### 3.2 하드웨어 정의 상세

```yaml
hardware:
  power_supply:
    display_name: "전원 공급기"
    driver: mock_power_supply
    class: MockPowerSupply
    description: "DC 전원 공급기 (0-30V, 0-5A)"

    # 설정 스키마 (optional)
    config_schema:
      port:
        type: string
        required: false
        default: "/dev/ttyUSB0"
        description: "시리얼 포트"
      max_voltage:
        type: float
        required: false
        default: 30.0
        min: 0.0
        max: 60.0
        description: "최대 전압 제한"

    # 수동 제어 명령 정의 (optional)
    manual_commands:
      - name: measure_voltage        # 메서드 이름
        display_name: "전압 측정"    # UI 표시명
        category: measurement        # 카테고리
        description: "출력 전압 측정"
        parameters: []               # 파라미터 없음
        returns:
          type: float
          unit: "V"

      - name: set_voltage
        display_name: "전압 설정"
        category: control
        description: "출력 전압 설정"
        parameters:
          - name: voltage
            display_name: "전압"
            type: number
            required: true
            default: 5.0
            min: 0
            max: 30
            unit: "V"
            description: "설정할 전압값"
```

### 3.3 명령 카테고리

| 카테고리 | 설명 | 예시 |
|----------|------|------|
| `measurement` | 값 읽기/측정 | 전압 측정, 상태 읽기 |
| `control` | 장치 제어 | 출력 ON/OFF, 값 설정 |
| `configuration` | 설정 변경 | 보호 임계값, 레이블 |
| `diagnostic` | 진단/유틸리티 | 리셋, 식별, 연결 확인 |

### 3.4 스텝 정의 (선택사항)

```yaml
steps:
  - name: initialize_hardware       # 메서드 이름
    display_name: "하드웨어 초기화" # UI 표시명
    order: 1                        # 실행 순서
    timeout: 30.0                   # 타임아웃 (초)
    manual:
      skippable: false              # 건너뛰기 허용
      auto_only: false              # 자동 실행 전용
      prompt: null                  # 실행 전 메시지
      pause_before: false           # 실행 전 일시정지
      pause_after: false            # 실행 후 일시정지
      parameter_overrides: []       # 재정의 가능 파라미터

  - name: run_test
    display_name: "테스트 실행"
    order: 2
    timeout: 60.0
    retry: 2                        # 재시도 횟수
    manual:
      skippable: true
      prompt: "테스트를 시작하시겠습니까?"
      pause_before: true
      parameter_overrides:
        - test_voltage
        - test_current

  - name: cleanup
    display_name: "정리"
    order: 99                       # 높은 순서 = 마지막 실행
    timeout: 30.0
    cleanup: true                   # 항상 실행 (실패 시에도)
```

### 3.5 파라미터 타입

| 타입 | 설명 | YAML 표기 |
|------|------|-----------|
| 문자열 | 텍스트 값 | `type: string` |
| 정수 | 정수 값 | `type: integer` |
| 실수 | 부동소수점 | `type: float` |
| 불리언 | true/false | `type: boolean` |

---

## 4. SDK 기반 시퀀스 (권장)

새로운 시퀀스는 `SequenceBase`를 상속하여 구현합니다. 이 방식은 CLI 기반 subprocess 실행을 지원하며, JSON Lines 프로토콜을 통해 Station Service와 통신합니다.

### 4.1 실행 방식

```bash
# 시퀀스 실행
python -m sequences.my_sequence.main --start --config '{"wip_id": "WIP-001", "parameters": {...}}'

# 시퀀스 중지
python -m sequences.my_sequence.main --stop

# 상태 확인
python -m sequences.my_sequence.main --status
```

### 4.2 main.py (CLI 진입점)

```python
"""CLI entry point for the sequence."""

from .sequence import MyTestSequence

if __name__ == "__main__":
    exit(MyTestSequence.run_from_cli())
```

### 4.3 SequenceBase 상속

```python
"""
My Test Sequence Module

시퀀스에 대한 설명을 작성합니다.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from station_service.sdk import SequenceBase, ExecutionContext

from .drivers.my_device import MyDeviceDriver

logger = logging.getLogger(__name__)


class MyTestSequence(SequenceBase):
    """
    테스트 시퀀스 클래스.

    SequenceBase를 상속하여 SDK 기반으로 구현합니다.
    """

    # 시퀀스 메타데이터 (필수)
    name = "my_test_sequence"
    version = "1.0.0"

    async def setup(self) -> None:
        """
        시퀀스 초기화 (하드웨어 연결 등).

        SequenceBase.run()에서 자동 호출됩니다.
        """
        self.emit_log("info", "Setting up sequence...")

        # 파라미터 가져오기
        self.test_value = self.get_parameter("test_value", 10.0)
        self.timeout_sec = self.get_parameter("timeout_sec", 30.0)

        # 하드웨어 드라이버 초기화
        device_config = self.hardware.get("my_device", {})
        self.my_device = MyDeviceDriver(config=device_config)
        await self.my_device.connect()

        self.emit_log("info", f"Setup complete. Device connected.")

    async def run(self) -> Dict[str, Any]:
        """
        메인 시퀀스 실행 로직.

        Returns:
            Dict: 최종 결과 (measurements, steps 등)
        """
        results = {"measurements": {}, "steps": []}

        # Step 1: 초기화
        await self._step_initialize(results)

        # Step 2: 측정
        await self._step_measurement(results)

        return results

    async def teardown(self) -> None:
        """
        시퀀스 정리 (하드웨어 해제 등).

        항상 실행됩니다 (실패 시에도).
        """
        self.emit_log("info", "Cleaning up...")

        if hasattr(self, 'my_device') and self.my_device:
            if await self.my_device.is_connected():
                await self.my_device.disconnect()

        self.emit_log("info", "Cleanup complete.")

    # === 스텝 메서드 ===

    async def _step_initialize(self, results: Dict) -> None:
        """Step 1: 장치 식별 및 리셋."""
        self.emit_step_start("initialize", 1, 2, "장치 초기화")
        start_time = asyncio.get_event_loop().time()

        try:
            idn = await self.my_device.identify()
            await self.my_device.reset()

            duration = asyncio.get_event_loop().time() - start_time
            self.emit_step_complete("initialize", 1, True, duration, {"idn": idn})
            results["steps"].append({"name": "initialize", "passed": True})

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            self.emit_step_complete("initialize", 1, False, duration, error=str(e))
            results["steps"].append({"name": "initialize", "passed": False, "error": str(e)})
            raise

    async def _step_measurement(self, results: Dict) -> None:
        """Step 2: 값 측정 및 판정."""
        self.emit_step_start("measurement", 2, 2, "측정 실행")
        start_time = asyncio.get_event_loop().time()

        try:
            # 측정 실행
            measured_value = await self.my_device.measure()

            # 측정값 기록
            self.emit_measurement(
                "voltage",
                measured_value,
                "V",
                min_value=self.test_value * 0.95,
                max_value=self.test_value * 1.05,
            )
            results["measurements"]["voltage"] = measured_value

            # 판정
            tolerance = self.test_value * 0.05
            passed = abs(measured_value - self.test_value) <= tolerance

            duration = asyncio.get_event_loop().time() - start_time
            self.emit_step_complete(
                "measurement", 2, passed, duration,
                measurements={"voltage": measured_value}
            )
            results["steps"].append({"name": "measurement", "passed": passed})

            if not passed:
                raise ValueError(f"Value {measured_value} out of tolerance")

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            self.emit_step_complete("measurement", 2, False, duration, error=str(e))
            results["steps"].append({"name": "measurement", "passed": False, "error": str(e)})
            raise
```

### 4.4 SequenceBase 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `setup()` | 시퀀스 시작 전 초기화 (하드웨어 연결 등) |
| `run()` | 메인 시퀀스 로직 실행 |
| `teardown()` | 시퀀스 종료 후 정리 (항상 실행) |
| `get_parameter(name, default)` | 파라미터 값 가져오기 |
| `emit_log(level, message)` | 로그 메시지 출력 |
| `emit_step_start(name, index, total)` | 스텝 시작 이벤트 |
| `emit_step_complete(name, index, passed, duration)` | 스텝 완료 이벤트 |
| `emit_measurement(name, value, unit)` | 측정값 기록 |
| `emit_error(code, message)` | 에러 이벤트 |

### 4.5 manifest.yaml 설정

SDK 기반 시퀀스는 `modes.cli: true`와 `entry_point.cli_main`을 설정합니다:

```yaml
name: my_test_sequence
version: "1.0.0"

modes:
  automatic: true
  manual: true
  cli: true  # CLI 모드 활성화

entry_point:
  module: sequence
  class: MyTestSequence
  cli_main: main  # main.py 지정
```

---

## 5. 드라이버 구현

### 5.1 BaseDriver 추상 클래스

모든 드라이버는 `BaseDriver`를 상속해야 합니다:

```python
"""
Base Driver Module

모든 하드웨어 드라이버의 기본 클래스입니다.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDriver(ABC):
    """
    추상 기본 드라이버 클래스.

    모든 하드웨어 드라이버는 이 클래스를 상속하고
    추상 메서드를 구현해야 합니다.

    Attributes:
        name: 드라이버 이름
        config: 설정 딕셔너리
    """

    def __init__(
        self,
        name: str = "BaseDriver",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        드라이버 초기화.

        Args:
            name: 드라이버 식별 이름
            config: 설정 딕셔너리 (포트, 속도 등)
        """
        self.name = name
        self.config = config or {}
        self._connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """
        하드웨어 연결.

        Returns:
            bool: 연결 성공 여부
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """
        하드웨어 연결 해제.

        리소스를 정리하고 연결을 종료합니다.
        """
        ...

    @abstractmethod
    async def reset(self) -> None:
        """
        하드웨어 초기 상태로 리셋.

        장치를 알려진 안전한 상태로 복원합니다.
        """
        ...

    async def identify(self) -> str:
        """
        장치 식별 문자열 반환.

        Returns:
            str: 장치 ID 문자열 (예: "Manufacturer,Model,Serial,Version")
        """
        return "Unknown"

    async def is_connected(self) -> bool:
        """
        연결 상태 확인.

        Returns:
            bool: 연결 여부
        """
        return self._connected

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, connected={self._connected})"
```

### 5.2 드라이버 구현 예시

```python
"""
My Device Driver Module

특정 장치와의 통신을 담당하는 드라이버입니다.
"""

import asyncio
import random
from typing import Any, Dict, Optional

from .base import BaseDriver


class MyDeviceDriver(BaseDriver):
    """
    장치 드라이버 구현.

    Attributes:
        port: 시리얼 포트 경로
        baudrate: 통신 속도
    """

    def __init__(
        self,
        name: str = "MyDeviceDriver",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        드라이버 초기화.

        Args:
            name: 드라이버 이름
            config: 설정 (port, baudrate 등)
        """
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB0")
        self.baudrate = self.config.get("baudrate", 9600)

        # 내부 상태
        self._model = "MyDevice-1000"
        self._serial = f"DEV{random.randint(1000, 9999)}"

    async def connect(self) -> bool:
        """하드웨어 연결."""
        # 실제 구현에서는 시리얼 포트 열기 등
        await asyncio.sleep(0.1)  # 연결 지연 시뮬레이션
        self._connected = True
        return True

    async def disconnect(self) -> None:
        """하드웨어 연결 해제."""
        await asyncio.sleep(0.02)
        self._connected = False

    async def reset(self) -> None:
        """하드웨어 리셋."""
        if not self._connected:
            raise RuntimeError("Device is not connected")
        await asyncio.sleep(0.05)

    async def identify(self) -> str:
        """장치 식별 문자열."""
        return f"MyCompany,{self._model},{self._serial},1.0.0"

    # === 측정 메서드 ===

    async def measure(self) -> float:
        """
        값 측정.

        Returns:
            float: 측정값
        """
        if not self._connected:
            raise RuntimeError("Device is not connected")

        await asyncio.sleep(0.05)  # 측정 시간

        # 실제 구현에서는 장치에서 값 읽기
        value = random.gauss(10.0, 0.1)
        return round(value, 4)

    async def measure_multiple(self, count: int = 10) -> list[float]:
        """
        여러 번 측정.

        Args:
            count: 측정 횟수

        Returns:
            list: 측정값 목록
        """
        samples = []
        for _ in range(count):
            sample = await self.measure()
            samples.append(sample)
        return samples

    # === 제어 메서드 ===

    async def set_output(self, value: float) -> float:
        """
        출력 설정.

        Args:
            value: 설정할 값

        Returns:
            float: 실제 설정된 값
        """
        if not self._connected:
            raise RuntimeError("Device is not connected")

        if value < 0 or value > 100:
            raise ValueError("Value must be between 0 and 100")

        await asyncio.sleep(0.05)
        return value

    async def enable_output(self) -> bool:
        """출력 활성화."""
        if not self._connected:
            raise RuntimeError("Device is not connected")
        await asyncio.sleep(0.02)
        return True

    async def disable_output(self) -> bool:
        """출력 비활성화."""
        if not self._connected:
            raise RuntimeError("Device is not connected")
        await asyncio.sleep(0.02)
        return True
```

### 5.3 Mock 드라이버 vs 실제 드라이버

개발 및 테스트를 위해 Mock 드라이버를 먼저 구현하고, 이후 실제 하드웨어 드라이버로 교체합니다:

```python
# Mock 드라이버 (테스트용)
class MockPowerSupply(BaseDriver):
    async def measure_voltage(self) -> float:
        # 시뮬레이션 값 반환
        return random.gauss(12.0, 0.1)

# 실제 드라이버 (하드웨어용)
class RealPowerSupply(BaseDriver):
    async def measure_voltage(self) -> float:
        # 실제 장치에서 SCPI 명령으로 값 읽기
        response = await self._send_command("MEAS:VOLT?")
        return float(response)
```

---

## 6. CLI 실행 및 JSON Lines 프로토콜

SDK 기반 시퀀스는 subprocess로 실행되며, stdout으로 JSON Lines 형식의 메시지를 출력합니다.

### 6.1 JSON Lines 메시지 형식

모든 메시지는 단일 JSON 라인으로 출력됩니다:

```json
{"type": "step_start", "timestamp": "2024-01-15T10:30:45.123", "execution_id": "abc123", "data": {...}}
```

### 6.2 메시지 타입

| 타입 | 설명 | data 필드 |
|------|------|-----------|
| `log` | 로그 메시지 | `level`, `message` |
| `step_start` | 스텝 시작 | `step`, `index`, `total`, `description` |
| `step_complete` | 스텝 완료 | `step`, `index`, `passed`, `duration`, `measurements`, `error` |
| `measurement` | 측정값 기록 | `name`, `value`, `unit`, `passed`, `min`, `max` |
| `error` | 에러 발생 | `code`, `message`, `step`, `recoverable` |
| `status` | 상태 업데이트 | `status`, `progress`, `current_step`, `message` |
| `sequence_complete` | 시퀀스 완료 | `overall_pass`, `duration`, `steps`, `measurements`, `error` |
| `input_request` | 입력 요청 | `id`, `prompt`, `input_type`, `timeout` |

### 6.3 메시지 예시

```json
// 스텝 시작
{"type": "step_start", "timestamp": "...", "execution_id": "abc123", "data": {"step": "initialize", "index": 1, "total": 3}}

// 측정값
{"type": "measurement", "timestamp": "...", "execution_id": "abc123", "data": {"name": "voltage", "value": 3.28, "unit": "V", "passed": true, "min": 3.0, "max": 3.6}}

// 스텝 완료
{"type": "step_complete", "timestamp": "...", "execution_id": "abc123", "data": {"step": "initialize", "index": 1, "passed": true, "duration": 1.5}}

// 시퀀스 완료
{"type": "sequence_complete", "timestamp": "...", "execution_id": "abc123", "data": {"overall_pass": true, "duration": 10.5, "steps": [...], "measurements": {...}}}
```

### 6.4 입력 요청/응답

수동 모드에서 사용자 입력이 필요한 경우:

```json
// stdout: 입력 요청
{"type": "input_request", "data": {"id": "input-1", "prompt": "시리얼 번호 입력:", "input_type": "text", "timeout": 60}}

// stdin: 입력 응답 (Station Service에서 전송)
{"type": "input_response", "data": {"id": "input-1", "value": "SN-12345"}}
```

---

## 7. 예제: 새 시퀀스 만들기

### 7.1 폴더 구조 생성

```bash
cd sequences/

mkdir -p my_new_test
mkdir -p my_new_test/drivers

touch my_new_test/__init__.py
touch my_new_test/main.py        # CLI 진입점 (새로 추가)
touch my_new_test/sequence.py
touch my_new_test/manifest.yaml
touch my_new_test/drivers/__init__.py
touch my_new_test/drivers/base.py
touch my_new_test/drivers/my_device.py
```

### 7.2 manifest.yaml 작성

```yaml
name: my_new_test
version: "1.0.0"
author: "개발팀"
description: |
  새로운 테스트 시퀀스입니다.

modes:
  automatic: true
  manual: true
  cli: true  # CLI 모드 활성화

entry_point:
  module: sequence
  class: MyNewTestSequence
  cli_main: main  # main.py 지정

hardware:
  test_device:
    display_name: "테스트 장치"
    driver: my_device
    class: MyDeviceDriver
    description: "테스트에 사용되는 장치"
    config_schema:
      port:
        type: string
        default: "/dev/ttyUSB0"
    manual_commands:
      - name: measure
        display_name: "측정"
        category: measurement
        parameters: []
        returns:
          type: float

parameters:
  target_value:
    display_name: "목표값"
    type: float
    default: 10.0
    min: 0.0
    max: 100.0
    unit: ""
    description: "테스트 목표값"
  tolerance:
    display_name: "허용 오차"
    type: float
    default: 5.0
    min: 0.1
    max: 20.0
    unit: "%"
    description: "허용 오차 비율"

dependencies:
  python: []
```

### 7.3 드라이버 구현

`drivers/base.py`:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDriver(ABC):
    def __init__(self, name: str = "BaseDriver", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self._connected = False

    @abstractmethod
    async def connect(self) -> bool:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def reset(self) -> None:
        ...

    async def identify(self) -> str:
        return "Unknown"

    async def is_connected(self) -> bool:
        return self._connected
```

`drivers/my_device.py`:
```python
import asyncio
import random
from typing import Any, Dict, Optional

from .base import BaseDriver


class MyDeviceDriver(BaseDriver):
    def __init__(self, name: str = "MyDeviceDriver", config: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB0")

    async def connect(self) -> bool:
        await asyncio.sleep(0.1)
        self._connected = True
        return True

    async def disconnect(self) -> None:
        await asyncio.sleep(0.02)
        self._connected = False

    async def reset(self) -> None:
        if not self._connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.05)

    async def identify(self) -> str:
        return f"MyCompany,MyDevice,SN{random.randint(1000,9999)},1.0"

    async def measure(self) -> float:
        if not self._connected:
            raise RuntimeError("Not connected")
        await asyncio.sleep(0.05)
        return round(random.gauss(10.0, 0.5), 4)
```

`drivers/__init__.py`:
```python
from .my_device import MyDeviceDriver

__all__ = ["MyDeviceDriver"]
```

### 7.4 main.py (CLI 진입점)

`main.py`:
```python
"""CLI entry point for the sequence."""

from .sequence import MyNewTestSequence

if __name__ == "__main__":
    exit(MyNewTestSequence.run_from_cli())
```

### 7.5 시퀀스 구현

`sequence.py`:
```python
"""
My New Test Sequence (SDK 기반)
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from station_service.sdk import SequenceBase

from .drivers.my_device import MyDeviceDriver

logger = logging.getLogger(__name__)


class MyNewTestSequence(SequenceBase):
    """새로운 테스트 시퀀스 (SequenceBase 상속)."""

    name = "my_new_test"
    version = "1.0.0"

    async def setup(self) -> None:
        """하드웨어 초기화."""
        self.emit_log("info", "Setting up sequence...")

        # 파라미터 로드
        self.target_value = self.get_parameter("target_value", 10.0)
        self.tolerance = self.get_parameter("tolerance", 5.0)

        # 드라이버 초기화
        device_config = self.hardware.get("test_device", {})
        self.device = MyDeviceDriver(config=device_config)
        await self.device.connect()

        idn = await self.device.identify()
        await self.device.reset()
        self.emit_log("info", f"Device connected: {idn}")

    async def run(self) -> Dict[str, Any]:
        """메인 시퀀스 로직."""
        results = {"measurements": {}, "steps": []}

        # Step 1: 다중 측정
        self.emit_step_start("measurement", 1, 1, "다중 측정 실행")
        start_time = time.perf_counter()

        try:
            samples = []
            for i in range(10):
                value = await self.device.measure()
                samples.append(value)
                self.emit_log("debug", f"Sample {i+1}: {value}")

            avg_value = sum(samples) / len(samples)
            results["measurements"]["average"] = round(avg_value, 4)
            results["measurements"]["samples"] = samples

            # 측정값 기록
            self.emit_measurement(
                "average_value",
                avg_value,
                "",
                passed=None,  # 판정 전
                min_value=self.target_value * (1 - self.tolerance / 100),
                max_value=self.target_value * (1 + self.tolerance / 100),
            )

            # 판정
            deviation = abs(avg_value - self.target_value) / self.target_value * 100
            passed = deviation <= self.tolerance

            duration = time.perf_counter() - start_time
            self.emit_step_complete(
                "measurement", 1, passed, duration,
                measurements={"average": avg_value, "deviation": deviation}
            )
            results["steps"].append({"name": "measurement", "passed": passed})

            if not passed:
                raise ValueError(f"Deviation {deviation:.2f}% exceeds tolerance {self.tolerance}%")

        except Exception as e:
            duration = time.perf_counter() - start_time
            self.emit_step_complete("measurement", 1, False, duration, error=str(e))
            results["steps"].append({"name": "measurement", "passed": False, "error": str(e)})
            raise

        return results

    async def teardown(self) -> None:
        """리소스 정리."""
        self.emit_log("info", "Cleaning up...")

        if hasattr(self, 'device') and self.device:
            if await self.device.is_connected():
                await self.device.disconnect()

        self.emit_log("info", "Cleanup complete.")
```

`__init__.py`:
```python
"""My New Test Sequence Package"""

__all__ = ["MyNewTestSequence"]
```

---

## 8. 베스트 프랙티스

### 8.1 에러 처리

SDK 기반 시퀀스에서는 `emit_error()`를 사용하여 에러를 보고합니다:

```python
async def run(self) -> Dict[str, Any]:
    results = {"measurements": {}, "steps": []}

    try:
        value = await self.device.measure()
        results["measurements"]["value"] = value

    except TimeoutError:
        self.emit_error("TIMEOUT", "Measurement timeout", step="measurement")
        raise

    except ConnectionError as e:
        self.emit_error("CONNECTION", f"Connection lost: {e}", step="measurement", recoverable=True)
        raise

    except Exception as e:
        self.emit_error("UNKNOWN", str(e), step="measurement")
        raise

    return results
```

### 8.2 리소스 정리

`teardown()` 메서드는 항상 실행됩니다 (실패 시에도):

```python
async def teardown(self) -> None:
    """리소스 정리 - 항상 실행됨."""
    cleanup_results = []

    # 여러 장치 순차 정리
    if hasattr(self, 'power_supply') and self.power_supply:
        try:
            await self.power_supply.output_off()
            await self.power_supply.disconnect()
            cleanup_results.append(("power_supply", "ok"))
        except Exception as e:
            self.emit_log("warning", f"Power supply cleanup failed: {e}")
            cleanup_results.append(("power_supply", str(e)))

    if hasattr(self, 'gpio') and self.gpio:
        try:
            await self.gpio.all_outputs_off()
            await self.gpio.disconnect()
            cleanup_results.append(("gpio", "ok"))
        except Exception as e:
            self.emit_log("warning", f"GPIO cleanup failed: {e}")
            cleanup_results.append(("gpio", str(e)))

    self.emit_log("info", f"Cleanup complete: {cleanup_results}")
```

### 8.3 로깅

SDK에서는 `emit_log()`를 사용합니다 (JSON Lines로 출력됨):

```python
# 중요한 이벤트
self.emit_log("info", "Test started")
self.emit_log("info", "Test completed with result: PASS")

# 디버깅 정보
self.emit_log("debug", f"Measured value: {value}")
self.emit_log("debug", f"Parameters: {self.parameters}")

# 경고
self.emit_log("warning", f"Value {value} close to limit")

# 에러 (emit_error와 별개)
self.emit_log("error", f"Test failed: {error}")
```

### 8.4 타임아웃 설정

| 작업 유형 | 권장 타임아웃 |
|----------|--------------|
| 초기화/연결 | 30초 |
| 측정 (단순) | 30-60초 |
| 측정 (복잡) | 60-120초 |
| 정리 | 30초 |
| 긴 프로세스 | 300초 이상 |

### 8.5 파라미터 검증

`setup()` 메서드에서 파라미터를 검증합니다:

```python
async def setup(self) -> None:
    # 파라미터 로드 및 검증
    self.voltage = self.get_parameter("voltage", 12.0)
    if not 0 <= self.voltage <= 30:
        raise ValueError(f"Voltage {self.voltage} out of range (0-30V)")

    self.tolerance = self.get_parameter("tolerance", 5.0)
    if not 0.1 <= self.tolerance <= 20:
        raise ValueError(f"Tolerance {self.tolerance} out of range (0.1-20%)")

    self.emit_log("info", f"Parameters validated: voltage={self.voltage}V, tolerance={self.tolerance}%")
```

### 8.6 스텝 실행 패턴

일관된 스텝 실행 패턴을 사용합니다:

```python
async def _run_step(self, step_name: str, index: int, total: int, func) -> bool:
    """공통 스텝 실행 패턴."""
    self.emit_step_start(step_name, index, total)
    start_time = time.perf_counter()

    try:
        result = await func()
        duration = time.perf_counter() - start_time
        self.emit_step_complete(step_name, index, True, duration, measurements=result)
        return True

    except Exception as e:
        duration = time.perf_counter() - start_time
        self.emit_step_complete(step_name, index, False, duration, error=str(e))
        self.emit_error("STEP_FAILED", str(e), step=step_name)
        return False
```

---

## 9. 레거시: 데코레이터 방식

> **Note**: 새로운 시퀀스는 SDK 기반 (SequenceBase 상속)으로 개발하는 것을 권장합니다.
> 이 섹션은 기존 시퀀스의 유지보수를 위해 제공됩니다.

### 9.1 @sequence 데코레이터

```python
from station_service.sequence.decorators import sequence

@sequence(
    name="sequence_name",
    description="설명",
    version="1.0.0"
)
class MySequence:
    pass
```

### 9.2 @step 데코레이터

```python
from station_service.sequence.decorators import step

@step(order=1, timeout=60.0, retry=0, cleanup=False)
async def my_step(self) -> Dict[str, Any]:
    return {"step": "my_step", "status": "passed", "data": {}}
```

### 9.3 @parameter 데코레이터

```python
from station_service.sequence.decorators import parameter

@parameter(name="voltage", display_name="Voltage", unit="V", description="테스트 전압")
def get_voltage(self) -> float:
    return self._voltage
```

---

## 참고 자료

- [Station Service SDK 소스코드](../station_service/sdk/)
- [예제 시퀀스](../sequences/)
- [Python asyncio 문서](https://docs.python.org/3/library/asyncio.html)
- [JSON Lines 형식](https://jsonlines.org/)
