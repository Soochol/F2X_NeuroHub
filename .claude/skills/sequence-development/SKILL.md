---
name: sequence-development
description: NeuroHub Station Service 테스트 시퀀스 개발 가이드. 데코레이터 패턴, 드라이버 구현, manifest.yaml 작성 포함.
---

# Sequence Development

NeuroHub Station Service용 테스트 시퀀스 개발 가이드입니다.

## 핵심 원칙

1. **데코레이터 패턴**: `@sequence`, `@step`, `@parameter` 데코레이터 필수 사용
2. **BaseDriver 상속**: 모든 드라이버는 BaseDriver 추상 클래스 상속
3. **비동기 메서드**: 모든 step과 driver 메서드는 `async` 함수
4. **manifest.yaml**: 시퀀스 메타데이터 정의 필수

---

## Quick Start

### 1. 폴더 구조 생성

```bash
sequences/
└── my_sequence/
    ├── __init__.py
    ├── manifest.yaml
    ├── sequence.py
    ├── drivers/
    │   ├── __init__.py
    │   ├── base.py
    │   └── my_device.py
    └── libs/                    # (선택) 내부 의존성
        └── my_protocol/
            └── __init__.py
```

### 2. sequences/__init__.py 등록

```python
__all__ = ["sensor_inspection", "manual_test", "my_sequence"]  # 추가!
```

---

## 데코레이터 사용법

### @sequence (클래스)

```python
from station_service.sequence.decorators import sequence, step, parameter

@sequence(
    name="my_sequence",           # Python 식별자
    description="시퀀스 설명",
    version="1.0.0"
)
class MySequence:
    pass
```

### @step (메서드)

```python
@step(order=1, timeout=30.0)
async def initialize(self) -> Dict[str, Any]:
    """하드웨어 초기화."""
    ...

@step(order=2, timeout=60.0, retry=1)
async def run_test(self) -> Dict[str, Any]:
    """테스트 실행. 실패 시 1회 재시도."""
    ...

@step(order=99, timeout=10.0, cleanup=True)
async def finalize(self) -> Dict[str, Any]:
    """정리. 이전 스텝 실패해도 항상 실행."""
    ...
```

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `order` | int | (필수) | 실행 순서 (낮을수록 먼저) |
| `timeout` | float | 60.0 | 최대 실행 시간 (초) |
| `retry` | int | 0 | 실패 시 재시도 횟수 |
| `cleanup` | bool | False | True면 항상 실행 |

### @parameter (프로퍼티)

```python
@parameter(
    name="target_value",
    display_name="목표값",
    unit="V",
    description="테스트 기준값"
)
def get_target_value(self) -> float:
    return self.target_value
```

---

## Step 반환값 구조

모든 step은 다음 구조의 Dict를 반환해야 합니다:

```python
{
    "step": "step_name",          # 스텝 식별자
    "status": "passed",           # "passed", "failed", "skipped"
    "data": {                     # 수집된 데이터
        "measured_value": 12.5,
        "device_idn": "...",
    },
    "error": "error message"      # 실패 시에만 (optional)
}
```

---

## Driver 구현

### BaseDriver 추상 클래스

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseDriver(ABC):
    def __init__(self, name: str = "BaseDriver", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self._connected = False

    @abstractmethod
    async def connect(self) -> bool: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def reset(self) -> None: ...

    async def identify(self) -> str:
        return "Unknown"

    async def is_connected(self) -> bool:
        return self._connected
```

### 드라이버 구현 예시

```python
from .base import BaseDriver

class MyDeviceDriver(BaseDriver):
    def __init__(self, name: str = "MyDevice", config: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, config=config)
        self.port = self.config.get("port", "/dev/ttyUSB0")

    async def connect(self) -> bool:
        # 연결 로직
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def reset(self) -> None:
        if not self._connected:
            raise RuntimeError("Not connected")

    async def measure(self) -> float:
        """측정 메서드."""
        if not self._connected:
            raise RuntimeError("Not connected")
        return 10.0  # 실제 측정값
```

---

## manifest.yaml 구조

```yaml
name: my_sequence
version: "1.0.0"
author: "개발팀"
description: |
  시퀀스 설명

modes:
  automatic: true
  manual: true

entry_point:
  module: sequence
  class: MySequenceClass

hardware:
  device_name:
    display_name: "장치 표시명"
    driver: driver_module
    class: DriverClassName
    config_schema:
      port:
        type: string
        default: "/dev/ttyUSB0"
    manual_commands:
      - name: measure
        display_name: "측정"
        category: measurement
        parameters: []

parameters:
  target_value:
    display_name: "목표값"
    type: float
    default: 10.0
    min: 0.0
    max: 100.0
    unit: "V"

steps:
  - name: initialize
    display_name: "초기화"
    order: 1
    timeout: 30.0

  - name: finalize
    display_name: "정리"
    order: 99
    cleanup: true

dependencies:
  python:
    - pyserial>=3.5
```

---

## 시퀀스 클래스 템플릿

```python
"""
My Test Sequence
"""

import logging
from typing import Any, Dict, List, Optional

from station_service.sequence.decorators import parameter, sequence, step
from .drivers.my_device import MyDeviceDriver

logger = logging.getLogger(__name__)


@sequence(
    name="my_sequence",
    description="테스트 시퀀스",
    version="1.0.0"
)
class MySequence:
    def __init__(
        self,
        hardware: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        self.hardware = hardware or {}
        self.parameters = parameters or {}
        self.results: List[Dict[str, Any]] = []

        # 하드웨어 드라이버
        self.device: Optional[MyDeviceDriver] = self.hardware.get("device_name")

        # 파라미터 로드
        self.target_value: float = self.parameters.get("target_value", 10.0)

    @step(order=1, timeout=30.0)
    async def initialize(self) -> Dict[str, Any]:
        """하드웨어 초기화."""
        result = {"step": "initialize", "status": "passed", "data": {}}

        try:
            if self.device:
                connected = await self.device.connect()
                if not connected:
                    result["status"] = "failed"
                    result["error"] = "Connection failed"
                    return result

                idn = await self.device.identify()
                result["data"]["device_idn"] = idn

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.exception(f"Initialize failed: {e}")

        return result

    @step(order=2, timeout=60.0, retry=1)
    async def run_test(self) -> Dict[str, Any]:
        """테스트 실행."""
        result = {"step": "run_test", "status": "passed", "data": {}}

        try:
            if not self.device:
                result["status"] = "failed"
                result["error"] = "Device not available"
                return result

            value = await self.device.measure()
            result["data"]["measured"] = value

            # 판정
            tolerance = self.target_value * 0.05
            if abs(value - self.target_value) <= tolerance:
                result["data"]["passed"] = True
            else:
                result["status"] = "failed"
                result["error"] = f"Value {value} out of tolerance"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        self.results.append(result)
        return result

    @step(order=99, timeout=10.0, cleanup=True)
    async def finalize(self) -> Dict[str, Any]:
        """리소스 정리."""
        result = {"step": "finalize", "status": "passed", "data": {}}

        try:
            if self.device and await self.device.is_connected():
                await self.device.disconnect()
            result["data"]["cleanup_completed"] = True
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    @parameter(name="target_value", display_name="목표값", unit="V", description="테스트 기준값")
    def get_target_value(self) -> float:
        return self.target_value
```

---

## 타임아웃 권장값

| 작업 유형 | 권장 타임아웃 |
|----------|--------------|
| 초기화/연결 | 30초 |
| 측정 (단순) | 30-60초 |
| 측정 (복잡) | 60-120초 |
| 정리 | 10-30초 |
| 센서 워밍업 | 60초 이상 |

---

## 체크리스트

### 필수

- [ ] `@sequence` 데코레이터 적용
- [ ] 모든 step에 `@step` 데코레이터
- [ ] cleanup step에 `cleanup=True`
- [ ] `manifest.yaml` 작성
- [ ] `sequences/__init__.py` 등록
- [ ] `drivers/base.py` BaseDriver 클래스
- [ ] 모든 메서드 `async` 정의

### 권장

- [ ] `@parameter` 데코레이터로 파라미터 노출
- [ ] 적절한 timeout 설정
- [ ] 재시도가 필요한 step에 `retry` 설정
- [ ] 로깅 (`logger.info`, `logger.error`)
- [ ] Lazy import 패턴 사용 (외부 의존성 있는 경우)

### Self-contained (배포용)

시퀀스 폴더만 복사해도 독립적으로 동작해야 합니다:

- [ ] `libs/` 폴더에 내부 라이브러리 **실제 코드** 포함 (re-export만 하면 안됨)
- [ ] 외부 프로젝트 경로 참조 없음 (`host_tools/`, 상위 폴더 등)
- [ ] pip 의존성은 `manifest.yaml` dependencies에 모두 명시
- [ ] 시퀀스 폴더만 다른 위치로 복사 후 import 테스트 통과

**검증 방법:**
```bash
# 시퀀스 폴더를 임시 위치로 복사
cp -r sequences/my_sequence /tmp/

# 독립 실행 테스트
cd /tmp/my_sequence
python -c "from sequence import MySequence; print('OK')"
```

---

## 의존성 관리

시퀀스의 의존성은 **Self-contained** 또는 **External** 방식으로 관리합니다.

### 의존성 처리 전략

| 의존성 종류 | 처리 방법 |
|------------|----------|
| **표준 pip 패키지** (pyserial, numpy 등) | `manifest.yaml` dependencies → 자동 설치 |
| **내부 커스텀 라이브러리** (프로토콜 등) | `libs/` 폴더에 포함 (Self-contained) |
| **대용량/복잡한 패키지** (tensorflow 등) | Docker 이미지에 포함 |

### 1. External Dependencies (자동 설치)

`manifest.yaml`에 명시하면 **업로드 시 자동 설치**됩니다:

```yaml
dependencies:
  python:
    - pyserial>=3.5
    - numpy>=1.20.0
    - requests>=2.25.0
```

**API 응답 예시** (`POST /api/sequences/upload`):

```json
{
  "success": true,
  "data": {
    "name": "my_sequence",
    "dependencies": {
      "total": 2,
      "installed": 1,
      "skipped": 1,
      "failed": 0,
      "details": [
        {"package": "pyserial>=3.5", "success": true, "already_installed": true},
        {"package": "numpy>=1.20.0", "success": true, "already_installed": false}
      ]
    }
  },
  "message": "Package 'my_sequence' uploaded successfully (1 deps installed, 1 skipped)"
}
```

### 2. Internal Dependencies (libs/ 폴더)

커스텀 프로토콜 등 내부 라이브러리는 `libs/` 폴더에 포함:

```bash
my_sequence/
├── sequence.py
├── drivers/
│   └── my_device.py      # libs/ 참조
└── libs/
    └── my_protocol/
        ├── __init__.py
        ├── client.py
        └── transport.py
```

**드라이버에서 libs/ 참조**:

```python
# drivers/my_device.py
import sys
from pathlib import Path

# libs 폴더를 sys.path에 추가
_libs_path = Path(__file__).parent.parent / "libs"
if str(_libs_path) not in sys.path:
    sys.path.insert(0, str(_libs_path))

from my_protocol import MyClient, MyTransport
```

### 3. Lazy Import 패턴 (권장)

외부 의존성이 있는 드라이버는 **lazy import**로 메타데이터 추출 시 에러를 방지합니다.
(순환 import 방지 패턴은 [순환 Import 방지](#순환-import-방지) 섹션 참조)

```python
# sequence.py - 의존성 없어도 메타데이터 추출 가능
def _get_driver_class():
    from .drivers.my_device import MyDeviceDriver
    return MyDeviceDriver

@sequence(name="my_sequence", ...)
class MySequence:
    def __init__(self, hardware=None, parameters=None):
        self.device = hardware.get("device_name") if hardware else None
        if self.device is None:
            self.device = _get_driver_class()(config={...})
```

**장점**: UI에서 step 목록 조회 가능 (의존성 미설치 상태에서도)

---

## 내부 라이브러리 (libs/) 만들기

pip로 설치할 수 없는 커스텀 프로토콜, 유틸리티는 `libs/` 폴더에 포함합니다.

### libs/ 폴더 구조

```bash
my_sequence/
└── libs/
    └── my_protocol/
        ├── __init__.py       # 패키지 초기화 및 exports
        ├── exceptions.py     # 예외 클래스
        ├── transport.py      # 저수준 통신 (시리얼, TCP 등)
        └── client.py         # 고수준 프로토콜 클라이언트
```

### 1. exceptions.py - 예외 클래스

```python
"""프로토콜 예외 클래스."""

class MyProtocolError(Exception):
    """Base exception for protocol."""
    pass

class TimeoutError(MyProtocolError):
    """Response timeout."""
    pass

class NAKError(MyProtocolError):
    """Device returned NAK."""
    def __init__(self, message: str = "NAK", error_code: int = 0):
        super().__init__(message)
        self.error_code = error_code
```

### 2. transport.py - 저수준 통신

```python
"""저수준 통신 처리."""
import serial  # manifest.yaml dependencies에 명시
from .exceptions import TimeoutError

class MyTransport:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 5.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def open(self) -> None:
        self._serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
        )

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()

    def write(self, data: bytes) -> int:
        return self._serial.write(data)

    def read(self, size: int) -> bytes:
        data = self._serial.read(size)
        if len(data) < size:
            raise TimeoutError(f"Expected {size} bytes, got {len(data)}")
        return data
```

### 3. client.py - 고수준 클라이언트

```python
"""프로토콜 클라이언트."""
from .transport import MyTransport
from .exceptions import NAKError

class MyClient:
    STX = 0x02
    ETX = 0x03
    ACK = 0x06
    NAK = 0x15

    def __init__(self, transport: MyTransport):
        self.transport = transport

    def ping(self) -> tuple:
        """PING 전송 및 버전 반환."""
        response = self._send_command(b"PING")
        parts = response.decode().split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def measure(self) -> float:
        """측정값 반환."""
        response = self._send_command(b"MEAS?")
        return float(response.decode())

    def _send_command(self, cmd: bytes) -> bytes:
        """명령 전송 및 응답 수신."""
        frame = bytes([self.STX]) + cmd + bytes([self.ETX])
        self.transport.write(frame)
        return self._read_response()

    def _read_response(self) -> bytes:
        header = self.transport.read(1)
        if header[0] == self.NAK:
            raise NAKError("Device returned NAK")
        # ... 응답 파싱
```

### 4. __init__.py - 패키지 exports

```python
"""My Protocol Package."""
from .transport import MyTransport
from .client import MyClient
from .exceptions import MyProtocolError, TimeoutError, NAKError

__all__ = ["MyTransport", "MyClient", "MyProtocolError", "TimeoutError", "NAKError"]
__version__ = "1.0.0"
```

### 5. 드라이버에서 libs/ 사용

```python
# drivers/my_device.py
import sys
from pathlib import Path

# libs 폴더를 sys.path에 추가
_libs_path = Path(__file__).parent.parent / "libs"
if str(_libs_path) not in sys.path:
    sys.path.insert(0, str(_libs_path))

from my_protocol import MyClient, MyTransport
from my_protocol.exceptions import NAKError, TimeoutError

from .base import BaseDriver


class MyDeviceDriver(BaseDriver):
    def __init__(self, name: str = "MyDevice", config=None):
        super().__init__(name=name, config=config)
        self._transport = None
        self._client = None

    async def connect(self) -> bool:
        self._transport = MyTransport(
            port=self.config.get("port", "/dev/ttyUSB0"),
            baudrate=self.config.get("baudrate", 115200),
        )
        self._transport.open()
        self._client = MyClient(self._transport)
        self._connected = True
        return True

    async def disconnect(self) -> None:
        if self._transport:
            self._transport.close()
        self._connected = False
```

### libs/ 작성 체크리스트

- [ ] `__init__.py`에서 public API export (`__all__`)
- [ ] 예외 클래스 정의 (`exceptions.py`)
- [ ] 외부 의존성은 `manifest.yaml` dependencies에 명시
- [ ] 드라이버에서 `sys.path` 설정 후 import
- [ ] 문서화 (docstring)

## 순환 Import 방지

Python의 순환 import는 `ImportError` 또는 `Broken pipe` 에러를 발생시킵니다.
특히 subprocess 환경에서는 즉시 크래시됩니다.

### 공통 원칙

#### 1. Import 방향 규칙 (단방향만 허용)

```
[시퀀스]                    [Station Service]
sequence.py                 api/routes
    ↓                           ↓
drivers/                    batch/, models/
    ↓                           ↓
libs/                       core/
```

**금지**: 하위 → 상위 방향 import

#### 2. `__init__.py` Lazy Import 패턴

**❌ Eager import (문제)**
```python
from .manager import Manager  # 즉시 로드 → 순환 위험
```

**✅ Lazy import (해결)**
```python
def __getattr__(name: str):
    if name == "Manager":
        from .manager import Manager
        return Manager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Manager"]
```

#### 3. 타입 힌트 순환 해결

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sequence import MySequence  # 런타임에 로드 안됨

class Driver:
    def set_sequence(self, seq: "MySequence"): ...  # 문자열 어노테이션
```

#### 4. 검증 방법

```bash
# 순환 import 시각화
pip install pycycle
pycycle --source <package>/

# 수동 import 테스트
python -c "from <module> import <Class>; print('OK')"
```

---

### 시퀀스 개발 시 적용

시퀀스 내부 모듈 간 import 규칙입니다.

#### Import 방향

| From | To | 허용 |
|------|-----|------|
| sequence.py | drivers/ | ✅ |
| drivers/ | libs/ | ✅ |
| libs/ | drivers/ | ❌ |
| drivers/ | sequence.py | ❌ |

#### 체크리스트

- [ ] sequence.py에서만 drivers를 import
- [ ] drivers에서만 libs를 import
- [ ] libs는 다른 시퀀스 모듈을 import하지 않음
- [ ] `..`으로 시퀀스 폴더 밖 참조 금지

#### 검증

```bash
cd sequences/my_sequence
python -c "from libs.my_protocol import MyClient; print('libs OK')"
python -c "from drivers.base import BaseDriver; print('drivers OK')"
python -c "from sequence import MySequence; print('sequence OK')"
```

---

### Station Service 적용 (Critical)

BatchWorker가 **subprocess**로 실행될 때 순환 import가 있으면 `Broken pipe`로 크래시됩니다.

#### 발생 원인

```
batch/__init__.py (eager import)
    → manager.py → models/ → api/schemas/
    → api/__init__.py → routes → batch/ (순환!)

결과: subprocess 즉시 종료 → "Broken pipe"
```

#### 공유 모델 분리

**❌ 문제**: models/가 api/를 참조
```python
# models/messages.py
from station_service.api.schemas.base import APIBaseModel  # api/ 전체 로드!
```

**✅ 해결**: 독립 core/ 패키지로 분리
```python
# core/base.py (새 위치)
class APIBaseModel(BaseModel): ...

# models/messages.py
from station_service.core.base import APIBaseModel  # core/만 로드
```

#### Subprocess Import 테스트

```bash
python -c "
from station_service.batch.worker import BatchWorker
from station_service.models.config import BatchConfig
print('Subprocess imports OK')
"
```

#### 신규 모듈 추가 시 체크리스트

- [ ] `__init__.py`에 eager import 추가하지 않음
- [ ] 새 모듈이 `api/` 패키지를 import하는지 확인
- [ ] subprocess import 테스트 실행

#### 문제 사례

| 증상 | 원인 | 해결 |
|------|------|------|
| `Broken pipe` on batch start | `__init__.py` eager import | `__getattr__` 패턴 |
| `cannot import 'X'` | models/ → api/ 참조 | core/로 분리 |
| subprocess 즉시 종료 | routes → batch 참조 | lazy import |

---

## References

### 템플릿
- **[templates/](./templates/)** - 시퀀스 템플릿 파일
  - `sequence.py` - 시퀀스 클래스 템플릿 (Lazy import 패턴 포함)
  - `manifest.yaml` - 매니페스트 템플릿
  - `drivers/` - 드라이버 템플릿
  - `libs/` - 내부 라이브러리 템플릿 (프로토콜 예시)

