# 03. API Specification

## 구현 체크리스트

> Phase 1.3 - API 스키마 정의

### FastAPI 라우터 스켈레톤
- [x] `station_service/api/__init__.py` 생성
- [x] `station_service/api/routes/system.py` - GET /api/system/info, /health
- [x] `station_service/api/routes/batches.py` - Batch CRUD, start/stop
- [x] `station_service/api/routes/sequences.py` - 시퀀스 패키지 조회
- [x] `station_service/api/routes/results.py` - 실행 결과 조회
- [x] `station_service/api/routes/logs.py` - 로그 조회

### WebSocket
- [x] `station_service/api/websocket.py` - WebSocket 핸들러
- [x] Subscribe/Unsubscribe 메시지 처리
- [x] 서버→클라이언트 이벤트 브로드캐스트

### 응답 스키마
- [x] `station_service/api/schemas/responses.py` - 공통 응답 형식
- [x] `station_service/api/schemas/batch.py` - Batch 응답 스키마
- [x] `station_service/api/schemas/sequence.py` - Sequence 응답 스키마
- [x] `station_service/api/schemas/result.py` - Result 응답 스키마

---

## 1. 개요

Station Service는 REST API와 WebSocket을 제공합니다.

### 1.1 Base URL

```
http://localhost:8080
```

### 1.2 공통 응답 형식

```typescript
// 성공 응답
{
  "success": true,
  "data": { ... }
}

// 에러 응답
{
  "success": false,
  "error": {
    "code": "BATCH_NOT_FOUND",
    "message": "Batch with id 'batch_1' not found"
  }
}
```

## 2. REST API

### 2.1 System

#### GET /api/system/info

Station 시스템 정보 조회

**Response:**
```json
{
  "success": true,
  "data": {
    "station_id": "ST-001",
    "station_name": "Station 1",
    "description": "PCB 테스트 스테이션",
    "version": "1.0.0",
    "uptime": 3600,
    "backend_connected": true
  }
}
```

#### GET /api/system/health

헬스 체크

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "batches_running": 2,
    "backend_status": "connected",
    "disk_usage": 45.2
  }
}
```

---

### 2.2 Batches

#### GET /api/batches

모든 Batch 목록 조회

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "batch_1",
      "name": "Batch 1",
      "status": "running",
      "sequence_name": "PCB_Voltage_Test",
      "sequence_version": "1.2.0",
      "current_step": "voltage_measurement",
      "step_index": 3,
      "total_steps": 5,
      "progress": 0.6,
      "started_at": "2025-01-20T12:30:00Z",
      "elapsed": 145
    },
    {
      "id": "batch_2",
      "name": "Batch 2",
      "status": "idle",
      "sequence_name": "PCB_Voltage_Test",
      "sequence_version": "1.2.0",
      "current_step": null,
      "step_index": 0,
      "total_steps": 5,
      "progress": 0,
      "started_at": null,
      "elapsed": 0
    }
  ]
}
```

#### GET /api/batches/{batch_id}

특정 Batch 상세 조회

**Parameters:**
- `batch_id` (path): Batch ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "batch_1",
    "name": "Batch 1",
    "status": "running",
    "sequence": {
      "name": "PCB_Voltage_Test",
      "version": "1.2.0",
      "package_path": "sequences/pcb_voltage_test"
    },
    "parameters": {
      "voltage_limit": 5.5,
      "current_limit": 1.0,
      "test_points": 10,
      "dut_type": "TypeA",
      "enable_aging": false
    },
    "hardware": {
      "dmm": {
        "status": "connected",
        "driver": "KeysightDMM",
        "port": "/dev/ttyUSB0"
      },
      "power": {
        "status": "connected",
        "driver": "AgilentPowerSupply",
        "ip": "192.168.1.100"
      }
    },
    "execution": {
      "status": "running",
      "current_step": "voltage_measurement",
      "step_index": 3,
      "total_steps": 5,
      "progress": 0.6,
      "started_at": "2025-01-20T12:30:00Z",
      "elapsed": 145,
      "steps": [
        {
          "name": "initialize",
          "status": "completed",
          "duration": 2.3,
          "result": { "status": "initialized" }
        },
        {
          "name": "power_on_test",
          "status": "completed",
          "duration": 5.1,
          "result": { "voltage": 5.0, "current": 0.234 }
        },
        {
          "name": "voltage_check",
          "status": "completed",
          "duration": 3.2,
          "result": { "all_pass": true }
        },
        {
          "name": "voltage_measurement",
          "status": "running",
          "duration": null,
          "result": null
        },
        {
          "name": "finalize",
          "status": "pending",
          "duration": null,
          "result": null
        }
      ]
    }
  }
}
```

#### POST /api/batches/{batch_id}/start

Batch 프로세스 시작

**Parameters:**
- `batch_id` (path): Batch ID

**Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_1",
    "status": "started",
    "pid": 12345
  }
}
```

#### POST /api/batches/{batch_id}/stop

Batch 프로세스 종료

**Parameters:**
- `batch_id` (path): Batch ID

**Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_1",
    "status": "stopped"
  }
}
```

#### POST /api/batches/{batch_id}/sequence/start

시퀀스 실행 시작

**Parameters:**
- `batch_id` (path): Batch ID

**Request Body:**
```json
{
  "parameters": {
    "voltage_limit": 5.5,
    "current_limit": 1.0,
    "test_points": 10,
    "dut_type": "TypeA",
    "enable_aging": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_1",
    "execution_id": "exec_20250120_123456",
    "status": "started"
  }
}
```

#### POST /api/batches/{batch_id}/sequence/stop

시퀀스 실행 중단

**Parameters:**
- `batch_id` (path): Batch ID

**Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_1",
    "status": "stopped"
  }
}
```

#### POST /api/batches/{batch_id}/manual

수동 제어 명령 실행

**Parameters:**
- `batch_id` (path): Batch ID

**Request Body:**
```json
{
  "hardware": "dmm",
  "command": "measure_dc_voltage",
  "params": {
    "range": "AUTO"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hardware": "dmm",
    "command": "measure_dc_voltage",
    "result": {
      "voltage": 4.987,
      "unit": "V"
    }
  }
}
```

---

### 2.3 Sequences

#### GET /api/sequences

모든 시퀀스 패키지 목록 조회

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "pcb_voltage_test",
      "version": "1.2.0",
      "display_name": "PCB Voltage Test",
      "description": "PCB 전압 테스트 시퀀스",
      "path": "sequences/pcb_voltage_test",
      "updated_at": "2025-01-15T10:00:00Z"
    },
    {
      "name": "aging_test",
      "version": "2.0.0",
      "display_name": "Aging Test",
      "description": "에이징 테스트 시퀀스",
      "path": "sequences/aging_test",
      "updated_at": "2025-01-10T08:30:00Z"
    }
  ]
}
```

#### GET /api/sequences/{sequence_name}

시퀀스 패키지 상세 조회 (파싱된 정보)

**Parameters:**
- `sequence_name` (path): 시퀀스 패키지 이름

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "pcb_voltage_test",
    "version": "1.2.0",
    "display_name": "PCB Voltage Test",
    "description": "PCB 전압 테스트 시퀀스",
    "author": "개발팀",
    "created_at": "2025-01-15",
    "updated_at": "2025-01-20",

    "hardware": [
      {
        "id": "dmm",
        "display_name": "디지털 멀티미터",
        "driver": "KeysightDMM",
        "config_schema": {
          "port": { "type": "string", "required": true },
          "baudrate": { "type": "integer", "default": 9600 }
        }
      },
      {
        "id": "power",
        "display_name": "파워 서플라이",
        "driver": "AgilentPowerSupply",
        "config_schema": {
          "ip": { "type": "string", "required": true },
          "port": { "type": "integer", "default": 5025 }
        }
      }
    ],

    "parameters": [
      {
        "name": "voltage_limit",
        "display_name": "전압 상한",
        "type": "float",
        "default": 5.5,
        "min": 0.0,
        "max": 50.0,
        "unit": "V"
      },
      {
        "name": "current_limit",
        "display_name": "전류 상한",
        "type": "float",
        "default": 1.0,
        "min": 0.0,
        "max": 10.0,
        "unit": "A"
      },
      {
        "name": "test_points",
        "display_name": "테스트 포인트 수",
        "type": "integer",
        "default": 10,
        "min": 1,
        "max": 100
      },
      {
        "name": "dut_type",
        "display_name": "DUT 타입",
        "type": "string",
        "default": "TypeA",
        "options": ["TypeA", "TypeB", "TypeC"]
      },
      {
        "name": "enable_aging",
        "display_name": "에이징 테스트",
        "type": "boolean",
        "default": false
      }
    ],

    "steps": [
      {
        "order": 1,
        "name": "initialize",
        "display_name": "장비 초기화",
        "description": "파워 서플라이 초기화, DMM 초기화 및 자가진단",
        "timeout": 30,
        "retry": 3,
        "cleanup": false,
        "condition": null
      },
      {
        "order": 2,
        "name": "power_on_test",
        "display_name": "전원 인가 테스트",
        "description": "전원을 인가하고 초기 전류를 확인합니다.",
        "timeout": 60,
        "retry": 0,
        "cleanup": false,
        "condition": null
      },
      {
        "order": 3,
        "name": "voltage_measurement",
        "display_name": "전압 측정 테스트",
        "description": "여러 포인트에서 전압을 측정합니다.",
        "timeout": 120,
        "retry": 0,
        "cleanup": false,
        "condition": null
      },
      {
        "order": 4,
        "name": "aging_test",
        "display_name": "에이징 테스트",
        "description": "에이징 테스트 (조건부 실행)",
        "timeout": 300,
        "retry": 0,
        "cleanup": false,
        "condition": "enable_aging"
      },
      {
        "order": 5,
        "name": "finalize",
        "display_name": "정리",
        "description": "정리 (항상 실행)",
        "timeout": 30,
        "retry": 0,
        "cleanup": true,
        "condition": null
      }
    ]
  }
}
```

#### PUT /api/sequences/{sequence_name}

시퀀스 패키지 수정 (파라미터, Step 순서 등)

**Parameters:**
- `sequence_name` (path): 시퀀스 패키지 이름

**Request Body:**
```json
{
  "parameters": [
    {
      "name": "voltage_limit",
      "default": 6.0
    }
  ],
  "steps": [
    {
      "name": "initialize",
      "order": 1,
      "timeout": 45
    },
    {
      "name": "power_on_test",
      "order": 2
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "pcb_voltage_test",
    "version": "1.2.1",
    "updated_at": "2025-01-20T14:30:00Z"
  }
}
```

---

### 2.4 Results

#### GET /api/results

실행 결과 목록 조회

**Query Parameters:**
- `batch_id` (optional): 특정 Batch 필터
- `status` (optional): 상태 필터 (completed, failed)
- `from` (optional): 시작 날짜
- `to` (optional): 종료 날짜
- `limit` (optional): 결과 수 제한 (default: 50)
- `offset` (optional): 오프셋

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 127,
    "items": [
      {
        "id": "exec_20250120_123456",
        "batch_id": "batch_1",
        "sequence_name": "PCB_Voltage_Test",
        "sequence_version": "1.2.0",
        "status": "completed",
        "overall_pass": true,
        "started_at": "2025-01-20T12:30:00Z",
        "completed_at": "2025-01-20T12:33:24Z",
        "duration": 204,
        "synced": true
      },
      {
        "id": "exec_20250120_121530",
        "batch_id": "batch_5",
        "sequence_name": "PCB_Voltage_Test",
        "sequence_version": "1.2.0",
        "status": "failed",
        "overall_pass": false,
        "started_at": "2025-01-20T12:15:30Z",
        "completed_at": "2025-01-20T12:17:15Z",
        "duration": 105,
        "synced": false
      }
    ]
  }
}
```

#### GET /api/results/{result_id}

실행 결과 상세 조회

**Parameters:**
- `result_id` (path): 실행 결과 ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "exec_20250120_123456",
    "batch_id": "batch_1",
    "sequence_name": "PCB_Voltage_Test",
    "sequence_version": "1.2.0",
    "status": "completed",
    "overall_pass": true,
    "started_at": "2025-01-20T12:30:00Z",
    "completed_at": "2025-01-20T12:33:24Z",
    "duration": 204,
    "parameters": {
      "voltage_limit": 5.5,
      "current_limit": 1.0,
      "test_points": 10,
      "dut_type": "TypeA"
    },
    "steps": [
      {
        "name": "initialize",
        "order": 1,
        "status": "completed",
        "pass": true,
        "duration": 2.3,
        "started_at": "2025-01-20T12:30:00Z",
        "completed_at": "2025-01-20T12:30:02Z",
        "result": {
          "status": "initialized",
          "dmm_id": "Keysight 34461A"
        }
      },
      {
        "name": "power_on_test",
        "order": 2,
        "status": "completed",
        "pass": true,
        "duration": 5.1,
        "started_at": "2025-01-20T12:30:02Z",
        "completed_at": "2025-01-20T12:30:07Z",
        "result": {
          "voltage": 5.0,
          "current": 0.234,
          "pass": true
        }
      }
    ]
  }
}
```

#### GET /api/results/{result_id}/export

실행 결과 내보내기

**Parameters:**
- `result_id` (path): 실행 결과 ID

**Query Parameters:**
- `format`: 형식 (json, csv)

**Response (CSV):**
```
step_name,status,pass,duration,voltage,current
initialize,completed,true,2.3,,
power_on_test,completed,true,5.1,5.0,0.234
voltage_measurement,completed,true,45.2,,
finalize,completed,true,1.5,,
```

---

### 2.5 Logs

#### GET /api/logs

로그 조회

**Query Parameters:**
- `batch_id` (optional): 특정 Batch 필터
- `level` (optional): 레벨 필터 (debug, info, warning, error)
- `from` (optional): 시작 시간
- `to` (optional): 종료 시간
- `search` (optional): 검색어
- `limit` (optional): 결과 수 제한 (default: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 1500,
    "items": [
      {
        "id": 1234,
        "batch_id": "batch_1",
        "execution_id": "exec_20250120_123456",
        "level": "info",
        "message": "Step \"power_on_test\" completed",
        "timestamp": "2025-01-20T12:34:56Z"
      },
      {
        "id": 1233,
        "batch_id": "batch_5",
        "execution_id": "exec_20250120_121530",
        "level": "error",
        "message": "Voltage exceeded limit: 6.2V > 5.5V",
        "timestamp": "2025-01-20T12:34:30Z"
      }
    ]
  }
}
```

---

## 3. WebSocket API

### 3.1 연결

```
ws://localhost:8080/ws
```

### 3.2 클라이언트 → 서버

#### Subscribe

특정 Batch 이벤트 구독

```json
{
  "type": "subscribe",
  "batch_ids": ["batch_1", "batch_2"]
}
```

#### Unsubscribe

구독 해제

```json
{
  "type": "unsubscribe",
  "batch_ids": ["batch_1"]
}
```

### 3.3 서버 → 클라이언트

#### batch_status

Batch 상태 변경

```json
{
  "type": "batch_status",
  "batch_id": "batch_1",
  "data": {
    "status": "running",
    "current_step": "voltage_measurement",
    "step_index": 3,
    "progress": 0.6
  }
}
```

#### step_start

Step 시작

```json
{
  "type": "step_start",
  "batch_id": "batch_1",
  "data": {
    "step": "voltage_measurement",
    "index": 3,
    "total": 5
  }
}
```

#### step_complete

Step 완료

```json
{
  "type": "step_complete",
  "batch_id": "batch_1",
  "data": {
    "step": "voltage_measurement",
    "index": 3,
    "duration": 45.2,
    "pass": true,
    "result": {
      "measurements": [...],
      "all_pass": true
    }
  }
}
```

#### sequence_complete

시퀀스 완료

```json
{
  "type": "sequence_complete",
  "batch_id": "batch_1",
  "data": {
    "execution_id": "exec_20250120_123456",
    "overall_pass": true,
    "duration": 204,
    "steps": [...]
  }
}
```

#### log

로그 메시지

```json
{
  "type": "log",
  "batch_id": "batch_1",
  "data": {
    "level": "info",
    "message": "Measured voltage: 4.987V",
    "timestamp": "2025-01-20T12:34:56Z"
  }
}
```

#### error

에러 발생

```json
{
  "type": "error",
  "batch_id": "batch_1",
  "data": {
    "code": "TEST_FAILURE",
    "message": "Voltage exceeded limit: 6.2V > 5.5V",
    "step": "voltage_measurement",
    "timestamp": "2025-01-20T12:34:56Z"
  }
}
```

---

## 4. Backend 통신 API

Station Service가 NeuroHub Backend에 전송하는 API입니다.

### 4.1 결과 전송

#### POST /api/stations/{station_id}/results

```json
{
  "execution_id": "exec_20250120_123456",
  "batch_id": "batch_1",
  "sequence_name": "PCB_Voltage_Test",
  "sequence_version": "1.2.0",
  "status": "completed",
  "overall_pass": true,
  "started_at": "2025-01-20T12:30:00Z",
  "completed_at": "2025-01-20T12:33:24Z",
  "parameters": {...},
  "steps": [...]
}
```

### 4.2 상태 업데이트

#### POST /api/stations/{station_id}/heartbeat

```json
{
  "station_id": "ST-001",
  "status": "online",
  "batches": [
    { "id": "batch_1", "status": "running" },
    { "id": "batch_2", "status": "idle" }
  ],
  "timestamp": "2025-01-20T12:34:56Z"
}
```

---

## 5. 에러 코드

| 코드 | 설명 |
|------|------|
| `BATCH_NOT_FOUND` | Batch를 찾을 수 없음 |
| `BATCH_ALREADY_RUNNING` | Batch가 이미 실행 중 |
| `BATCH_NOT_RUNNING` | Batch가 실행 중이 아님 |
| `SEQUENCE_NOT_FOUND` | 시퀀스를 찾을 수 없음 |
| `SEQUENCE_ALREADY_RUNNING` | 시퀀스가 이미 실행 중 |
| `HARDWARE_ERROR` | 하드웨어 통신 오류 |
| `HARDWARE_NOT_CONNECTED` | 하드웨어 미연결 |
| `INVALID_PARAMETERS` | 잘못된 파라미터 |
| `TIMEOUT` | 타임아웃 |
| `INTERNAL_ERROR` | 내부 오류 |
