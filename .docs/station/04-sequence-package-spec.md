# 04. Sequence Package - 요구사항 명세

## 구현 체크리스트

> Phase 2.1 - 시퀀스 패키지 구조

### 패키지 구조 생성
- [x] `sequences/` 루트 디렉토리 생성
- [x] 예제 패키지: `sequences/example_test/` 구조 생성
  - [x] `manifest.yaml` - 패키지 메타데이터
  - [x] `sequence.py` - 시퀀스 메인 클래스
  - [x] `drivers/` - 드라이버 모듈
  - [x] `drivers/__init__.py`
  - [x] `drivers/base.py` - BaseDriver 추상 클래스
  - [x] `requirements.txt` - 패키지 의존성

### Manifest 스키마 검증
- [x] `station_service/sequence/manifest.py` - Manifest Pydantic 모델
- [x] YAML 로딩 및 검증 로직

---

## Document Information
- **Version**: 1.0.0
- **Date**: 2025-12-30
- **Type**: Requirements Specification
- **Related**: [05-sequence-package-design.md](./05-sequence-package-design.md) (상세 설계)

---

## 1. 개요

### 1.1 목적
**Sequence Package**는 테스트 시퀀스 로직, 하드웨어 드라이버, 설정을 하나의 배포 가능한 패키지로 캡슐화하는 자체 완결형 컴포넌트입니다.

### 1.2 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Self-contained** | 모든 필요 코드(드라이버, 유틸)가 함께 번들됨 |
| **Portable** | 폴더 복사만으로 배포, Station Service에 대한 외부 의존성 없음 |
| **Versioned** | 시맨틱 버저닝과 변경 추적 |
| **Documented** | manifest.yaml이 완전한 자기 문서화 제공 |
| **Type-Safe** | 완전한 타입 힌트와 Pydantic 검증 |
| **Async-First** | 모든 I/O 작업은 async/await |

---

## 2. 아키텍처 개요

### 2.1 컴포넌트 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SEQUENCE PACKAGE                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        manifest.yaml                                 │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │   Metadata    │  │   Hardware    │  │     Parameters        │   │   │
│  │  │ name, version │  │   Definitions │  │   UI-editable         │   │   │
│  │  │ author, desc  │  │   + configs   │  │   test settings       │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │         sequence.py              │  │          drivers/            │   │
│  │                                  │  │                              │   │
│  │  @sequence                       │  │  ┌────────────────────────┐ │   │
│  │  class TestSequence:             │  │  │      base.py           │ │   │
│  │                                  │  │  │  BaseDriver(ABC)       │ │   │
│  │    @parameter                    │  │  └────────────────────────┘ │   │
│  │    def voltage_limit(): ...      │  │                              │   │
│  │                                  │  │  ┌────────────────────────┐ │   │
│  │    @step(order=1)                │  │  │      dmm.py            │ │   │
│  │    async def initialize(): ...   │  │  │  KeysightDMM(Base)     │ │   │
│  │                                  │  │  └────────────────────────┘ │   │
│  │    @step(order=2)                │  │                              │   │
│  │    async def measure(): ...      │  │  ┌────────────────────────┐ │   │
│  │                                  │  │  │   power_supply.py      │ │   │
│  │    @step(cleanup=True)           │  │  │  AgilentPower(Base)    │ │   │
│  │    async def finalize(): ...     │  │  └────────────────────────┘ │   │
│  │                                  │  │                              │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐                                      │
│  │          utils/ (optional)       │                                      │
│  │  calculations.py, helpers.py     │                                      │
│  └──────────────────────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 패키지 구조

```
sequences/
└── pcb_voltage_test/              # 패키지 폴더명 = Package ID
    ├── __init__.py                # 패키지 초기화
    ├── manifest.yaml              # 메타데이터, 하드웨어, 파라미터
    ├── sequence.py                # 데코레이터가 적용된 메인 시퀀스 클래스
    │
    ├── drivers/                   # 하드웨어 드라이버 (번들됨)
    │   ├── __init__.py
    │   ├── base.py                # 선택: BaseDriver ABC
    │   ├── dmm.py                 # 디지털 멀티미터 드라이버
    │   └── power_supply.py        # 파워 서플라이 드라이버
    │
    └── utils/                     # 선택: 유틸리티
        ├── __init__.py
        └── calculations.py        # 헬퍼 함수
```

---

## 3. Manifest 스키마

### 3.1 전체 스키마

```yaml
# ============================================
# 기본 정보 (필수)
# ============================================
name: pcb_voltage_test              # Package ID (폴더명과 일치)
version: 1.2.0                      # 시맨틱 버전
author: "Engineering Team"
description: "PCB Voltage Test Sequence"
created_at: "2025-01-15"
updated_at: "2025-01-20"

# ============================================
# 엔트리 포인트 (필수)
# ============================================
entry_point:
  module: sequence                  # sequence.py
  class: PCBVoltageTest             # sequence.py 내 클래스명

# ============================================
# 하드웨어 정의
# ============================================
# Key = 시퀀스 코드에서 사용하는 Hardware ID
# 드라이버 경로는 패키지 루트 기준 상대 경로
hardware:
  dmm:
    display_name: "디지털 멀티미터"
    driver: "./drivers/dmm.py"
    class: "KeysightDMM"
    description: "Voltage/current measurement"
    config_schema:                  # Station이 제공하는 값
      port:
        type: string
        required: true
        description: "Serial port (e.g., /dev/ttyUSB0)"
      baudrate:
        type: integer
        default: 9600
        options: [9600, 19200, 38400, 115200]
      timeout:
        type: float
        default: 1.0
        min: 0.1
        max: 30.0

  power:
    display_name: "파워 서플라이"
    driver: "./drivers/power_supply.py"
    class: "AgilentPowerSupply"
    description: "Power supply control"
    config_schema:
      ip:
        type: string
        required: true
        description: "Device IP address"
      port:
        type: integer
        default: 5025
      timeout:
        type: float
        default: 5.0

# ============================================
# 시퀀스 파라미터 (UI 편집 가능)
# ============================================
parameters:
  voltage_limit:
    display_name: "전압 상한"
    type: float
    default: 5.5
    min: 0.0
    max: 50.0
    unit: "V"
    description: "Fail if exceeded"

  current_limit:
    display_name: "전류 상한"
    type: float
    default: 1.0
    min: 0.0
    max: 10.0
    unit: "A"

  test_points:
    display_name: "테스트 포인트 수"
    type: integer
    default: 10
    min: 1
    max: 100

  dut_type:
    display_name: "DUT 타입"
    type: string
    default: "TypeA"
    options: ["TypeA", "TypeB", "TypeC"]

  enable_aging:
    display_name: "에이징 테스트 활성화"
    type: boolean
    default: false

# ============================================
# 의존성 (선택)
# ============================================
dependencies:
  python:
    - pyserial>=3.5
    - numpy>=1.20.0
```

### 3.2 필드 요구사항

#### 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 패키지 식별자 (유효한 Python 식별자) |
| `version` | string | 시맨틱 버전 (X.Y.Z) |
| `entry_point.module` | string | Python 모듈명 (.py 제외) |
| `entry_point.class` | string | 시퀀스 클래스명 |

#### 선택 필드

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `author` | string | - | 작성자 |
| `description` | string | - | 패키지 설명 |
| `created_at` | string | - | 생성일 |
| `updated_at` | string | - | 수정일 |
| `hardware` | object | {} | 하드웨어 정의 |
| `parameters` | object | {} | UI 편집 가능 파라미터 |
| `dependencies` | object | {} | Python 패키지 의존성 |

### 3.3 파라미터 타입

| 타입 | 설명 | 추가 속성 |
|------|------|-----------|
| `string` | 문자열 | `options`: 선택 목록 |
| `integer` | 정수 | `min`, `max`, `options` |
| `float` | 실수 | `min`, `max`, `unit` |
| `boolean` | 불리언 | - |

---

## 4. 데코레이터 정의

### 4.1 @sequence

시퀀스 클래스를 표시합니다.

```python
@sequence(
    name: str,           # 시퀀스 표시 이름
    description: str,    # 설명
    version: str         # 버전 (기본: "1.0.0")
)
```

**예시:**
```python
@sequence(
    name="PCB_Voltage_Test",
    description="PCB voltage measurement sequence"
)
class PCBVoltageTest:
    ...
```

### 4.2 @step

테스트 Step 메서드를 표시합니다.

```python
@step(
    order: int,          # 실행 순서 (1-based, 고유해야 함)
    timeout: float,      # 최대 실행 시간 (초, 기본: 60)
    retry: int,          # 실패 시 재시도 횟수 (기본: 0)
    cleanup: bool,       # True면 에러 시에도 항상 실행 (기본: False)
    condition: str       # 파라미터명; 해당 파라미터가 truthy일 때만 실행
)
```

**예시:**
```python
@step(order=1, timeout=30, retry=3)
async def initialize(self) -> Dict[str, Any]:
    """Initialize equipment"""
    await self.power.reset()
    return {"status": "ready"}

@step(order=4, condition="enable_aging")
async def aging_test(self) -> Dict[str, Any]:
    """Only runs if enable_aging is True"""
    ...

@step(order=99, cleanup=True)
async def finalize(self) -> Dict[str, Any]:
    """Always runs, even on error"""
    ...
```

### 4.3 @parameter

외부 설정 가능한 파라미터를 정의합니다.

```python
@parameter(
    name: str,           # 파라미터 식별자 (manifest.yaml과 일치)
    display_name: str,   # UI 표시 이름
    unit: str,           # 단위 (예: "V", "A", "ms")
    description: str     # 설명
)
```

**예시:**
```python
@parameter(name="voltage_limit", display_name="Voltage Limit", unit="V")
def voltage_limit(self) -> float:
    return 5.5  # 기본값
```

---

## 5. 드라이버 인터페이스

### 5.1 필수 메서드

모든 드라이버는 다음 메서드를 구현해야 합니다:

```python
class BaseDriver(ABC):
    @abstractmethod
    async def connect(self) -> bool:
        """하드웨어 연결 수립"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """연결 종료 및 리소스 해제"""
        pass

    @abstractmethod
    async def reset(self) -> None:
        """하드웨어를 알려진 상태로 초기화"""
        pass
```

### 5.2 선택 메서드

```python
class BaseDriver(ABC):
    async def identify(self) -> str:
        """하드웨어 식별 정보 조회 (예: *IDN?)"""
        return "Unknown"

    async def is_connected(self) -> bool:
        """연결 상태 확인"""
        return True

    async def self_test(self) -> Dict[str, Any]:
        """하드웨어 자가 테스트"""
        return {"pass": True, "message": "Not implemented"}
```

### 5.3 드라이버 상태 다이어그램

```
                    ┌───────────────┐
                    │   CREATED     │
                    │ (constructor) │
                    └───────┬───────┘
                            │
                            │ connect()
                            ▼
              ┌─────────────────────────────┐
              │         CONNECTING          │
              └─────────────┬───────────────┘
                            │
           ┌────────────────┼────────────────┐
           │ success        │                │ failure
           ▼                                 ▼
    ┌──────────────┐                 ┌──────────────┐
    │  CONNECTED   │                 │    ERROR     │
    │              │─────────────────│              │
    │ ready for    │     retry       │ log error    │
    │ operations   │<────────────────│ attempt      │
    └──────┬───────┘                 └──────────────┘
           │
           │ operations (measure, set, etc.)
           │
           │ disconnect() or error
           ▼
    ┌──────────────┐
    │ DISCONNECTED │
    └──────────────┘
```

---

## 6. 시퀀스 실행 흐름

### 6.1 실행 단계

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENCE EXECUTOR                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Initialization Phase                            │  │
│  │                                                                        │  │
│  │  1. Load manifest.yaml                                                 │  │
│  │  2. Validate manifest schema                                           │  │
│  │  3. Load sequence class (entry_point)                                  │  │
│  │  4. Create driver instances                                            │  │
│  │  5. Connect all drivers                                                │  │
│  │  6. Instantiate sequence (inject drivers)                              │  │
│  │  7. Extract step metadata from decorators                              │  │
│  │  8. Sort steps by order                                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Execution Phase                                 │  │
│  │                                                                        │  │
│  │  for each step in sorted_steps:                                        │  │
│  │      │                                                                 │  │
│  │      ├─► Check condition (skip if condition param is False)           │  │
│  │      │                                                                 │  │
│  │      ├─► Emit STEP_START event                                        │  │
│  │      │                                                                 │  │
│  │      ├─► Execute with timeout and retry logic                         │  │
│  │      │   │                                                             │  │
│  │      │   ├─► Success: Store result, emit STEP_COMPLETE                │  │
│  │      │   │                                                             │  │
│  │      │   └─► Failure: Retry or fail based on config                   │  │
│  │      │       │                                                         │  │
│  │      │       └─► If not cleanup step: break execution                 │  │
│  │      │                                                                 │  │
│  │      └─► If stopped flag: break execution                             │  │
│  │                                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Cleanup Phase                                   │  │
│  │                                                                        │  │
│  │  for each cleanup_step:                                                │  │
│  │      Execute (ignore errors)                                           │  │
│  │                                                                        │  │
│  │  Disconnect all drivers                                                │  │
│  │  Emit SEQUENCE_COMPLETE event                                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 에러 처리 흐름

```
Step Execution
      │
      ▼
  ┌───────────────────┐
  │  Execute Step     │
  └─────────┬─────────┘
            │
      ┌─────┴─────┐
      │           │
   Success     Exception
      │           │
      ▼           ▼
  ┌─────────┐ ┌─────────────────────────────────┐
  │ Continue│ │  Exception Type?                 │
  │ to next │ │                                  │
  │ step    │ │  ┌───────────┬──────────┬──────┐│
  └─────────┘ │  │TestFailure│ Timeout  │Other ││
              │  └─────┬─────┴────┬─────┴───┬──┘│
              │        │          │         │   │
              │        ▼          ▼         ▼   │
              │  ┌──────────────────────────────┐│
              │  │ retry < max_retry?           ││
              │  │                              ││
              │  │   Yes → Wait → Retry         ││
              │  │   No  → Record failure       ││
              │  └──────────────────────────────┘│
              └────────────────┬─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ cleanup step?   │
                        │                 │
                        │  No  → Stop     │
                        │  Yes → Continue │
                        └─────────────────┘
```

---

## 7. 예외 정의

### 7.1 예외 계층

| 예외 | 부모 | 용도 |
|------|------|------|
| `SequenceError` | `Exception` | 모든 시퀀스 관련 예외의 베이스 |
| `PackageError` | `SequenceError` | 패키지 구조/검증 오류 |
| `ManifestError` | `PackageError` | Manifest 파싱/검증 오류 |
| `DriverError` | `SequenceError` | 하드웨어 드라이버 오류 |
| `ConnectionError` | `DriverError` | 드라이버 연결 오류 |
| `CommunicationError` | `DriverError` | 드라이버 통신 오류 |
| `ExecutionError` | `SequenceError` | 시퀀스 실행 오류 |
| `TestFailure` | `ExecutionError` | 테스트 Step 검증 실패 |
| `TestSkipped` | `ExecutionError` | 테스트 Step 스킵 |
| `TimeoutError` | `ExecutionError` | Step 실행 타임아웃 |

### 7.2 TestFailure 사용

```python
from station.exceptions import TestFailure

@step(order=2)
async def power_on_test(self) -> Dict[str, Any]:
    current = await self.dmm.measure_dc_current()

    if current > self.current_limit:
        raise TestFailure(
            f"Current exceeded: {current}A > {self.current_limit}A",
            actual=current,
            limit=self.current_limit
        )

    return {"current": current, "pass": True}
```

---

## 8. 통합 포인트

### 8.1 Station Service 통합

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATION SERVICE INTEGRATION                               │
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │  BatchManager   │                                                        │
│  │                 │                                                        │
│  │  - start_batch()│───────────────┐                                        │
│  │  - stop_batch() │               │                                        │
│  └─────────────────┘               ▼                                        │
│                         ┌──────────────────────┐                            │
│                         │    BatchProcess      │                            │
│                         │    (Child Process)   │                            │
│                         │                      │                            │
│                         │  ┌────────────────┐  │                            │
│                         │  │  BatchWorker   │  │                            │
│                         │  │                │  │                            │
│                         │  │  - Loads pkg   │  │                            │
│                         │  │  - Creates exe │  │                            │
│                         │  │  - Runs seq    │  │                            │
│                         │  └───────┬────────┘  │                            │
│                         │          │           │                            │
│                         │          ▼           │                            │
│                         │  ┌────────────────┐  │                            │
│                         │  │SequenceExecutor│  │                            │
│                         │  │                │  │                            │
│                         │  │  ┌──────────┐  │  │                            │
│                         │  │  │ Sequence │  │  │                            │
│                         │  │  │ Instance │  │  │                            │
│                         │  │  │          │  │  │                            │
│                         │  │  │ Drivers  │  │  │                            │
│                         │  │  └──────────┘  │  │                            │
│                         │  └────────────────┘  │                            │
│                         └──────────────────────┘                            │
│                                    │                                        │
│                                    │ ZeroMQ                                 │
│                                    ▼                                        │
│  ┌─────────────────┐     ┌─────────────────┐                               │
│  │   REST API      │     │   WebSocket     │                               │
│  │                 │     │                 │                               │
│  │  GET /batches   │     │  step_start     │                               │
│  │  POST /sequence │     │  step_complete  │                               │
│  └─────────────────┘     └─────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Backend (NeuroHub) 통합

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NEUROHUB BACKEND INTEGRATION                            │
│                                                                             │
│  Station Service                          NeuroHub Backend                   │
│  ┌─────────────────┐                     ┌─────────────────┐                │
│  │                 │                     │                 │                │
│  │  Sync Engine    │ ───── REST ──────>  │  API Endpoints  │                │
│  │                 │                     │                 │                │
│  │  - Results      │  POST /results      │  - Store result │                │
│  │  - Heartbeat    │  POST /heartbeat    │  - Update status│                │
│  │                 │                     │                 │                │
│  └─────────────────┘                     └────────┬────────┘                │
│                                                   │                          │
│                                                   ▼                          │
│                                          ┌─────────────────┐                │
│                                          │   Database      │                │
│                                          │                 │                │
│                                          │  execution_logs │                │
│                                          │  step_results   │                │
│                                          │  process_data   │                │
│                                          └─────────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 검증 규칙

### 9.1 패키지 검증 체크리스트

| 검증 항목 | 설명 |
|-----------|------|
| 필수 파일 존재 | `__init__.py`, `manifest.yaml` |
| `drivers/` 디렉토리 존재 | 드라이버 폴더 필수 |
| Manifest YAML 유효성 | YAML 구문 검사 |
| Manifest 스키마 준수 | Pydantic 검증 통과 |
| 폴더명 = 패키지명 | `manifest.name`과 폴더명 일치 |
| 엔트리 포인트 존재 | `entry_point.module` 파일 존재 |
| 시퀀스 클래스 존재 | `entry_point.class` 클래스 존재 |
| @sequence 데코레이터 | 클래스에 `_sequence_meta` 속성 존재 |
| 드라이버 파일 존재 | `hardware.*.driver` 파일 존재 |
| Step order 고유성 | 중복된 order 값 없음 |
| 최소 1개 Step | @step 데코레이터 메서드 존재 |

### 9.2 에러 코드

| 코드 | 설명 |
|------|------|
| `MISSING_FILE` | 필수 파일 없음 |
| `MISSING_DIR` | 필수 디렉토리 없음 |
| `INVALID_YAML` | YAML 구문 오류 |
| `INVALID_SCHEMA` | 스키마 검증 실패 |
| `NAME_MISMATCH` | 폴더명과 패키지명 불일치 |
| `MISSING_MODULE` | 엔트리 포인트 모듈 없음 |
| `MISSING_CLASS` | 엔트리 포인트 클래스 없음 |
| `MISSING_DECORATOR` | @sequence 데코레이터 없음 |
| `MISSING_DRIVER` | 드라이버 파일 없음 |
| `DUPLICATE_ORDER` | 중복된 Step order |
| `NO_STEPS` | Step이 하나도 없음 |

---

## 10. 빠른 참조

### 10.1 데코레이터 요약

| 데코레이터 | 대상 | 용도 |
|-----------|------|------|
| `@sequence(name, description, version)` | Class | 시퀀스로 표시 |
| `@step(order, timeout, retry, cleanup, condition)` | Async method | 테스트 Step으로 표시 |
| `@parameter(name, display_name, unit, description)` | Method → Property | 파라미터 정의 |

### 10.2 Manifest 필수 필드

```yaml
# 필수
name: string           # 패키지 식별자
version: string        # 시맨틱 버전 (X.Y.Z)
entry_point:
  module: string       # Python 모듈명
  class: string        # 클래스명

# 선택
author: string
description: string
hardware: {}           # 하드웨어 정의
parameters: {}         # UI 편집 가능 파라미터
dependencies: {}       # Python 패키지
```

### 10.3 드라이버 필수 인터페이스

```python
class Driver:
    async def connect(self) -> bool: ...
    async def disconnect(self) -> None: ...
    async def reset(self) -> None: ...
    async def identify(self) -> str: ...  # Optional
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2025-12-30 | 요구사항 명세 분리 (design.md에서 분리) |
