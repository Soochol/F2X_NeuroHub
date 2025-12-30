# 02. Data Models

## 구현 체크리스트

> Phase 1.2 - 데이터 모델 구현

### Python (Backend)
- [x] `station_service/models/__init__.py` 생성
- [x] `station_service/models/station.py` - Station 모델
- [x] `station_service/models/batch.py` - Batch, BatchDetail 모델
- [x] `station_service/models/sequence.py` - SequencePackage 관련 모델
- [x] `station_service/models/execution.py` - ExecutionResult, StepResult 모델
- [x] `station_service/models/hardware.py` - HardwareStatus 모델
- [x] `station_service/models/config.py` - StationConfig, BatchConfig 모델
- [x] `station_service/models/messages.py` - WebSocket/IPC 메시지 모델

### TypeScript (Frontend)
- [x] `station_ui/src/types/station.ts` - Station 타입
- [x] `station_ui/src/types/batch.ts` - Batch 타입
- [x] `station_ui/src/types/sequence.ts` - SequencePackage 타입
- [x] `station_ui/src/types/execution.ts` - ExecutionResult 타입
- [x] `station_ui/src/types/messages.ts` - WebSocket 메시지 타입
- [x] `station_ui/src/types/index.ts` - 통합 export

### Database
- [x] `station_service/storage/schema.sql` 생성
- [x] `station_service/storage/database.py` - SQLite 래퍼

---

## 1. 개요

Station Service에서 사용하는 데이터 모델을 정의합니다.

## 2. Core Models

### 2.1 Station

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Station(BaseModel):
    id: str                    # "ST-001"
    name: str                  # "Station 1"
    description: Optional[str] # "PCB 테스트 스테이션"
    version: str               # "1.0.0"
    status: str                # "online", "offline"
    backend_connected: bool
    uptime: int                # seconds
```

```typescript
// TypeScript
interface Station {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: 'online' | 'offline';
  backendConnected: boolean;
  uptime: number;
}
```

### 2.2 Batch

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BatchStatus(str, Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"

class Batch(BaseModel):
    id: str                        # "batch_1"
    name: str                      # "Batch 1"
    status: BatchStatus
    sequence_name: Optional[str]   # "PCB_Voltage_Test"
    sequence_version: Optional[str]
    sequence_package: str          # "sequences/pcb_voltage_test"

    # 실행 상태
    current_step: Optional[str]
    step_index: int = 0
    total_steps: int = 0
    progress: float = 0.0          # 0.0 ~ 1.0

    # 시간
    started_at: Optional[datetime]
    elapsed: int = 0               # seconds

    # 설정
    hardware_config: Dict[str, Dict[str, Any]]
    auto_start: bool = False

    # 프로세스 정보
    pid: Optional[int]

class BatchDetail(Batch):
    """Batch 상세 정보 (API 응답용)"""

    parameters: Dict[str, Any] = {}
    hardware_status: Dict[str, HardwareStatus] = {}
    execution: Optional[ExecutionStatus] = None
```

```typescript
// TypeScript
type BatchStatus = 'idle' | 'starting' | 'running' | 'stopping' | 'completed' | 'error';

interface Batch {
  id: string;
  name: string;
  status: BatchStatus;
  sequenceName?: string;
  sequenceVersion?: string;
  sequencePackage: string;

  currentStep?: string;
  stepIndex: number;
  totalSteps: number;
  progress: number;

  startedAt?: Date;
  elapsed: number;

  hardwareConfig: Record<string, Record<string, any>>;
  autoStart: boolean;

  pid?: number;
}

interface BatchDetail extends Batch {
  parameters: Record<string, any>;
  hardwareStatus: Record<string, HardwareStatus>;
  execution?: ExecutionStatus;
}
```

### 2.3 Sequence Package

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ParameterSchema(BaseModel):
    name: str
    display_name: str
    type: str                      # "float", "integer", "string", "boolean"
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[str]] = None
    unit: Optional[str] = None
    description: Optional[str] = None

class HardwareSchema(BaseModel):
    id: str
    display_name: str
    driver: str                    # 드라이버 파일 경로
    class_name: str                # 드라이버 클래스 이름
    description: Optional[str]
    config_schema: Dict[str, Dict[str, Any]]

class StepSchema(BaseModel):
    order: int
    name: str
    display_name: str
    description: str
    timeout: float = 60.0
    retry: int = 0
    cleanup: bool = False
    condition: Optional[str] = None

class SequencePackage(BaseModel):
    name: str                      # "pcb_voltage_test"
    version: str                   # "1.2.0"
    display_name: str
    description: str
    author: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    path: str                      # "sequences/pcb_voltage_test"

    hardware: List[HardwareSchema]
    parameters: List[ParameterSchema]
    steps: List[StepSchema]
```

```typescript
// TypeScript
interface ParameterSchema {
  name: string;
  displayName: string;
  type: 'float' | 'integer' | 'string' | 'boolean';
  default: any;
  min?: number;
  max?: number;
  options?: string[];
  unit?: string;
  description?: string;
}

interface HardwareSchema {
  id: string;
  displayName: string;
  driver: string;
  className: string;
  description?: string;
  configSchema: Record<string, Record<string, any>>;
}

interface StepSchema {
  order: number;
  name: string;
  displayName: string;
  description: string;
  timeout: number;
  retry: number;
  cleanup: boolean;
  condition?: string;
}

interface SequencePackage {
  name: string;
  version: string;
  displayName: string;
  description: string;
  author?: string;
  createdAt?: string;
  updatedAt?: string;
  path: string;

  hardware: HardwareSchema[];
  parameters: ParameterSchema[];
  steps: StepSchema[];
}
```

### 2.4 Execution (실행 결과)

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class StepResult(BaseModel):
    name: str
    order: int
    status: str                    # "pending", "running", "completed", "failed", "skipped"
    pass_: bool = True             # 필드명 충돌로 pass_ 사용
    duration: Optional[float]      # seconds
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

    class Config:
        fields = {'pass_': 'pass'}

class ExecutionResult(BaseModel):
    id: str                        # "exec_20250120_123456"
    batch_id: str
    sequence_name: str
    sequence_version: str
    status: ExecutionStatus
    overall_pass: bool

    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[int]        # seconds

    parameters: Dict[str, Any]
    steps: List[StepResult]

    synced_at: Optional[datetime]  # Backend 동기화 시간

class ExecutionSummary(BaseModel):
    """실행 결과 목록용 요약"""
    id: str
    batch_id: str
    sequence_name: str
    sequence_version: str
    status: ExecutionStatus
    overall_pass: bool
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[int]
    synced: bool
```

```typescript
// TypeScript
type ExecutionStatus = 'running' | 'completed' | 'failed' | 'stopped';

interface StepResult {
  name: string;
  order: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  pass: boolean;
  duration?: number;
  startedAt?: Date;
  completedAt?: Date;
  result?: Record<string, any>;
  error?: string;
}

interface ExecutionResult {
  id: string;
  batchId: string;
  sequenceName: string;
  sequenceVersion: string;
  status: ExecutionStatus;
  overallPass: boolean;

  startedAt: Date;
  completedAt?: Date;
  duration?: number;

  parameters: Record<string, any>;
  steps: StepResult[];

  syncedAt?: Date;
}

interface ExecutionSummary {
  id: string;
  batchId: string;
  sequenceName: string;
  sequenceVersion: string;
  status: ExecutionStatus;
  overallPass: boolean;
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  synced: boolean;
}
```

### 2.5 Hardware Status

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import Optional, Dict, Any

class HardwareStatus(BaseModel):
    id: str                        # "dmm"
    driver: str                    # "KeysightDMM"
    status: str                    # "connected", "disconnected", "error"
    connected: bool
    last_error: Optional[str]
    config: Dict[str, Any]         # 실제 적용된 설정
    info: Optional[Dict[str, Any]] # 장비 정보 (IDN 등)
```

```typescript
// TypeScript
interface HardwareStatus {
  id: string;
  driver: string;
  status: 'connected' | 'disconnected' | 'error';
  connected: boolean;
  lastError?: string;
  config: Record<string, any>;
  info?: Record<string, any>;
}
```

### 2.6 Log Entry

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class LogEntry(BaseModel):
    id: int
    batch_id: str
    execution_id: Optional[str]
    level: LogLevel
    message: str
    timestamp: datetime
```

```typescript
// TypeScript
type LogLevel = 'debug' | 'info' | 'warning' | 'error';

interface LogEntry {
  id: number;
  batchId: string;
  executionId?: string;
  level: LogLevel;
  message: string;
  timestamp: Date;
}
```

## 3. Configuration Models

### 3.1 Station Config (station.yaml)

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080

class BackendConfig(BaseModel):
    url: str = ""
    api_key: str = ""
    sync_interval: int = 30        # seconds

class StationInfo(BaseModel):
    id: str
    name: str
    description: str = ""

class BatchConfig(BaseModel):
    id: str
    name: str
    sequence_package: str
    hardware: Dict[str, Dict[str, Any]]
    auto_start: bool = False

class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "data/logs/station.log"
    max_size: str = "10MB"
    backup_count: int = 5

class StationConfig(BaseModel):
    station: StationInfo
    server: ServerConfig = ServerConfig()
    backend: BackendConfig = BackendConfig()
    batches: List[BatchConfig] = []
    logging: LoggingConfig = LoggingConfig()
```

### 3.2 Manifest (manifest.yaml)

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ConfigField(BaseModel):
    type: str                      # "string", "integer", "float", "boolean"
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    options: Optional[List[Any]] = None
    min: Optional[float] = None
    max: Optional[float] = None

class HardwareDefinition(BaseModel):
    display_name: str
    driver: str                    # 상대 경로
    class_name: str                # 클래스 이름 (class는 예약어)
    description: Optional[str] = None
    config_schema: Dict[str, ConfigField]

    class Config:
        fields = {'class_name': 'class'}

class ParameterDefinition(BaseModel):
    display_name: str
    type: str
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[Any]] = None
    unit: Optional[str] = None
    description: Optional[str] = None

class EntryPoint(BaseModel):
    module: str                    # "sequence"
    class_name: str                # "PCBVoltageTest"

    class Config:
        fields = {'class_name': 'class'}

class SequenceManifest(BaseModel):
    name: str
    version: str
    author: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    entry_point: EntryPoint
    hardware: Dict[str, HardwareDefinition]
    parameters: Dict[str, ParameterDefinition]
    dependencies: Optional[Dict[str, List[str]]] = None
```

## 4. WebSocket Message Models

### 4.1 Client Messages

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import List, Literal

class SubscribeMessage(BaseModel):
    type: Literal["subscribe"] = "subscribe"
    batch_ids: List[str]

class UnsubscribeMessage(BaseModel):
    type: Literal["unsubscribe"] = "unsubscribe"
    batch_ids: List[str]
```

```typescript
// TypeScript
interface SubscribeMessage {
  type: 'subscribe';
  batchIds: string[];
}

interface UnsubscribeMessage {
  type: 'unsubscribe';
  batchIds: string[];
}

type ClientMessage = SubscribeMessage | UnsubscribeMessage;
```

### 4.2 Server Messages

```python
# Python (Pydantic)
from pydantic import BaseModel
from typing import Literal, Dict, Any, Optional
from datetime import datetime

class BatchStatusMessage(BaseModel):
    type: Literal["batch_status"] = "batch_status"
    batch_id: str
    data: Dict[str, Any]

class StepStartMessage(BaseModel):
    type: Literal["step_start"] = "step_start"
    batch_id: str
    data: Dict[str, Any]  # step, index, total

class StepCompleteMessage(BaseModel):
    type: Literal["step_complete"] = "step_complete"
    batch_id: str
    data: Dict[str, Any]  # step, index, duration, pass, result

class SequenceCompleteMessage(BaseModel):
    type: Literal["sequence_complete"] = "sequence_complete"
    batch_id: str
    data: Dict[str, Any]  # execution_id, overall_pass, duration, steps

class LogMessage(BaseModel):
    type: Literal["log"] = "log"
    batch_id: str
    data: Dict[str, Any]  # level, message, timestamp

class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    batch_id: str
    data: Dict[str, Any]  # code, message, step, timestamp
```

```typescript
// TypeScript
interface BatchStatusMessage {
  type: 'batch_status';
  batchId: string;
  data: {
    status: BatchStatus;
    currentStep?: string;
    stepIndex: number;
    progress: number;
  };
}

interface StepStartMessage {
  type: 'step_start';
  batchId: string;
  data: {
    step: string;
    index: number;
    total: number;
  };
}

interface StepCompleteMessage {
  type: 'step_complete';
  batchId: string;
  data: {
    step: string;
    index: number;
    duration: number;
    pass: boolean;
    result?: Record<string, any>;
  };
}

interface SequenceCompleteMessage {
  type: 'sequence_complete';
  batchId: string;
  data: {
    executionId: string;
    overallPass: boolean;
    duration: number;
    steps: StepResult[];
  };
}

interface LogMessage {
  type: 'log';
  batchId: string;
  data: {
    level: LogLevel;
    message: string;
    timestamp: Date;
  };
}

interface ErrorMessage {
  type: 'error';
  batchId: string;
  data: {
    code: string;
    message: string;
    step?: string;
    timestamp: Date;
  };
}

type ServerMessage =
  | BatchStatusMessage
  | StepStartMessage
  | StepCompleteMessage
  | SequenceCompleteMessage
  | LogMessage
  | ErrorMessage;
```

## 5. Database Schema (SQLite)

```sql
-- Station 설정 (변경 이력용)
CREATE TABLE station_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 실행 결과
CREATE TABLE execution_results (
    id TEXT PRIMARY KEY,              -- "exec_20250120_123456"
    batch_id TEXT NOT NULL,
    sequence_name TEXT NOT NULL,
    sequence_version TEXT NOT NULL,
    status TEXT NOT NULL,             -- running, completed, failed, stopped
    overall_pass BOOLEAN,
    parameters_json TEXT,             -- JSON
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    duration INTEGER,                 -- seconds
    synced_at DATETIME,               -- Backend 동기화 시간
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_batch_id (batch_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
);

-- Step 결과
CREATE TABLE step_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    status TEXT NOT NULL,             -- pending, running, completed, failed, skipped
    pass BOOLEAN,
    result_json TEXT,                 -- JSON
    error TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    duration REAL,                    -- seconds (float)

    FOREIGN KEY (execution_id) REFERENCES execution_results(id),
    INDEX idx_execution_id (execution_id)
);

-- 로그
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    execution_id TEXT,
    level TEXT NOT NULL,              -- debug, info, warning, error
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_batch_id (batch_id),
    INDEX idx_level (level),
    INDEX idx_timestamp (timestamp)
);

-- 동기화 큐 (오프라인 모드)
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,        -- execution, log
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,             -- create, update
    payload_json TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_entity_type (entity_type)
);
```

## 6. IPC Message Models (ZeroMQ)

### 6.1 Master → Worker

```python
# Python
from pydantic import BaseModel
from typing import Literal, Dict, Any, Optional

class StartSequenceCommand(BaseModel):
    type: Literal["START_SEQUENCE"] = "START_SEQUENCE"
    parameters: Dict[str, Any] = {}

class StopSequenceCommand(BaseModel):
    type: Literal["STOP_SEQUENCE"] = "STOP_SEQUENCE"

class GetStatusCommand(BaseModel):
    type: Literal["GET_STATUS"] = "GET_STATUS"

class ManualControlCommand(BaseModel):
    type: Literal["MANUAL_CONTROL"] = "MANUAL_CONTROL"
    hardware: str
    command: str
    params: Dict[str, Any] = {}

class ShutdownCommand(BaseModel):
    type: Literal["SHUTDOWN"] = "SHUTDOWN"
```

### 6.2 Worker → Master (Response)

```python
# Python
from pydantic import BaseModel
from typing import Dict, Any, Optional

class CommandResponse(BaseModel):
    status: str                       # "ok", "error"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

### 6.3 Worker → Master (Broadcast/PUB)

```python
# Python
from pydantic import BaseModel
from typing import Literal, Dict, Any
from datetime import datetime

class StepStartEvent(BaseModel):
    type: Literal["STEP_START"] = "STEP_START"
    batch_id: str
    step: str
    index: int
    timestamp: datetime

class StepCompleteEvent(BaseModel):
    type: Literal["STEP_COMPLETE"] = "STEP_COMPLETE"
    batch_id: str
    step: str
    index: int
    duration: float
    pass_: bool
    result: Dict[str, Any]
    timestamp: datetime

class SequenceCompleteEvent(BaseModel):
    type: Literal["SEQUENCE_COMPLETE"] = "SEQUENCE_COMPLETE"
    batch_id: str
    execution_id: str
    overall_pass: bool
    duration: int
    result: Dict[str, Any]
    timestamp: datetime

class LogEvent(BaseModel):
    type: Literal["LOG"] = "LOG"
    batch_id: str
    level: str
    message: str
    timestamp: datetime

class ErrorEvent(BaseModel):
    type: Literal["ERROR"] = "ERROR"
    batch_id: str
    code: str
    message: str
    step: Optional[str] = None
    timestamp: datetime
```
