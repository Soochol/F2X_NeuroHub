# Sequence Decorators Reference (DEPRECATED)

> **DEPRECATED**: 이 데코레이터 방식은 더 이상 권장되지 않습니다.
> 새로운 시퀀스는 SDK 기반 `SequenceBase` 클래스를 사용하세요.
>
> **권장 방식:**
> - [SEQUENCE_DEVELOPMENT_GUIDE.md](/.docs/sequences_dev/SEQUENCE_DEVELOPMENT_GUIDE.md) - SDK 기반 개발 가이드
> - `station_service/sdk/` - SDK 패키지
>
> ```python
> from station_service.sdk import SequenceBase
>
> class MySequence(SequenceBase):
>     name = "my_sequence"
>     version = "1.0.0"
>
>     async def setup(self) -> None: ...
>     async def run(self) -> dict: ...
>     async def teardown(self) -> None: ...
> ```

---

station_service에서 제공하는 시퀀스 데코레이터 상세 레퍼런스입니다.
레거시 시퀀스 유지보수를 위한 참고용입니다.

## Import

```python
# DEPRECATED - 새 시퀀스에서는 사용하지 마세요
from station_service.sequence.decorators import sequence, step, parameter
```

---

## @sequence

클래스 데코레이터. 시퀀스 메타데이터를 정의합니다.

### 사용법

```python
@sequence(
    name="my_sequence",
    description="시퀀스 설명",
    version="1.0.0"
)
class MySequence:
    pass
```

### 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `name` | str | O | 시퀀스 이름 (Python 식별자) |
| `description` | str | O | 시퀀스 설명 |
| `version` | str | O | 버전 (X.Y.Z 형식) |

### 내부 동작

- 클래스에 `_sequence_meta` 속성 추가
- `SequenceMeta(name, description, version)` 데이터클래스 저장
- `SequenceLoader`가 클래스 로드 시 검증

### 예시

```python
@sequence(
    name="psa_sensor_test",
    description="PSA 센서 테스트 (VL53L0X ToF, MLX90640 IR)",
    version="1.0.0"
)
class PSASensorTestSequence:
    """PSA Sensor Test Sequence."""
    pass
```

---

## @step

메서드 데코레이터. 테스트 스텝을 정의합니다.

### 사용법

```python
@step(order=1, timeout=30.0)
async def initialize(self) -> Dict[str, Any]:
    pass

@step(order=2, timeout=60.0, retry=2)
async def run_test(self) -> Dict[str, Any]:
    pass

@step(order=99, timeout=10.0, cleanup=True)
async def finalize(self) -> Dict[str, Any]:
    pass
```

### 파라미터

| 파라미터 | 타입 | 기본값 | 필수 | 설명 |
|----------|------|--------|------|------|
| `order` | int | - | O | 실행 순서 (낮을수록 먼저) |
| `timeout` | float | 60.0 | X | 최대 실행 시간 (초) |
| `retry` | int | 0 | X | 실패 시 재시도 횟수 |
| `cleanup` | bool | False | X | True면 항상 실행 |
| `condition` | str | None | X | 조건부 실행 파라미터명 |

### 내부 동작

- 메서드에 `_step_meta` 속성 추가
- `StepMeta` 데이터클래스 저장:
  ```python
  @dataclass(frozen=True)
  class StepMeta:
      order: int
      timeout: float = 60.0
      retry: int = 0
      cleanup: bool = False
      condition: Optional[str] = None
      name: Optional[str] = None       # 메서드명에서 자동 추출
      description: Optional[str] = None # docstring에서 자동 추출
  ```
- `SequenceExecutor._extract_steps()`가 수집
- `collect_steps(cls)` 헬퍼 함수로 접근 가능

### 실행 순서

1. `order` 값으로 정렬 (낮은 순)
2. 일반 스텝 (`cleanup=False`) 먼저 실행
3. 실패 시 나머지 일반 스텝 중단
4. cleanup 스텝 (`cleanup=True`) 항상 실행

### 재시도 로직

```python
@step(order=2, timeout=30.0, retry=2)
async def run_test(self):
    # 최대 3회 시도 (1회 실행 + 2회 재시도)
    # TimeoutError, Exception 발생 시 재시도
    # TestFailure 예외는 즉시 실패 (재시도 안함)
    pass
```

### 예시

```python
@step(order=1, timeout=30.0)
async def initialize(self) -> Dict[str, Any]:
    """하드웨어 초기화."""
    result = {"step": "initialize", "status": "passed", "data": {}}
    try:
        await self.device.connect()
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    return result

@step(order=99, timeout=10.0, cleanup=True)
async def finalize(self) -> Dict[str, Any]:
    """리소스 정리. 항상 실행됨."""
    if self.device:
        await self.device.disconnect()
    return {"step": "finalize", "status": "passed", "data": {}}
```

---

## @parameter

프로퍼티 데코레이터. 런타임 파라미터를 UI에 노출합니다.

### 사용법

```python
@parameter(
    name="voltage_limit",
    display_name="전압 제한",
    unit="V",
    description="최대 전압 제한값"
)
def get_voltage_limit(self) -> float:
    return self._voltage_limit
```

### 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `name` | str | O | 내부 이름 (manifest와 일치) |
| `display_name` | str | O | UI 표시명 |
| `unit` | str | O | 단위 (빈 문자열 가능) |
| `description` | str | O | 설명 |

### 내부 동작

- `ParameterProperty` 클래스 생성 (Python `property` 상속)
- `_param_meta` 속성에 `ParameterMeta` 저장:
  ```python
  @dataclass(frozen=True)
  class ParameterMeta:
      name: str
      display_name: str
      unit: str
      description: str
      default_getter: Optional[Callable[[], Any]] = None
  ```
- `collect_parameters(cls)` 헬퍼 함수로 접근 가능

### 예시

```python
class MySequence:
    def __init__(self, parameters=None):
        self.target_value = parameters.get("target_value", 10.0)
        self.tolerance = parameters.get("tolerance", 5.0)

    @parameter(
        name="target_value",
        display_name="목표값",
        unit="V",
        description="테스트 목표 전압"
    )
    def get_target_value(self) -> float:
        return self.target_value

    @parameter(
        name="tolerance",
        display_name="허용 오차",
        unit="%",
        description="허용 오차 비율"
    )
    def get_tolerance(self) -> float:
        return self.tolerance
```

---

## Helper Functions

### collect_steps(cls)

클래스에서 모든 `@step` 데코레이터 스텝을 수집합니다.

```python
from station_service.sequence.decorators import collect_steps

steps = collect_steps(MySequence)
# Returns: List[Tuple[str, Callable, StepMeta]]
# [(method_name, method, step_meta), ...]
```

### collect_parameters(cls)

클래스에서 모든 `@parameter` 데코레이터 파라미터를 수집합니다.

```python
from station_service.sequence.decorators import collect_parameters

params = collect_parameters(MySequence)
# Returns: List[Tuple[str, ParameterProperty, ParameterMeta]]
```

### get_sequence_meta(cls)

클래스의 `@sequence` 메타데이터를 가져옵니다.

```python
from station_service.sequence.decorators import get_sequence_meta

meta = get_sequence_meta(MySequence)
# Returns: SequenceMeta(name="...", description="...", version="...")
```

---

## 파일 위치

- 데코레이터 정의: `station_service/sequence/decorators.py`
- 실행기: `station_service/sequence/executor.py`
- 로더: `station_service/sequence/loader.py`
