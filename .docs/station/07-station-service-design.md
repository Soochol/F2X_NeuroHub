# 07. Station Service 상세 설계

## 구현 체크리스트

> Phase 3.2 ~ 3.5 - Station Service 핵심 구현

### 3.2 BatchManager 구현
- [x] `station_service/batch/__init__.py`
- [x] `station_service/batch/manager.py` - BatchManager 클래스
  - [x] `start_batch()` - 프로세스 시작
  - [x] `stop_batch()` - 프로세스 종료
  - [x] `get_batch_status()` - 상태 조회
- [x] `station_service/batch/process.py` - Batch 프로세스 래퍼
- [x] `station_service/batch/worker.py` - Batch 워커 (자식 프로세스)
  - [x] 시퀀스 로딩/실행
  - [x] IPC 통신 처리

### 3.3 IPC 통신 구현
- [x] `station_service/ipc/__init__.py`
- [x] `station_service/ipc/server.py` - Master 측 IPC
  - [x] ZeroMQ ROUTER 소켓 (커맨드 응답)
  - [x] ZeroMQ SUB 소켓 (이벤트 수신)
- [x] `station_service/ipc/client.py` - Worker 측 IPC
  - [x] ZeroMQ DEALER 소켓 (커맨드 수신)
  - [x] ZeroMQ PUB 소켓 (이벤트 발행)
- [x] `station_service/ipc/messages.py` - IPC 메시지 정의

### 3.4 FastAPI 서버 구현
- [x] `station_service/main.py` - FastAPI 앱 설정
- [x] REST API 라우터 통합 (03-api-specification 참조)
- [x] WebSocket 핸들러 구현
- [x] CORS, 미들웨어 설정
- [x] Static 파일 서빙 (UI)

### 3.5 LocalDB 구현
- [x] `station_service/storage/__init__.py`
- [x] `station_service/storage/database.py` - SQLite 래퍼
  - [x] `async execute()`, `fetch_one()`, `fetch_all()`
  - [x] 연결 풀링
- [x] `station_service/storage/repositories/` - 리포지토리 패턴
  - [x] `execution_repository.py` - 실행 결과
  - [x] `log_repository.py` - 로그
  - [x] `sync_repository.py` - 동기화 큐

### 3.6 Sync Engine 구현
- [x] `station_service/sync/__init__.py`
- [x] `station_service/sync/engine.py` - Backend 동기화 엔진

### 3.7 Core Utilities
- [x] `station_service/core/__init__.py`
- [x] `station_service/core/exceptions.py` - 예외 정의
- [x] `station_service/core/events.py` - 이벤트 시스템

---

## Document Information
- **Version**: 1.1.0
- **Date**: 2025-12-30
- **Type**: Design Specification
- **Related**: [06-station-service-spec.md](./06-station-service-spec.md) (요구사항 명세)

---

## 1. 개요

이 문서는 Station Service의 상세 설계를 다룹니다. 요구사항 및 API 명세는 [02-station-service-spec.md](./02-station-service-spec.md)를 참조하세요.

### 1.1 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Station Service (Master Process)                         │
│                                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │   FastAPI     │  │   WebSocket   │  │    Batch      │  │    Sync      │ │
│  │   REST API    │  │   Server      │  │   Manager     │  │   Engine     │ │
│  │               │  │               │  │               │  │              │ │
│  │  /api/batches │  │  Real-time    │  │  Lifecycle    │  │  Backend     │ │
│  │  /api/results │  │  Updates      │  │  Management   │  │  Sync        │ │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └──────┬───────┘ │
│          │                  │                  │                  │         │
│          └──────────────────┴────────┬─────────┴──────────────────┘         │
│                                      │                                       │
│  ┌───────────────────────────────────┴───────────────────────────────────┐  │
│  │                         ZeroMQ IPC Layer                               │  │
│  │                    REQ/REP (Commands) + PUB/SUB (Events)               │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           ▼                           ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │    Batch 1      │         │    Batch 2      │         │    Batch N      │
    │   (Process)     │         │   (Process)     │         │   (Process)     │
    │                 │         │                 │         │                 │
    │  ┌───────────┐  │         │  ┌───────────┐  │         │  ┌───────────┐  │
    │  │ Sequence  │  │         │  │ Sequence  │  │         │  │ Sequence  │  │
    │  │ Executor  │  │         │  │ Executor  │  │         │  │ Executor  │  │
    │  │           │  │         │  │           │  │         │  │           │  │
    │  │ ┌───────┐ │  │         │  │ ┌───────┐ │  │         │  │ ┌───────┐ │  │
    │  │ │Drivers│ │  │         │  │ │Drivers│ │  │         │  │ │Drivers│ │  │
    │  │ └───────┘ │  │         │  │ └───────┘ │  │         │  │ └───────┘ │  │
    │  └───────────┘  │         │  └───────────┘  │         │  └───────────┘  │
    └────────┬────────┘         └────────┬────────┘         └────────┬────────┘
             │                           │                           │
             ▼                           ▼                           ▼
      [Equipment 1]               [Equipment 2]               [Equipment N]
```

### 1.2 핵심 책임

| 책임 | 설명 |
|------|------|
| **Batch 관리** | Batch 프로세스 생성, 시작, 종료, 모니터링 |
| **시퀀스 로딩** | 시퀀스 패키지 검증 및 로딩 |
| **결과 수집** | Batch에서 결과 수집, 로컬 저장 |
| **Backend 통신** | 결과 전송, 동기화 |
| **UI 서빙** | React UI 정적 파일 서빙, WebSocket |

### 1.3 담당하지 않는 것

- 하드웨어 드라이버 구현
- 장비 통신 로직
- 프로토콜 파싱

### 1.4 기술 스택

| 구성요소 | 기술 | 버전 | 용도 |
|----------|------|------|------|
| Runtime | Python | 3.11+ | 메인 런타임 |
| Web Framework | FastAPI | 0.100+ | REST API, WebSocket |
| Async | asyncio | - | 비동기 처리 |
| IPC | ZeroMQ (pyzmq) | 25+ | Batch 통신 |
| Database | SQLite + aiosqlite | - | 로컬 저장소 |
| Config | Pydantic Settings | 2.0+ | 설정 검증 |
| YAML | PyYAML | 6.0+ | 설정 파일 파싱 |

## 2. 모듈 구조

```
station-service/
├── main.py                    # 엔트리포인트
├── requirements.txt
├── pyproject.toml
│
├── core/
│   ├── __init__.py
│   ├── config.py              # 설정 관리
│   ├── events.py              # 이벤트 정의
│   └── exceptions.py          # 예외 정의
│
├── batch/
│   ├── __init__.py
│   ├── manager.py             # Batch 프로세스 관리
│   ├── process.py             # Batch 프로세스 래퍼
│   ├── worker.py              # Batch Worker (자식 프로세스)
│   └── ipc.py                 # ZeroMQ 통신
│
├── sequence/
│   ├── __init__.py
│   ├── loader.py              # 패키지 로딩
│   ├── validator.py           # 패키지 검증
│   ├── executor.py            # 시퀀스 실행기
│   └── decorators.py          # @sequence, @step 등
│
├── api/
│   ├── __init__.py
│   ├── router.py              # FastAPI 라우터
│   ├── endpoints/
│   │   ├── batches.py         # /api/batches
│   │   ├── sequences.py       # /api/sequences
│   │   ├── results.py         # /api/results
│   │   └── system.py          # /api/system
│   └── websocket.py           # WebSocket 핸들러
│
├── storage/
│   ├── __init__.py
│   ├── database.py            # SQLite 연결
│   ├── models.py              # ORM 모델
│   └── repository.py          # 데이터 접근
│
├── sync/
│   ├── __init__.py
│   ├── engine.py              # 동기화 엔진
│   └── queue.py               # 오프라인 큐
│
└── static/                    # 빌드된 UI (gitignore)
    └── ...
```

## 3. 핵심 컴포넌트

### 3.1 Batch Manager

Batch 프로세스의 생명주기를 관리합니다.

```python
# batch/manager.py

from typing import Dict, Optional
import asyncio
import multiprocessing
from .process import BatchProcess
from .ipc import IPCServer

class BatchManager:
    """Batch 프로세스 관리자"""

    def __init__(self, config: dict):
        self.config = config
        self.batches: Dict[str, BatchProcess] = {}
        self.ipc_server = IPCServer()
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self):
        """매니저 시작"""
        await self.ipc_server.start()
        self._monitor_task = asyncio.create_task(self._monitor_batches())

        # auto_start 배치 시작
        for batch_config in self.config.get('batches', []):
            if batch_config.get('auto_start', False):
                await self.start_batch(batch_config['id'])

    async def stop(self):
        """매니저 종료"""
        if self._monitor_task:
            self._monitor_task.cancel()

        # 모든 배치 종료
        for batch_id in list(self.batches.keys()):
            await self.stop_batch(batch_id)

        await self.ipc_server.stop()

    async def start_batch(self, batch_id: str) -> BatchProcess:
        """Batch 프로세스 시작"""
        if batch_id in self.batches:
            raise ValueError(f"Batch {batch_id} already running")

        batch_config = self._get_batch_config(batch_id)
        if not batch_config:
            raise ValueError(f"Batch {batch_id} not found in config")

        # 프로세스 생성 및 시작
        batch = BatchProcess(
            batch_id=batch_id,
            config=batch_config,
            ipc_address=self.ipc_server.address
        )
        await batch.start()

        self.batches[batch_id] = batch
        return batch

    async def stop_batch(self, batch_id: str) -> bool:
        """Batch 프로세스 종료"""
        if batch_id not in self.batches:
            return False

        batch = self.batches[batch_id]
        await batch.stop()
        del self.batches[batch_id]
        return True

    async def get_batch_status(self, batch_id: str) -> Optional[dict]:
        """Batch 상태 조회"""
        if batch_id not in self.batches:
            return None
        return await self.batches[batch_id].get_status()

    async def send_command(self, batch_id: str, command: str, **params) -> dict:
        """Batch에 명령 전송"""
        if batch_id not in self.batches:
            raise ValueError(f"Batch {batch_id} not running")
        return await self.batches[batch_id].send_command(command, **params)

    async def _monitor_batches(self):
        """Batch 상태 모니터링 (백그라운드)"""
        while True:
            for batch_id, batch in list(self.batches.items()):
                if not batch.is_alive():
                    # 프로세스 비정상 종료 감지
                    await self._handle_batch_crash(batch_id)
            await asyncio.sleep(1)

    async def _handle_batch_crash(self, batch_id: str):
        """Batch 크래시 처리"""
        # 이벤트 발행, 로깅, 알림 등
        pass

    def _get_batch_config(self, batch_id: str) -> Optional[dict]:
        for batch in self.config.get('batches', []):
            if batch['id'] == batch_id:
                return batch
        return None
```

### 3.2 Batch Process (자식 프로세스)

```python
# batch/process.py

import multiprocessing
import asyncio
from typing import Optional

class BatchProcess:
    """Batch 프로세스 래퍼"""

    def __init__(self, batch_id: str, config: dict, ipc_address: str):
        self.batch_id = batch_id
        self.config = config
        self.ipc_address = ipc_address
        self._process: Optional[multiprocessing.Process] = None

    async def start(self):
        """프로세스 시작"""
        self._process = multiprocessing.Process(
            target=self._run_worker,
            args=(self.batch_id, self.config, self.ipc_address),
            daemon=True
        )
        self._process.start()

    async def stop(self, timeout: float = 5.0):
        """프로세스 종료"""
        if self._process and self._process.is_alive():
            # 먼저 정상 종료 시도
            await self.send_command("SHUTDOWN")
            self._process.join(timeout=timeout)

            # 타임아웃 시 강제 종료
            if self._process.is_alive():
                self._process.terminate()
                self._process.join(timeout=1.0)

    def is_alive(self) -> bool:
        return self._process is not None and self._process.is_alive()

    async def send_command(self, command: str, **params) -> dict:
        """IPC로 명령 전송"""
        # ZeroMQ REQ/REP 패턴
        pass

    async def get_status(self) -> dict:
        """상태 조회"""
        return await self.send_command("GET_STATUS")

    @staticmethod
    def _run_worker(batch_id: str, config: dict, ipc_address: str):
        """워커 프로세스 엔트리포인트"""
        from .worker import BatchWorker

        worker = BatchWorker(batch_id, config, ipc_address)
        asyncio.run(worker.run())
```

### 3.3 Batch Worker (실제 시퀀스 실행)

```python
# batch/worker.py

import asyncio
from sequence.loader import SequenceLoader
from sequence.executor import SequenceExecutor
from .ipc import IPCClient

class BatchWorker:
    """Batch 워커 (자식 프로세스에서 실행)"""

    def __init__(self, batch_id: str, config: dict, ipc_address: str):
        self.batch_id = batch_id
        self.config = config
        self.ipc = IPCClient(ipc_address)
        self.loader = SequenceLoader()
        self.executor: SequenceExecutor = None
        self._running = True
        self._current_sequence = None

    async def run(self):
        """메인 루프"""
        await self.ipc.connect()

        # 시퀀스 패키지 로딩
        package_path = self.config['sequence_package']
        package = await self.loader.load(package_path)

        # 드라이버 인스턴스 생성
        drivers = await self._create_drivers(package, self.config['hardware'])

        # Executor 생성
        self.executor = SequenceExecutor(package, drivers)

        # 명령 처리 루프
        while self._running:
            command = await self.ipc.receive_command()
            await self._handle_command(command)

    async def _handle_command(self, command: dict):
        """명령 처리"""
        cmd_type = command['type']

        if cmd_type == "START_SEQUENCE":
            params = command.get('params', {})
            asyncio.create_task(self._run_sequence(params))
            await self.ipc.send_response({"status": "started"})

        elif cmd_type == "STOP_SEQUENCE":
            await self.executor.stop()
            await self.ipc.send_response({"status": "stopped"})

        elif cmd_type == "GET_STATUS":
            status = await self.executor.get_status()
            await self.ipc.send_response(status)

        elif cmd_type == "MANUAL_CONTROL":
            # 수동 제어 모드
            result = await self._execute_manual_command(command['command'])
            await self.ipc.send_response(result)

        elif cmd_type == "SHUTDOWN":
            self._running = False
            await self._cleanup()
            await self.ipc.send_response({"status": "shutdown"})

    async def _run_sequence(self, params: dict):
        """시퀀스 실행"""
        try:
            # 파라미터 적용
            self.executor.set_parameters(params)

            # 실행 (상태 업데이트는 PUB/SUB로 전송)
            result = await self.executor.run(
                on_step_start=self._on_step_start,
                on_step_complete=self._on_step_complete,
                on_log=self._on_log
            )

            # 완료 알림
            await self.ipc.publish("SEQUENCE_COMPLETE", result)

        except Exception as e:
            await self.ipc.publish("SEQUENCE_ERROR", {"error": str(e)})

    async def _on_step_start(self, step_name: str, step_index: int):
        await self.ipc.publish("STEP_START", {
            "step": step_name,
            "index": step_index
        })

    async def _on_step_complete(self, step_name: str, result: dict):
        await self.ipc.publish("STEP_COMPLETE", {
            "step": step_name,
            "result": result
        })

    async def _on_log(self, level: str, message: str):
        await self.ipc.publish("LOG", {
            "level": level,
            "message": message
        })

    async def _create_drivers(self, package, hw_config: dict) -> dict:
        """드라이버 인스턴스 생성"""
        drivers = {}

        for hw_name, hw_spec in package.manifest['hardware'].items():
            driver_module = package.load_driver(hw_spec['driver'])
            driver_class = getattr(driver_module, hw_spec['class'])

            config = hw_config.get(hw_name, {})
            driver = driver_class(**config)
            await driver.connect()

            drivers[hw_name] = driver

        return drivers

    async def _cleanup(self):
        """정리"""
        if self.executor:
            await self.executor.cleanup()
        await self.ipc.disconnect()
```

### 3.4 IPC 통신 (ZeroMQ)

```python
# batch/ipc.py

import zmq
import zmq.asyncio
import json
from typing import Optional

class IPCServer:
    """Station Service의 IPC 서버"""

    def __init__(self, port: int = 5555):
        self.context = zmq.asyncio.Context()
        self.port = port
        self.address = f"tcp://127.0.0.1:{port}"

        # REQ/REP for commands
        self.rep_socket: Optional[zmq.asyncio.Socket] = None
        # PUB/SUB for broadcasts
        self.sub_socket: Optional[zmq.asyncio.Socket] = None

    async def start(self):
        # REP socket (receive commands from workers)
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind(f"tcp://127.0.0.1:{self.port}")

        # SUB socket (receive broadcasts from workers)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.bind(f"tcp://127.0.0.1:{self.port + 1}")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    async def stop(self):
        if self.rep_socket:
            self.rep_socket.close()
        if self.sub_socket:
            self.sub_socket.close()
        self.context.term()


class IPCClient:
    """Batch Worker의 IPC 클라이언트"""

    def __init__(self, server_address: str):
        self.server_address = server_address
        self.context = zmq.asyncio.Context()
        self.req_socket: Optional[zmq.asyncio.Socket] = None
        self.pub_socket: Optional[zmq.asyncio.Socket] = None

    async def connect(self):
        # REQ socket (send commands to server)
        self.req_socket = self.context.socket(zmq.REQ)
        self.req_socket.connect(self.server_address)

        # PUB socket (broadcast to server)
        pub_port = int(self.server_address.split(':')[-1]) + 1
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.connect(f"tcp://127.0.0.1:{pub_port}")

    async def receive_command(self) -> dict:
        """명령 수신 대기"""
        message = await self.req_socket.recv_string()
        return json.loads(message)

    async def send_response(self, response: dict):
        """응답 전송"""
        await self.req_socket.send_string(json.dumps(response))

    async def publish(self, event_type: str, data: dict):
        """이벤트 브로드캐스트"""
        message = json.dumps({
            "batch_id": self.batch_id,
            "type": event_type,
            "data": data
        })
        await self.pub_socket.send_string(message)

    async def disconnect(self):
        if self.req_socket:
            self.req_socket.close()
        if self.pub_socket:
            self.pub_socket.close()
        self.context.term()
```

## 4. API 엔드포인트

### 4.1 REST API

```python
# api/endpoints/batches.py

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/batches", tags=["batches"])

class BatchStatus(BaseModel):
    id: str
    name: str
    status: str  # idle, running, error
    current_step: str | None
    progress: float  # 0.0 ~ 1.0
    sequence_name: str | None

class StartSequenceRequest(BaseModel):
    parameters: dict = {}

@router.get("/", response_model=List[BatchStatus])
async def list_batches():
    """모든 Batch 상태 조회"""
    pass

@router.get("/{batch_id}", response_model=BatchStatus)
async def get_batch(batch_id: str):
    """특정 Batch 상태 조회"""
    pass

@router.post("/{batch_id}/start")
async def start_batch(batch_id: str):
    """Batch 프로세스 시작"""
    pass

@router.post("/{batch_id}/stop")
async def stop_batch(batch_id: str):
    """Batch 프로세스 종료"""
    pass

@router.post("/{batch_id}/sequence/start")
async def start_sequence(batch_id: str, request: StartSequenceRequest):
    """시퀀스 실행 시작"""
    pass

@router.post("/{batch_id}/sequence/stop")
async def stop_sequence(batch_id: str):
    """시퀀스 실행 중단"""
    pass

@router.post("/{batch_id}/manual")
async def manual_control(batch_id: str, command: dict):
    """수동 제어 명령"""
    pass
```

### 4.2 WebSocket

```python
# api/websocket.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 수신 (필요시)
            data = await websocket.receive_json()
            # 처리...
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**WebSocket 메시지 타입:**

```typescript
// 클라이언트 → 서버
{ type: "subscribe", batch_ids: ["batch_1", "batch_2"] }
{ type: "unsubscribe", batch_ids: ["batch_1"] }

// 서버 → 클라이언트
{ type: "batch_status", batch_id: "batch_1", data: {...} }
{ type: "step_start", batch_id: "batch_1", step: "measure", index: 2 }
{ type: "step_complete", batch_id: "batch_1", step: "measure", result: {...} }
{ type: "sequence_complete", batch_id: "batch_1", result: {...} }
{ type: "log", batch_id: "batch_1", level: "info", message: "..." }
{ type: "error", batch_id: "batch_1", error: "..." }
```

## 5. 로컬 저장소

### 5.1 SQLite 스키마

```sql
-- 실행 결과
CREATE TABLE execution_results (
    id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    sequence_name TEXT NOT NULL,
    sequence_version TEXT NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    status TEXT NOT NULL,  -- 'running', 'completed', 'failed', 'stopped'
    parameters JSON,
    result JSON,
    synced_at DATETIME,  -- Backend 동기화 시간
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Step 결과
CREATE TABLE step_results (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    status TEXT NOT NULL,
    result JSON,
    FOREIGN KEY (execution_id) REFERENCES execution_results(id)
);

-- 로그
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    execution_id TEXT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 오프라인 동기화 큐
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- 'execution', 'step'
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,  -- 'create', 'update'
    payload JSON NOT NULL,
    retry_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 6. 설정 관리

```python
# core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import yaml

class BatchConfig(BaseSettings):
    id: str
    name: str
    sequence_package: str
    hardware: dict = {}
    auto_start: bool = False

class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8080

class BackendConfig(BaseSettings):
    url: str = ""
    api_key: str = ""
    sync_interval: int = 30

class StationConfig(BaseSettings):
    id: str
    name: str
    description: str = ""

class Config(BaseSettings):
    station: StationConfig
    server: ServerConfig = ServerConfig()
    backend: BackendConfig = BackendConfig()
    batches: List[BatchConfig] = []

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

## 7. 시작/종료 흐름

### 7.1 시작

```
1. main.py 실행
2. Config 로딩 (station.yaml)
3. Database 초기화 (SQLite)
4. BatchManager 시작
5. Sync Engine 시작 (Backend 연결)
6. FastAPI 서버 시작
7. auto_start Batch 시작
8. 준비 완료
```

### 7.2 종료

```
1. SIGTERM/SIGINT 수신
2. 새 요청 거부
3. 실행 중인 시퀀스 중단
4. 모든 Batch 프로세스 종료
5. 동기화 큐 플러시 (가능하면)
6. Database 연결 종료
7. 프로세스 종료
```

```python
# main.py

import asyncio
import signal
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.config import Config
from batch.manager import BatchManager
from sync.engine import SyncEngine
from storage.database import Database

config = Config.from_yaml("config/station.yaml")
batch_manager: BatchManager = None
sync_engine: SyncEngine = None
database: Database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global batch_manager, sync_engine, database

    # Startup
    database = Database("data/station.db")
    await database.connect()

    batch_manager = BatchManager(config.model_dump())
    await batch_manager.start()

    sync_engine = SyncEngine(config.backend, database)
    await sync_engine.start()

    yield

    # Shutdown
    await sync_engine.stop()
    await batch_manager.stop()
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# Static files (React UI)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# API routes
from api.router import router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.server.host,
        port=config.server.port,
        reload=False
    )
```

## 8. 설계 원칙 및 근거

### 8.1 프로세스 격리 (Process Isolation)

Batch를 독립 프로세스로 분리한 이유:

| 측면 | 장점 |
|------|------|
| **장애 격리** | Batch 1 크래시 → Batch 2 영향 없음 |
| **리소스 격리** | 메모리/CPU 독립적 관리 가능 |
| **독립 재시작** | 개별 Batch만 선택적 재시작 |
| **보안** | 드라이버 코드가 메인 프로세스와 분리 |

```
장점 비교:
┌─────────────────────────────────────────────────────────────────┐
│  멀티스레드 방식          │  멀티프로세스 방식 (현재 설계)    │
│  ─────────────────────── │  ────────────────────────────────  │
│  ✗ GIL로 인한 병목       │  ✓ 진정한 병렬 실행               │
│  ✗ 메모리 공유 위험      │  ✓ 메모리 격리                    │
│  ✗ 하나가 죽으면 전체 위험│  ✓ 개별 프로세스 장애 격리        │
│  ✓ 통신 오버헤드 없음    │  ✗ IPC 오버헤드 (ZeroMQ로 최소화) │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 ZeroMQ 선택 이유

```
통신 방식 비교:
┌────────────────────────────────────────────────────────────────────────┐
│  방식        │ 장점                    │ 단점                         │
│  ──────────  │ ─────────────────────── │ ──────────────────────────── │
│  HTTP/REST   │ 표준, 디버깅 용이       │ 오버헤드 높음, 양방향 불편   │
│  gRPC        │ 효율적, 타입 안전       │ 설정 복잡, 오버헤드 있음     │
│  Redis Pub   │ 신뢰성, 영속성          │ 외부 의존성, 복잡도          │
│  ZeroMQ ✓    │ 저지연, 양방향 패턴     │ 메시지 영속성 없음           │
│  Unix Socket │ 매우 빠름               │ 플랫폼 의존, 기능 제한       │
└────────────────────────────────────────────────────────────────────────┘
```

ZeroMQ 선택 근거:
- **REQ/REP**: 명령-응답 패턴에 적합
- **PUB/SUB**: 실시간 이벤트 브로드캐스트
- **낮은 지연**: 마이크로초 단위 통신
- **비동기**: asyncio 완전 지원

### 8.3 Offline-First 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Offline-First Flow                                │
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│  │   Batch     │────>│   SQLite    │────>│  Sync Queue │                │
│  │   실행      │     │   저장      │     │   (대기열)  │                │
│  └─────────────┘     └─────────────┘     └──────┬──────┘                │
│                                                  │                       │
│                             ┌────────────────────┴────────────────────┐  │
│                             ▼                                         ▼  │
│                      ┌─────────────┐                           ┌────────┐│
│  [Online Mode]       │  즉시 전송  │       [Offline Mode]      │ 연결   ││
│                      │  Backend    │                           │ 복구 시││
│                      └─────────────┘                           │ 동기화 ││
│                                                                └────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

오프라인 동기화 보장:
1. 모든 결과는 먼저 로컬 SQLite에 저장
2. `sync_queue` 테이블에 동기화 대기열 관리
3. Backend 연결 시 순차적으로 동기화
4. 동기화 실패 시 재시도 (retry_count 관리)

## 9. 구현 가이드라인

### 9.1 에러 처리 전략

```python
# core/exceptions.py

class StationError(Exception):
    """Station Service 기본 예외"""
    pass

class BatchError(StationError):
    """Batch 관련 예외"""
    pass

class BatchNotFoundError(BatchError):
    """Batch를 찾을 수 없음"""
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        super().__init__(f"Batch '{batch_id}' not found")

class BatchAlreadyRunningError(BatchError):
    """Batch가 이미 실행 중"""
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        super().__init__(f"Batch '{batch_id}' is already running")

class SequenceError(StationError):
    """시퀀스 관련 예외"""
    pass

class HardwareError(StationError):
    """하드웨어 통신 예외"""
    pass

class IPCError(StationError):
    """IPC 통신 예외"""
    pass
```

### 9.2 로깅 전략

```python
# core/logging.py

import logging
import structlog

def setup_logging(level: str = "INFO", log_file: str = None):
    """구조화된 로깅 설정"""

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# 사용 예시
logger = structlog.get_logger()
logger.info("batch_started", batch_id="batch_1", sequence="PCB_Test")
logger.error("hardware_error", batch_id="batch_1", error="Connection timeout")
```

### 9.3 테스트 전략

```
tests/
├── unit/
│   ├── test_batch_manager.py
│   ├── test_sequence_loader.py
│   ├── test_ipc.py
│   └── test_config.py
├── integration/
│   ├── test_batch_lifecycle.py
│   ├── test_sequence_execution.py
│   └── test_api_endpoints.py
├── e2e/
│   └── test_full_workflow.py
└── fixtures/
    ├── sequences/
    │   └── test_sequence/
    └── configs/
        └── test_station.yaml
```

테스트 작성 가이드:
- **Unit Test**: 각 컴포넌트 독립 테스트
- **Integration Test**: Batch Manager ↔ IPC 통합
- **E2E Test**: 전체 워크플로우 검증

## 10. 운영 가이드

### 10.1 모니터링 체크리스트

| 항목 | 확인 방법 | 정상 기준 |
|------|-----------|-----------|
| 프로세스 상태 | `ps aux | grep station` | 마스터 + Batch 프로세스 실행 중 |
| 포트 상태 | `netstat -tlnp | grep 8080` | 8080 포트 LISTEN |
| ZeroMQ 상태 | IPC 로그 확인 | 연결 에러 없음 |
| 디스크 사용량 | `df -h /opt/station/data` | 80% 미만 |
| Backend 연결 | `/api/system/health` | `backend_connected: true` |

### 10.2 트러블슈팅

#### Batch 프로세스 크래시 시

```bash
# 1. 로그 확인
tail -100 /opt/station/data/logs/station.log | grep -i error

# 2. 프로세스 상태 확인
ps aux | grep batch

# 3. Batch 재시작
curl -X POST http://localhost:8080/api/batches/batch_1/start

# 4. 전체 서비스 재시작 (최후 수단)
systemctl restart station-service
```

#### Backend 동기화 실패 시

```bash
# 1. sync_queue 상태 확인
sqlite3 /opt/station/data/station.db "SELECT * FROM sync_queue ORDER BY created_at DESC LIMIT 10;"

# 2. Backend 연결 테스트
curl -v http://neurohub.local:3000/api/health

# 3. 수동 동기화 트리거
curl -X POST http://localhost:8080/api/system/sync
```

### 10.3 백업 전략

```bash
# 일일 백업 스크립트 예시
#!/bin/bash
BACKUP_DIR="/backup/station/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# SQLite 백업 (온라인 백업)
sqlite3 /opt/station/data/station.db ".backup '$BACKUP_DIR/station.db'"

# 설정 파일 백업
cp /opt/station/config/station.yaml $BACKUP_DIR/

# 7일 이상 오래된 백업 삭제
find /backup/station -type d -mtime +7 -exec rm -rf {} +
```

## 11. 보안 고려사항

### 11.1 네트워크 보안

```yaml
# 권장 설정
server:
  host: "127.0.0.1"  # 로컬 전용
  # host: "0.0.0.0"  # 네트워크 접근 필요시

  # 네트워크 접근 시 인증 활성화 권장
  auth:
    enabled: true
    type: "api_key"
```

### 11.2 민감 정보 관리

```bash
# 환경 변수로 민감 정보 관리
export STATION_BACKEND_API_KEY="your-secret-key"
export STATION_JWT_SECRET="your-jwt-secret"
```

```yaml
# station.yaml에서 환경 변수 참조
backend:
  url: "http://neurohub.local:3000"
  api_key: "${STATION_BACKEND_API_KEY}"
```

## 12. 향후 확장 계획

### 12.1 단기 개선 (Phase 1)

- [ ] 프로세스 체크포인팅 (크래시 복구)
- [ ] Prometheus 메트릭 엔드포인트
- [ ] 향상된 에러 분류 및 처리

### 12.2 중기 개선 (Phase 2)

- [ ] 리소스 제한 (메모리/CPU)
- [ ] 선택적 인증 지원
- [ ] 분산 Batch 지원 (멀티 노드)

### 12.3 장기 개선 (Phase 3)

- [ ] 시퀀스 핫 리로딩
- [ ] A/B 테스트 지원
- [ ] ML 기반 이상 감지

---

## 부록 A: API 빠른 참조

### REST API 요약

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/system/info` | GET | 시스템 정보 |
| `/api/system/health` | GET | 헬스 체크 |
| `/api/batches` | GET | Batch 목록 |
| `/api/batches/{id}` | GET | Batch 상세 |
| `/api/batches/{id}/start` | POST | Batch 시작 |
| `/api/batches/{id}/stop` | POST | Batch 종료 |
| `/api/batches/{id}/sequence/start` | POST | 시퀀스 실행 |
| `/api/batches/{id}/sequence/stop` | POST | 시퀀스 중단 |
| `/api/sequences` | GET | 시퀀스 목록 |
| `/api/results` | GET | 결과 목록 |
| `/ws` | WS | 실시간 업데이트 |

### WebSocket 메시지 요약

```typescript
// 구독
{ type: "subscribe", batch_ids: ["batch_1"] }

// 수신 이벤트
{ type: "batch_status", batch_id: "...", data: {...} }
{ type: "step_start", batch_id: "...", data: {...} }
{ type: "step_complete", batch_id: "...", data: {...} }
{ type: "sequence_complete", batch_id: "...", data: {...} }
{ type: "log", batch_id: "...", data: {...} }
{ type: "error", batch_id: "...", data: {...} }
```

---

## 부록 B: 의존성 목록

```txt
# requirements.txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyzmq>=25.0.0
aiosqlite>=0.19.0
pyyaml>=6.0
structlog>=23.0.0
httpx>=0.24.0  # Backend 통신용
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2025-12-30 | 초기 문서 작성 |
| 1.1.0 | 2025-12-30 | 아키텍처 다이어그램, 설계 원칙, 구현 가이드라인, 운영 가이드 추가 |
| 1.2.0 | 2025-12-30 | 문서 분리: 요구사항 명세(spec.md)와 상세 설계(design.md)로 분리 |
