# 10. Batch 착공/완공 - Backend 통합 가이드

## 구현 체크리스트

> Phase 4 - Backend 통합 ✅ 완료

### 4.1 BackendClient 구현
- [x] `station_service/sync/__init__.py`
- [x] `station_service/sync/backend_client.py` - HTTP 클라이언트
  - [x] `async connect()` / `disconnect()`
  - [x] `async health_check()` - 연결 상태 확인
  - [x] 인증 헤더 (Bearer token)
- [x] `station_service/sync/models.py` - Pydantic 모델

### 4.2 착공 API 연동
- [x] `async start_process(wip_int_id, request)` 구현 (wip_id는 int)
- [x] `ProcessStartRequest` 모델 정의
- [x] 에러 처리: `WIP_NOT_FOUND`, `PREREQUISITE_NOT_MET`
- [x] WIP 조회: `lookup_wip(wip_id_string)` - string → int 변환

### 4.3 완공 API 연동
- [x] `async complete_process(wip_int_id, process_id, operator_id, request)` 구현
- [x] `ProcessCompleteRequest` 모델 정의
- [x] 측정 데이터 변환 (`measurements` 필드)
- [x] 불량 코드 추출 (`defects` 필드)

### 4.4 시리얼 변환 연동
- [x] `async convert_to_serial(wip_int_id, request)` 구현
- [x] `SerialConvertRequest` 모델 정의
- [x] WIP 상태 확인 로직

### 4.5 SyncEngine 확장
- [x] `station_service/sync/engine.py` - 오프라인 동기화
  - [x] WIP 프로세스 동기화 메서드 추가
  - [x] `sync_process_start()`, `sync_process_complete()`, `sync_serial_convert()`
  - [x] 주기적 동기화 루프

### 4.6 예외 및 설정
- [x] `station_service/core/exceptions.py` - Backend 예외 추가
  - [x] `BackendError`, `WIPNotFoundError`, `PrerequisiteNotMetError`
  - [x] `DuplicatePassError`, `InvalidWIPStatusError`, `BackendConnectionError`
- [x] `station_service/models/config.py` - BackendConfig 확장
  - [x] `station_id`, `equipment_id`, `timeout`, `max_retries` 추가

### 4.7 BatchWorker 통합
- [x] `station_service/batch/worker.py` 확장
  - [x] `_init_backend_client()` - Backend 클라이언트 초기화
  - [x] `_lookup_wip()` - WIP 조회 (string → int)
  - [x] 착공 호출 (시퀀스 시작 전)
  - [x] 완공 호출 (시퀀스 완료 후)
  - [x] `_extract_measurements()`, `_extract_defects()` - 데이터 추출
  - [x] 오프라인 모드 폴백

### 4.8 테스트
- [x] `station_service/tests/unit/test_backend_client.py`

---

## Document Information
- **Version**: 1.1.0
- **Date**: 2025-12-30
- **Type**: Integration Specification
- **Implementation Status**: ✅ Complete
- **Related**:
  - [07-station-service-design.md](./07-station-service-design.md) (Station Service 설계)
  - [03-api-specification.md](./03-api-specification.md) (API 명세)

---

## 1. 개요

이 문서는 Station Service에서 Batch 실행 시작/종료 시 Backend와 통신하여 **착공(Start Work)** 및 **완공(Complete Work)**을 처리하는 방법을 정의합니다.

### 1.1 용어 정의

| 용어 | 한국어 | 설명 |
|------|--------|------|
| **착공 (Chak-gong)** | Start Work | Batch 실행 시작 - 생산 공정 시작을 Backend에 알림 |
| **완공 (Wan-gong)** | Complete Work | Batch 실행 종료 - 공정 결과를 Backend에 전송 |
| **WIP** | Work In Progress | 생산 중인 개별 단위 (시리얼 부여 전) |
| **Process** | 공정 | 제조 과정의 각 단계 (1-6번 공정) |

### 1.2 전체 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Batch 생명주기와 Backend 연동                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   [Station Service]                              [Backend (NeuroHub)]        │
│                                                                              │
│   1. Batch 시작 (사용자 트리거)                                              │
│      │                                                                       │
│      ├──── POST /api/v1/wip-items/{wip_id}/start-process ────────────────►  │
│      │     {                                                                 │
│      │       "process_id": 1,                     착공 (Start Work)          │
│      │       "operator_id": 5,                    공정 시작 기록              │
│      │       "equipment_id": 3,                                              │
│      │       "started_at": "2025-12-30T10:00:00Z"                           │
│      │     }                                                                 │
│      │                                                                       │
│   2. 시퀀스 실행 (측정/테스트)                                               │
│      │                                                                       │
│   3. Batch 종료 (시퀀스 완료)                                                │
│      │                                                                       │
│      ├──── POST /api/v1/wip-items/{wip_id}/complete-process ────────────►   │
│      │     {                                                                 │
│      │       "result": "PASS",                    완공 (Complete Work)       │
│      │       "measurements": {...},               공정 결과 기록              │
│      │       "defects": [],                                                  │
│      │       "completed_at": "2025-12-30T10:30:00Z"                         │
│      │     }                                                                 │
│      │                                                                       │
│   4. [모든 공정 완료 시]                                                     │
│      │                                                                       │
│      └──── POST /api/v1/wip-items/{wip_id}/convert-to-serial ───────────►   │
│            {                                                                 │
│              "operator_id": 5,                    최종 완공                   │
│              "notes": "..."                       시리얼 번호 부여            │
│            }                                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend API 상세

### 2.1 착공 - 공정 시작 (Start Process)

Batch 시퀀스 실행이 시작될 때 호출합니다.

#### Endpoint
```
POST /api/v1/wip-items/{wip_id}/start-process
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `wip_id` | **int** | WIP 정수 ID (DB primary key) |

> **Note**: Backend API는 정수 `wip_id`를 사용합니다. Station Service에서는 QR 스캔으로 받은 문자열 WIP ID(예: `WIP-KR01PSA2511-001`)를 먼저 `/api/v1/wip-items/{wip_id_string}/scan` API로 조회하여 정수 ID를 얻습니다.

#### Request Body
```json
{
  "process_id": 1,
  "operator_id": 5,
  "equipment_id": 3,
  "started_at": "2025-12-30T10:00:00Z"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `process_id` | integer | Y | 공정 번호 (1-6) |
| `operator_id` | integer | Y | 작업자 ID |
| `equipment_id` | integer | N | 장비 ID (옵션) |
| `started_at` | datetime | N | 시작 시간 (미지정 시 현재 시간) |

#### Response (200 OK)
```json
{
  "wip_item": {
    "id": 1,
    "wip_id": "WIP-KR01PSA2511-001",
    "status": "IN_PROGRESS",
    "current_process_id": 1,
    "updated_at": "2025-12-30T10:00:00Z"
  },
  "message": "Process started successfully"
}
```

#### Business Rules
- **BR-003**:
  - 공정 1은 WIP 상태가 `CREATED` 또는 `IN_PROGRESS`일 때 시작 가능
  - 공정 2-6은 이전 공정이 `PASS` 결과여야 시작 가능
- WIP 상태가 `FAILED` 또는 `CONVERTED`이면 시작 불가

#### Error Responses
```json
// 404 Not Found - WIP를 찾을 수 없음
{
  "error": "WIP_NOT_FOUND",
  "message": "WIP 'WIP-KR01PSA2511-999' not found"
}

// 400 Bad Request - 이전 공정 미완료
{
  "error": "PREREQUISITE_NOT_MET",
  "message": "Process 1 must have PASS result before starting Process 2 (BR-003)"
}

// 400 Bad Request - 잘못된 WIP 상태
{
  "error": "INVALID_WIP_STATUS",
  "message": "Cannot start process on WIP with status 'FAILED'"
}
```

---

### 2.2 완공 - 공정 완료 (Complete Process)

Batch 시퀀스 실행이 종료될 때 결과와 함께 호출합니다.

#### Endpoint
```
POST /api/v1/wip-items/{wip_id}/complete-process
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `wip_id` | string | WIP ID |

#### Request Body
```json
{
  "result": "PASS",
  "measurements": {
    "temperature": 98.5,
    "pressure": 2.1,
    "humidity": 45.2,
    "cycle_time_ms": 15000,
    "busbar_lot": "LOT-2024-001",
    "component_lots": {
      "spring_assembly": "SA-2024-0450"
    }
  },
  "defects": [],
  "notes": "All quality criteria met",
  "completed_at": "2025-12-30T10:30:00Z"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `result` | string | Y | 결과: `PASS`, `FAIL`, `REWORK` |
| `measurements` | object | N | 측정 데이터 (JSON) |
| `defects` | array | N | 불량 코드 목록 |
| `notes` | string | N | 작업자 메모 |
| `completed_at` | datetime | N | 완료 시간 (미지정 시 현재 시간) |

#### Measurements 필드 상세

Station에서 측정한 데이터를 `measurements` 객체에 포함합니다:

```json
{
  "measurements": {
    // 환경 데이터
    "temperature": 98.5,        // 온도 (섭씨)
    "pressure": 2.1,            // 압력 (bar)
    "humidity": 45.2,           // 습도 (%)

    // 타이밍 데이터
    "cycle_time_ms": 15000,     // 사이클 타임 (밀리초)
    "process_time_ms": 12000,   // 실제 처리 시간

    // 부품 추적
    "busbar_lot": "LOT-2024-001",
    "component_lots": {
      "spring_assembly": "SA-2024-0450",
      "connector": "CN-2024-1234"
    },

    // 측정값 (공정별로 다름)
    "resistance_ohm": 0.005,
    "voltage_v": 3.7,
    "torque_nm": 1.5,

    // 테스트 결과
    "test_results": {
      "visual_check": "PASS",
      "electrical_test": "PASS",
      "mechanical_test": "PASS"
    }
  }
}
```

#### Defects 필드 상세

불량 발생 시 불량 코드 목록을 포함합니다:

```json
{
  "result": "FAIL",
  "defects": [
    "DEF001",  // 외관 불량
    "DEF003"   // 치수 불량
  ],
  "notes": "Visual inspection failed - scratch on surface"
}
```

#### Response (200 OK)
```json
{
  "process_history": {
    "id": 1,
    "wip_item_id": 1,
    "process_id": 1,
    "result": "PASS",
    "started_at": "2025-12-30T10:00:00Z",
    "completed_at": "2025-12-30T10:30:00Z",
    "duration_seconds": 1800
  },
  "wip_item": {
    "id": 1,
    "wip_id": "WIP-KR01PSA2511-001",
    "status": "IN_PROGRESS",
    "current_process_id": null,
    "updated_at": "2025-12-30T10:30:00Z"
  }
}
```

#### WIP 상태 전이

| 결과 | 상태 변화 | 설명 |
|------|----------|------|
| `PASS` (공정 1-5) | `IN_PROGRESS` 유지 | 다음 공정 진행 가능 |
| `PASS` (공정 6) | → `COMPLETED` | 모든 공정 완료, 시리얼 변환 가능 |
| `FAIL` | → `FAILED` | 생산 중단, 불량품 처리 |
| `REWORK` | `IN_PROGRESS` 유지 | 재작업 후 동일 공정 재시도 |

#### Business Rules
- **BR-004**: 동일 공정에 대해 `PASS` 결과가 이미 있으면 중복 `PASS` 불가
- `FAIL` 결과는 중복 기록 가능 (재작업 이력 추적용)

#### Error Responses
```json
// 400 Bad Request - 중복 PASS
{
  "error": "DUPLICATE_PASS",
  "message": "Duplicate PASS results are not allowed for process 1 (BR-004)"
}

// 400 Bad Request - 공정 시작 안 함
{
  "error": "PROCESS_NOT_STARTED",
  "message": "Process must be started before completion"
}
```

---

### 2.3 최종 완공 - 시리얼 변환 (Convert to Serial)

모든 공정이 완료된 WIP를 최종 시리얼 번호로 변환합니다.

#### Endpoint
```
POST /api/v1/wip-items/{wip_id}/convert-to-serial
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `wip_id` | string | WIP ID |

#### Request Body
```json
{
  "operator_id": 5,
  "notes": "Final inspection passed, ready for shipment"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `operator_id` | integer | Y | 작업자 ID |
| `notes` | string | N | 최종 검사 메모 |

#### Response (201 Created)
```json
{
  "serial": {
    "id": 1,
    "serial_number": "SN-KR01PSA2511-001",
    "lot_id": 10,
    "status": "CREATED",
    "created_at": "2025-12-30T11:00:00Z"
  },
  "wip_item": {
    "id": 1,
    "wip_id": "WIP-KR01PSA2511-001",
    "status": "CONVERTED",
    "serial_id": 1,
    "converted_at": "2025-12-30T11:00:00Z"
  }
}
```

#### Business Rules
- **BR-005**: 모든 제조 공정(1-6)이 `PASS` 결과여야 변환 가능
- WIP 상태가 `COMPLETED`여야 변환 가능
- 이미 `CONVERTED` 상태이면 중복 변환 불가

#### Error Responses
```json
// 400 Bad Request - 공정 미완료
{
  "error": "INCOMPLETE_PROCESSES",
  "message": "Missing PASS results for processes: [3, 5, 6] (BR-005)"
}

// 400 Bad Request - 잘못된 상태
{
  "error": "INVALID_WIP_STATUS",
  "message": "WIP must be in COMPLETED status for serial conversion"
}

// 400 Bad Request - 이미 변환됨
{
  "error": "ALREADY_CONVERTED",
  "message": "WIP has already been converted to serial"
}
```

---

## 3. Station Service 구현

### 3.1 Backend Client 모듈

```python
# sync/backend_client.py

import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from core.config import BackendConfig
from core.exceptions import BackendError

class ProcessStartRequest(BaseModel):
    process_id: int
    operator_id: int
    equipment_id: Optional[int] = None
    started_at: Optional[datetime] = None

class ProcessCompleteRequest(BaseModel):
    result: str  # PASS, FAIL, REWORK
    measurements: Dict[str, Any] = {}
    defects: list = []
    notes: str = ""
    completed_at: Optional[datetime] = None

class SerialConvertRequest(BaseModel):
    operator_id: int
    notes: str = ""

class BackendClient:
    """Backend API 클라이언트"""

    def __init__(self, config: BackendConfig):
        self.base_url = config.url.rstrip('/')
        self.api_key = config.api_key
        self.timeout = config.timeout or 30.0
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

    async def connect(self):
        """HTTP 클라이언트 초기화"""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )

    async def disconnect(self):
        """HTTP 클라이언트 종료"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def start_process(
        self,
        wip_id: str,
        request: ProcessStartRequest
    ) -> Dict[str, Any]:
        """
        착공 - 공정 시작

        Args:
            wip_id: WIP ID (예: WIP-KR01PSA2511-001)
            request: 공정 시작 요청 데이터

        Returns:
            Backend 응답 (wip_item, message)

        Raises:
            BackendError: Backend 통신 실패 시
        """
        url = f"/api/v1/wip-items/{wip_id}/start-process"

        payload = request.model_dump(exclude_none=True)
        if request.started_at:
            payload["started_at"] = request.started_at.isoformat()

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendError(
                f"Failed to start process: {e.response.status_code}",
                response=e.response.json() if e.response.content else None
            )
        except httpx.RequestError as e:
            raise BackendError(f"Backend connection error: {str(e)}")

    async def complete_process(
        self,
        wip_id: str,
        request: ProcessCompleteRequest
    ) -> Dict[str, Any]:
        """
        완공 - 공정 완료

        Args:
            wip_id: WIP ID
            request: 공정 완료 요청 데이터 (결과, 측정값, 불량 등)

        Returns:
            Backend 응답 (process_history, wip_item)

        Raises:
            BackendError: Backend 통신 실패 시
        """
        url = f"/api/v1/wip-items/{wip_id}/complete-process"

        payload = request.model_dump(exclude_none=True)
        if request.completed_at:
            payload["completed_at"] = request.completed_at.isoformat()

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendError(
                f"Failed to complete process: {e.response.status_code}",
                response=e.response.json() if e.response.content else None
            )
        except httpx.RequestError as e:
            raise BackendError(f"Backend connection error: {str(e)}")

    async def convert_to_serial(
        self,
        wip_id: str,
        request: SerialConvertRequest
    ) -> Dict[str, Any]:
        """
        최종 완공 - 시리얼 변환

        Args:
            wip_id: WIP ID
            request: 시리얼 변환 요청 데이터

        Returns:
            Backend 응답 (serial, wip_item)

        Raises:
            BackendError: Backend 통신 실패 시
        """
        url = f"/api/v1/wip-items/{wip_id}/convert-to-serial"

        payload = request.model_dump(exclude_none=True)

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise BackendError(
                f"Failed to convert to serial: {e.response.status_code}",
                response=e.response.json() if e.response.content else None
            )
        except httpx.RequestError as e:
            raise BackendError(f"Backend connection error: {str(e)}")

    async def health_check(self) -> bool:
        """Backend 연결 상태 확인"""
        try:
            response = await self._client.get("/api/health")
            return response.status_code == 200
        except Exception:
            return False
```

### 3.2 Batch Worker 통합

```python
# batch/worker.py (확장)

from sync.backend_client import (
    BackendClient,
    ProcessStartRequest,
    ProcessCompleteRequest,
    SerialConvertRequest
)
from datetime import datetime

class BatchWorker:
    """Batch 워커 - Backend 착공/완공 통합"""

    def __init__(self, batch_id: str, config: dict, ipc_address: str):
        self.batch_id = batch_id
        self.config = config
        self.ipc = IPCClient(ipc_address)
        self.loader = SequenceLoader()
        self.executor: SequenceExecutor = None
        self._running = True

        # Backend 클라이언트
        self.backend = BackendClient(config.get('backend', {}))

        # 현재 작업 컨텍스트
        self._current_wip_id: str = None
        self._current_process_id: int = None
        self._current_operator_id: int = None
        self._process_start_time: datetime = None

    async def run(self):
        """메인 루프"""
        await self.ipc.connect()
        await self.backend.connect()

        # ... 기존 초기화 코드 ...

        while self._running:
            command = await self.ipc.receive_command()
            await self._handle_command(command)

    async def _run_sequence(self, params: dict):
        """
        시퀀스 실행 - 착공/완공 포함

        params 예시:
        {
            "wip_id": "WIP-KR01PSA2511-001",
            "process_id": 1,
            "operator_id": 5,
            "equipment_id": 3
        }
        """
        wip_id = params.get('wip_id')
        process_id = params.get('process_id')
        operator_id = params.get('operator_id')
        equipment_id = params.get('equipment_id')

        if not wip_id or not process_id or not operator_id:
            await self.ipc.publish("SEQUENCE_ERROR", {
                "error": "Missing required parameters: wip_id, process_id, operator_id"
            })
            return

        self._current_wip_id = wip_id
        self._current_process_id = process_id
        self._current_operator_id = operator_id

        try:
            # ═══════════════════════════════════════════
            # 1. 착공 (Start Work) - Backend에 공정 시작 알림
            # ═══════════════════════════════════════════
            self._process_start_time = datetime.utcnow()

            start_request = ProcessStartRequest(
                process_id=process_id,
                operator_id=operator_id,
                equipment_id=equipment_id,
                started_at=self._process_start_time
            )

            try:
                start_response = await self.backend.start_process(wip_id, start_request)
                await self.ipc.publish("PROCESS_STARTED", {
                    "wip_id": wip_id,
                    "process_id": process_id,
                    "backend_response": start_response
                })
            except BackendError as e:
                # 오프라인 모드 - 나중에 동기화
                await self._queue_for_sync("start_process", {
                    "wip_id": wip_id,
                    "request": start_request.model_dump()
                })
                await self.ipc.publish("PROCESS_STARTED_OFFLINE", {
                    "wip_id": wip_id,
                    "process_id": process_id,
                    "error": str(e)
                })

            # ═══════════════════════════════════════════
            # 2. 시퀀스 실행 (측정/테스트)
            # ═══════════════════════════════════════════
            self.executor.set_parameters(params)

            result = await self.executor.run(
                on_step_start=self._on_step_start,
                on_step_complete=self._on_step_complete,
                on_log=self._on_log
            )

            # ═══════════════════════════════════════════
            # 3. 완공 (Complete Work) - Backend에 결과 전송
            # ═══════════════════════════════════════════
            process_result = self._determine_result(result)
            measurements = self._extract_measurements(result)
            defects = self._extract_defects(result)

            complete_request = ProcessCompleteRequest(
                result=process_result,
                measurements=measurements,
                defects=defects,
                notes=result.get('notes', ''),
                completed_at=datetime.utcnow()
            )

            try:
                complete_response = await self.backend.complete_process(
                    wip_id, complete_request
                )

                # WIP가 COMPLETED 상태가 되었으면 시리얼 변환 가능 알림
                wip_status = complete_response.get('wip_item', {}).get('status')

                await self.ipc.publish("SEQUENCE_COMPLETE", {
                    "wip_id": wip_id,
                    "process_id": process_id,
                    "result": process_result,
                    "wip_status": wip_status,
                    "can_convert": wip_status == "COMPLETED",
                    "backend_response": complete_response
                })

            except BackendError as e:
                # 오프라인 모드 - 나중에 동기화
                await self._queue_for_sync("complete_process", {
                    "wip_id": wip_id,
                    "request": complete_request.model_dump()
                })
                await self.ipc.publish("SEQUENCE_COMPLETE_OFFLINE", {
                    "wip_id": wip_id,
                    "process_id": process_id,
                    "result": process_result,
                    "error": str(e)
                })

        except Exception as e:
            # 시퀀스 실행 중 에러
            await self._handle_sequence_error(e)

    async def convert_wip_to_serial(self, wip_id: str, operator_id: int, notes: str = ""):
        """
        최종 완공 - 시리얼 변환
        모든 공정 완료 후 호출
        """
        request = SerialConvertRequest(
            operator_id=operator_id,
            notes=notes
        )

        try:
            response = await self.backend.convert_to_serial(wip_id, request)

            await self.ipc.publish("SERIAL_CREATED", {
                "wip_id": wip_id,
                "serial": response.get('serial'),
                "backend_response": response
            })

            return response

        except BackendError as e:
            await self._queue_for_sync("convert_to_serial", {
                "wip_id": wip_id,
                "request": request.model_dump()
            })

            await self.ipc.publish("SERIAL_CREATED_OFFLINE", {
                "wip_id": wip_id,
                "error": str(e)
            })

            raise

    def _determine_result(self, execution_result: dict) -> str:
        """시퀀스 실행 결과를 PASS/FAIL/REWORK로 변환"""
        status = execution_result.get('status', 'failed')

        if status == 'completed' and execution_result.get('passed', False):
            return "PASS"
        elif execution_result.get('rework_requested', False):
            return "REWORK"
        else:
            return "FAIL"

    def _extract_measurements(self, execution_result: dict) -> dict:
        """시퀀스 실행 결과에서 측정값 추출"""
        measurements = {}

        # Step별 결과에서 측정값 수집
        for step in execution_result.get('steps', []):
            step_measurements = step.get('measurements', {})
            measurements.update(step_measurements)

        # 전체 실행 메타데이터 추가
        measurements['cycle_time_ms'] = execution_result.get('duration_ms', 0)

        return measurements

    def _extract_defects(self, execution_result: dict) -> list:
        """시퀀스 실행 결과에서 불량 코드 추출"""
        defects = []

        for step in execution_result.get('steps', []):
            step_defects = step.get('defects', [])
            defects.extend(step_defects)

        return list(set(defects))  # 중복 제거

    async def _queue_for_sync(self, action: str, data: dict):
        """오프라인 동기화 큐에 추가"""
        # SQLite sync_queue에 저장
        await self.database.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, action, payload)
            VALUES (?, ?, ?, ?)
            """,
            ("wip_process", data.get('wip_id'), action, json.dumps(data))
        )

    async def _cleanup(self):
        """정리"""
        if self.executor:
            await self.executor.cleanup()
        await self.backend.disconnect()
        await self.ipc.disconnect()
```

---

## 4. 데이터 흐름

### 4.1 착공 데이터 흐름

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              착공 데이터 흐름                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   [Tablet Scanner]          [Station Service]              [Backend]          │
│         │                         │                            │              │
│   1. WIP 스캔                     │                            │              │
│   QR: WIP-KR01PSA2511-001        │                            │              │
│         │                         │                            │              │
│         ├── POST /batch/start ───►│                            │              │
│         │   {                     │                            │              │
│         │     wip_id: "...",      │                            │              │
│         │     process_id: 1,      │                            │              │
│         │     operator_id: 5      │                            │              │
│         │   }                     │                            │              │
│         │                         │                            │              │
│         │                         ├── POST /wip-items/.../     │              │
│         │                         │   start-process ──────────►│              │
│         │                         │                            │              │
│         │                         │◄───── 200 OK ──────────────┤              │
│         │                         │   {                        │              │
│         │                         │     wip_item: {...},       │              │
│         │                         │     message: "..."         │              │
│         │                         │   }                        │              │
│         │                         │                            │              │
│         │◄─── 200 OK ─────────────┤                            │              │
│         │   { status: "started" } │                            │              │
│         │                         │                            │              │
│   2. UI 업데이트                  │                            │              │
│   "공정 시작됨"                   │                            │              │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 완공 데이터 흐름

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              완공 데이터 흐름                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   [Station Service]                                         [Backend]         │
│         │                                                       │             │
│   1. 시퀀스 실행 완료                                           │             │
│      result = {                                                 │             │
│        status: "completed",                                     │             │
│        passed: true,                                            │             │
│        steps: [...],                                            │             │
│        measurements: {...}                                      │             │
│      }                                                          │             │
│         │                                                       │             │
│   2. 결과 변환                                                  │             │
│      ProcessCompleteRequest {                                   │             │
│        result: "PASS",                                          │             │
│        measurements: {                                          │             │
│          temperature: 98.5,                                     │             │
│          cycle_time_ms: 15000                                   │             │
│        },                                                       │             │
│        defects: []                                              │             │
│      }                                                          │             │
│         │                                                       │             │
│         ├── POST /wip-items/.../complete-process ──────────────►│             │
│         │                                                       │             │
│         │◄────────────────── 200 OK ────────────────────────────┤             │
│         │   {                                                   │             │
│         │     process_history: {                                │             │
│         │       id: 1,                                          │             │
│         │       result: "PASS",                                 │             │
│         │       duration_seconds: 1800                          │             │
│         │     },                                                │             │
│         │     wip_item: {                                       │             │
│         │       status: "IN_PROGRESS" | "COMPLETED"             │             │
│         │     }                                                 │             │
│         │   }                                                   │             │
│         │                                                       │             │
│   3. [모든 공정 완료 시]                                        │             │
│         │                                                       │             │
│         ├── POST /wip-items/.../convert-to-serial ─────────────►│             │
│         │                                                       │             │
│         │◄────────────────── 201 Created ───────────────────────┤             │
│         │   {                                                   │             │
│         │     serial: {                                         │             │
│         │       serial_number: "SN-KR01PSA2511-001"             │             │
│         │     }                                                 │             │
│         │   }                                                   │             │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 오프라인 처리

### 5.1 오프라인 큐 스키마

```sql
-- 오프라인 동기화 큐
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,     -- 'wip_process'
    entity_id TEXT NOT NULL,       -- WIP ID
    action TEXT NOT NULL,          -- 'start_process', 'complete_process', 'convert_to_serial'
    payload JSON NOT NULL,         -- 요청 데이터
    retry_count INTEGER DEFAULT 0, -- 재시도 횟수
    last_error TEXT,               -- 마지막 에러 메시지
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    synced_at DATETIME             -- 동기화 완료 시간
);

CREATE INDEX idx_sync_queue_pending ON sync_queue(synced_at) WHERE synced_at IS NULL;
```

### 5.2 동기화 엔진

```python
# sync/engine.py

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from storage.database import Database
from .backend_client import (
    BackendClient,
    ProcessStartRequest,
    ProcessCompleteRequest,
    SerialConvertRequest
)

class SyncEngine:
    """오프라인 동기화 엔진"""

    def __init__(self, backend_config: dict, database: Database):
        self.backend = BackendClient(backend_config)
        self.database = database
        self._running = False
        self._sync_task: asyncio.Task = None
        self.sync_interval = backend_config.get('sync_interval', 30)
        self.max_retries = backend_config.get('max_retries', 5)

    async def start(self):
        """동기화 엔진 시작"""
        self._running = True
        await self.backend.connect()
        self._sync_task = asyncio.create_task(self._sync_loop())

    async def stop(self):
        """동기화 엔진 중지"""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        await self.backend.disconnect()

    async def _sync_loop(self):
        """동기화 루프"""
        while self._running:
            try:
                await self._process_pending_items()
            except Exception as e:
                # 에러 로깅
                pass

            await asyncio.sleep(self.sync_interval)

    async def _process_pending_items(self):
        """대기 중인 항목 처리"""
        # 대기 중인 항목 조회 (오래된 것부터)
        items = await self.database.fetch_all(
            """
            SELECT id, entity_type, entity_id, action, payload, retry_count
            FROM sync_queue
            WHERE synced_at IS NULL AND retry_count < ?
            ORDER BY created_at ASC
            LIMIT 100
            """,
            (self.max_retries,)
        )

        for item in items:
            await self._sync_item(item)

    async def _sync_item(self, item: Dict[str, Any]):
        """개별 항목 동기화"""
        item_id = item['id']
        action = item['action']
        payload = json.loads(item['payload'])
        wip_id = item['entity_id']

        try:
            if action == 'start_process':
                request = ProcessStartRequest(**payload['request'])
                await self.backend.start_process(wip_id, request)

            elif action == 'complete_process':
                request = ProcessCompleteRequest(**payload['request'])
                await self.backend.complete_process(wip_id, request)

            elif action == 'convert_to_serial':
                request = SerialConvertRequest(**payload['request'])
                await self.backend.convert_to_serial(wip_id, request)

            # 성공 - 동기화 완료 표시
            await self.database.execute(
                """
                UPDATE sync_queue
                SET synced_at = ?
                WHERE id = ?
                """,
                (datetime.utcnow().isoformat(), item_id)
            )

        except Exception as e:
            # 실패 - 재시도 횟수 증가
            await self.database.execute(
                """
                UPDATE sync_queue
                SET retry_count = retry_count + 1,
                    last_error = ?
                WHERE id = ?
                """,
                (str(e), item_id)
            )
```

---

## 6. 에러 처리

### 6.1 에러 코드 매핑

| Backend 에러 | Station 처리 | 사용자 메시지 |
|-------------|-------------|--------------|
| `WIP_NOT_FOUND` | 시퀀스 중단, 알림 | "WIP를 찾을 수 없습니다" |
| `PREREQUISITE_NOT_MET` | 시퀀스 중단, 이전 공정 확인 필요 | "이전 공정을 먼저 완료하세요" |
| `DUPLICATE_PASS` | 경고, 이미 완료된 공정 | "이미 완료된 공정입니다" |
| `NETWORK_ERROR` | 오프라인 모드, 큐에 저장 | "오프라인 모드로 전환됨" |
| `TIMEOUT` | 재시도 후 오프라인 모드 | "서버 응답 지연" |

### 6.2 예외 클래스

```python
# core/exceptions.py

class BackendError(StationError):
    """Backend 통신 예외"""
    def __init__(self, message: str, response: dict = None):
        super().__init__(message)
        self.response = response
        self.error_code = response.get('error') if response else None

class WIPNotFoundError(BackendError):
    """WIP를 찾을 수 없음"""
    pass

class PrerequisiteNotMetError(BackendError):
    """선행 조건 미충족"""
    pass

class DuplicatePassError(BackendError):
    """중복 PASS"""
    pass
```

---

## 7. 보안 고려사항

### 7.1 인증

```python
# Backend 인증
class BackendClient:
    def __init__(self, config: BackendConfig):
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "X-Station-ID": config.station_id,
            "X-Equipment-ID": config.equipment_id
        }
```

### 7.2 데이터 검증

```python
# WIP ID 형식 검증
import re

WIP_ID_PATTERN = re.compile(r'^WIP-[A-Z0-9]{11}-[0-9]{3}$')

def validate_wip_id(wip_id: str) -> bool:
    return WIP_ID_PATTERN.match(wip_id) is not None
```

---

## 8. 테스트 가이드

### 8.1 단위 테스트

```python
# tests/unit/test_backend_client.py

import pytest
from httpx import Response
from unittest.mock import AsyncMock, patch
from sync.backend_client import BackendClient, ProcessStartRequest

@pytest.fixture
def backend_client():
    config = {"url": "http://test.local", "api_key": "test-key"}
    return BackendClient(config)

@pytest.mark.asyncio
async def test_start_process_success(backend_client):
    mock_response = {
        "wip_item": {"id": 1, "status": "IN_PROGRESS"},
        "message": "Process started"
    }

    with patch.object(
        backend_client._client, 'post',
        return_value=AsyncMock(json=lambda: mock_response, raise_for_status=lambda: None)
    ):
        request = ProcessStartRequest(process_id=1, operator_id=5)
        result = await backend_client.start_process("WIP-KR01PSA2511-001", request)

        assert result["wip_item"]["status"] == "IN_PROGRESS"

@pytest.mark.asyncio
async def test_start_process_wip_not_found(backend_client):
    error_response = {"error": "WIP_NOT_FOUND", "message": "WIP not found"}

    with patch.object(
        backend_client._client, 'post',
        side_effect=httpx.HTTPStatusError("404", request=None, response=Response(404, json=error_response))
    ):
        with pytest.raises(BackendError) as exc_info:
            request = ProcessStartRequest(process_id=1, operator_id=5)
            await backend_client.start_process("WIP-KR01PSA2511-999", request)

        assert exc_info.value.error_code == "WIP_NOT_FOUND"
```

### 8.2 통합 테스트

```python
# tests/integration/test_batch_lifecycle.py

import pytest
from batch.worker import BatchWorker

@pytest.mark.asyncio
async def test_full_batch_lifecycle(mock_backend):
    """전체 Batch 생명주기 테스트"""
    worker = BatchWorker("batch_1", test_config, "ipc://test")

    # 1. 착공
    await worker._run_sequence({
        "wip_id": "WIP-KR01PSA2511-001",
        "process_id": 1,
        "operator_id": 5
    })

    # 착공 API 호출 확인
    mock_backend.start_process.assert_called_once()

    # 완공 API 호출 확인
    mock_backend.complete_process.assert_called_once()

    # 결과 확인
    call_args = mock_backend.complete_process.call_args
    assert call_args[1]['request'].result == "PASS"
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2025-12-30 | 초기 문서 작성 |
