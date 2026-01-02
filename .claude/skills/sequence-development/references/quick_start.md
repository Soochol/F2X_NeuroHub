# Quick Start: 새 시퀀스 만들기

새 테스트 시퀀스를 빠르게 생성하는 단계별 가이드입니다.

## 1. 폴더 구조 생성

```bash
cd /home/dev/code/F2X_NeuroHub/sequences

# 시퀀스 폴더 생성
mkdir -p my_new_test/drivers

# 파일 생성
touch my_new_test/__init__.py
touch my_new_test/sequence.py
touch my_new_test/manifest.yaml
touch my_new_test/drivers/__init__.py
touch my_new_test/drivers/base.py
touch my_new_test/drivers/my_device.py
```

## 2. sequences/__init__.py 등록

```python
# /home/dev/code/F2X_NeuroHub/sequences/__init__.py
__all__ = ["sensor_inspection", "manual_test", "psa_sensor_test", "my_new_test"]
```

## 3. manifest.yaml 작성

```yaml
name: my_new_test
version: "1.0.0"
author: "개발팀"
description: "새 테스트 시퀀스"

modes:
  automatic: true
  manual: true

entry_point:
  module: sequence
  class: MyNewTestSequence

hardware:
  test_device:
    display_name: "테스트 장치"
    driver: my_device
    class: MyDeviceDriver

parameters:
  target_value:
    display_name: "목표값"
    type: float
    default: 10.0

dependencies:
  python: []
```

## 4. drivers/base.py 복사

```bash
cp sequences/sensor_inspection/drivers/base.py sequences/my_new_test/drivers/
```

## 5. 드라이버 구현

`drivers/my_device.py`:
```python
from .base import BaseDriver

class MyDeviceDriver(BaseDriver):
    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> None:
        self._connected = False

    async def reset(self) -> None:
        pass

    async def measure(self) -> float:
        return 10.0
```

`drivers/__init__.py`:
```python
from .my_device import MyDeviceDriver
__all__ = ["MyDeviceDriver"]
```

## 6. sequence.py 작성

```python
from station_service.sequence.decorators import sequence, step, parameter
from .drivers.my_device import MyDeviceDriver

@sequence(name="my_new_test", description="새 테스트", version="1.0.0")
class MyNewTestSequence:
    def __init__(self, hardware=None, parameters=None):
        self.hardware = hardware or {}
        self.parameters = parameters or {}
        self.device = self.hardware.get("test_device")
        self.target_value = self.parameters.get("target_value", 10.0)

    @step(order=1, timeout=30.0)
    async def initialize(self):
        if self.device:
            await self.device.connect()
        return {"step": "initialize", "status": "passed", "data": {}}

    @step(order=2, timeout=60.0)
    async def run_test(self):
        value = await self.device.measure()
        return {"step": "run_test", "status": "passed", "data": {"value": value}}

    @step(order=99, timeout=10.0, cleanup=True)
    async def finalize(self):
        if self.device:
            await self.device.disconnect()
        return {"step": "finalize", "status": "passed", "data": {}}

    @parameter(name="target_value", display_name="목표값", unit="", description="목표값")
    def get_target_value(self):
        return self.target_value
```

`__init__.py`:
```python
from .sequence import MyNewTestSequence
__all__ = ["MyNewTestSequence"]
```

## 7. 검증

```bash
# Python import 테스트
cd /home/dev/code/F2X_NeuroHub
python -c "from sequences.my_new_test import MyNewTestSequence; print('OK')"
```

## 체크리스트

- [ ] 폴더 구조 생성
- [ ] `sequences/__init__.py` 등록
- [ ] `manifest.yaml` 작성
- [ ] `drivers/base.py` 복사
- [ ] 드라이버 구현
- [ ] `sequence.py` 작성 (데코레이터 포함)
- [ ] `__init__.py` 파일들 작성
- [ ] Import 테스트

## 참조 시퀀스

- `sequences/sensor_inspection/` - 전체 기능 구현 예시
- `sequences/psa_sensor_test/` - PSA 센서 테스트
- `sequences/manual_test/` - 수동 테스트
