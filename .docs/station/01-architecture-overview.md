# 01. Architecture Overview

## 1. 시스템 컨텍스트

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Factory Network                                 │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  Station 1  │     │  Station 2  │     │  Station N  │                   │
│  │     PC      │     │     PC      │     │     PC      │                   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│         │                   │                   │                           │
│         └───────────────────┼───────────────────┘                           │
│                             │                                               │
│                             ▼                                               │
│                    ┌─────────────────┐                                      │
│                    │  NeuroHub       │                                      │
│                    │  Backend        │                                      │
│                    └─────────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Station PC 내부 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Station PC                                      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     Station Service (Master Process)                   │  │
│  │                                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐   │  │
│  │  │  FastAPI     │  │  WebSocket   │  │   Static File Server       │   │  │
│  │  │  REST API    │  │  Server      │  │   (React UI 서빙)          │   │  │
│  │  │              │  │              │  │                            │   │  │
│  │  │ - Backend    │  │ - UI 실시간  │  │ - localhost:8080           │   │  │
│  │  │   통신       │  │   업데이트   │  │ - 브라우저 접속            │   │  │
│  │  │ - 상태 조회  │  │ - Batch 상태 │  │                            │   │  │
│  │  └──────────────┘  └──────────────┘  └────────────────────────────┘   │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                      Batch Manager                               │  │  │
│  │  │                                                                  │  │  │
│  │  │  - Batch 프로세스 생성/시작/종료                                 │  │  │
│  │  │  - 프로세스 상태 모니터링                                        │  │  │
│  │  │  - ZeroMQ 기반 IPC 통신                                          │  │  │
│  │  │  - 결과 수집 및 저장                                             │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │  │
│  │  │  Sync Engine    │  │  Local DB       │  │  Config Manager     │   │  │
│  │  │                 │  │  (SQLite)       │  │                     │   │  │
│  │  │ - Backend 동기화│  │ - 실행 결과     │  │ - station.yaml      │   │  │
│  │  │ - 오프라인 큐   │  │ - 로그 저장     │  │ - batch 설정        │   │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│              ┌───────────────────────┼───────────────────────┐              │
│              │ ZeroMQ               │ ZeroMQ               │ ZeroMQ        │
│              ▼                       ▼                       ▼              │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐     │
│  │    Batch 1        │   │    Batch 2        │   │    Batch N        │     │
│  │  (독립 프로세스)  │   │  (독립 프로세스)  │   │  (독립 프로세스)  │     │
│  │                   │   │                   │   │                   │     │
│  │ ┌───────────────┐ │   │ ┌───────────────┐ │   │ ┌───────────────┐ │     │
│  │ │   Sequence    │ │   │ │   Sequence    │ │   │ │   Sequence    │ │     │
│  │ │   Package     │ │   │ │   Package     │ │   │ │   Package     │ │     │
│  │ │               │ │   │ │               │ │   │ │               │ │     │
│  │ │ ┌───────────┐ │ │   │ │ ┌───────────┐ │ │   │ │ ┌───────────┐ │ │     │
│  │ │ │ sequence  │ │ │   │ │ │ sequence  │ │ │   │ │ │ sequence  │ │ │     │
│  │ │ │ .py       │ │ │   │ │ │ .py       │ │ │   │ │ │ .py       │ │ │     │
│  │ │ ├───────────┤ │ │   │ │ ├───────────┤ │ │   │ │ ├───────────┤ │ │     │
│  │ │ │ drivers/  │ │ │   │ │ │ drivers/  │ │ │   │ │ │ drivers/  │ │ │     │
│  │ │ │ (HW통신)  │ │ │   │ │ │ (HW통신)  │ │ │   │ │ │ (HW통신)  │ │ │     │
│  │ │ └───────────┘ │ │   │ │ └───────────┘ │ │   │ │ └───────────┘ │ │     │
│  │ └───────────────┘ │   │ └───────────────┘ │   │ └───────────────┘ │     │
│  │         │         │   │         │         │   │         │         │     │
│  └─────────┼─────────┘   └─────────┼─────────┘   └─────────┼─────────┘     │
│            │                       │                       │               │
│            ▼                       ▼                       ▼               │
│     [Equipment 1]           [Equipment 2]           [Equipment N]          │
│     (Serial/TCP/OPC-UA)     (Serial/TCP/OPC-UA)     (Serial/TCP/OPC-UA)    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3. 핵심 설계 원칙

### 3.1 Thin Station Service

Station Service는 **시퀀스 실행/관리**만 담당합니다.

| 담당 | 담당하지 않음 |
|------|--------------|
| 시퀀스 패키지 로딩 | 드라이버 구현 |
| Batch 프로세스 관리 | 하드웨어 통신 로직 |
| 결과 수집/저장 | 프로토콜 파싱 |
| Backend 통신 | 장비별 명령어 |
| UI 서빙 | |

### 3.2 Self-contained Sequence Package

시퀀스 패키지는 **드라이버 + 시퀀스**가 통합된 완전한 배포 단위입니다.

```
sequence_package/
├── manifest.yaml      # 메타데이터
├── sequence.py        # 시퀀스 로직
├── drivers/           # 하드웨어 드라이버
│   ├── dmm.py
│   └── plc.py
└── utils/             # 유틸리티
```

### 3.3 Offline-first

Station은 Backend 연결 없이도 독립 동작합니다.

```
[Online Mode]
Batch 실행 → 결과 저장 → Backend 즉시 전송

[Offline Mode]
Batch 실행 → 결과 저장 → 로컬 큐에 보관 → 연결 복구 시 동기화
```

### 3.4 Independent Batch Process

각 Batch는 독립된 OS 프로세스로 실행됩니다.

**장점:**
- 장애 격리: Batch 1 크래시 → Batch 2 영향 없음
- 리소스 격리: 메모리/CPU 독립
- 독립 재시작: 개별 Batch만 재시작 가능

**통신:**
- ZeroMQ REQ/REP: 명령 전송
- ZeroMQ PUB/SUB: 상태 브로드캐스트

## 4. 통신 흐름

### 4.1 Station ↔ Backend

```
┌──────────────┐                              ┌──────────────┐
│   Station    │                              │   Backend    │
│   Service    │                              │   (NeuroHub) │
└──────┬───────┘                              └──────┬───────┘
       │                                             │
       │  ──── REST API (결과 전송) ────────────────>│
       │                                             │
       │  <─── REST API (시퀀스 목록 조회) ──────────│
       │                                             │
       │  <════ WebSocket (실시간 상태) ════════════>│
       │                                             │
```

### 4.2 Station Service ↔ Batch (ZeroMQ)

```
┌──────────────────┐                         ┌──────────────────┐
│  Station Service │                         │     Batch        │
│  (Master)        │                         │   (Worker)       │
└────────┬─────────┘                         └────────┬─────────┘
         │                                            │
         │  ──── REQ: START_SEQUENCE ────────────────>│
         │  <─── REP: ACK ────────────────────────────│
         │                                            │
         │  <════ PUB: STATUS_UPDATE ════════════════ │
         │  <════ PUB: STEP_COMPLETE ════════════════ │
         │  <════ PUB: SEQUENCE_COMPLETE ════════════ │
         │                                            │
         │  ──── REQ: STOP_SEQUENCE ─────────────────>│
         │  <─── REP: ACK ────────────────────────────│
```

### 4.3 Station UI ↔ Station Service

```
┌──────────────────┐                         ┌──────────────────┐
│   Browser        │                         │  Station Service │
│   (Station UI)   │                         │                  │
└────────┬─────────┘                         └────────┬─────────┘
         │                                            │
         │  ──── HTTP GET /api/batches ──────────────>│
         │  <─── JSON Response ───────────────────────│
         │                                            │
         │  ════ WebSocket Connect ══════════════════>│
         │  <═══ ws: batch_status ═══════════════════ │
         │  <═══ ws: step_progress ══════════════════ │
         │  <═══ ws: log_entry ══════════════════════ │
```

## 5. 배포 구조

### 5.1 폴더 구조

```
/opt/station/
├── station-service/           # Station Service
│   ├── main.py
│   ├── core/
│   ├── api/
│   └── requirements.txt
│
├── station-ui/                # 빌드된 React UI
│   ├── index.html
│   ├── assets/
│   └── ...
│
├── sequences/                 # 시퀀스 패키지들
│   ├── pcb_test_v1/
│   ├── aging_test_v2/
│   └── ...
│
├── data/                      # 로컬 데이터
│   ├── station.db             # SQLite
│   ├── logs/
│   └── results/
│
└── config/
    └── station.yaml           # 설정 파일
```

### 5.2 station.yaml 예시

```yaml
station:
  id: "ST-001"
  name: "Station 1"
  description: "PCB 테스트 스테이션"

server:
  host: "0.0.0.0"
  port: 8080

backend:
  url: "http://neurohub.local:3000"
  api_key: "xxx"
  sync_interval: 30  # seconds

batches:
  - id: "batch_1"
    name: "Batch 1"
    sequence_package: "sequences/pcb_test_v1"
    hardware:
      dmm:
        port: "/dev/ttyUSB0"
        baudrate: 9600
      power:
        ip: "192.168.1.100"
        port: 5025
    auto_start: true

  - id: "batch_2"
    name: "Batch 2"
    sequence_package: "sequences/pcb_test_v1"
    hardware:
      dmm:
        port: "/dev/ttyUSB1"
        baudrate: 9600
      power:
        ip: "192.168.1.101"
        port: 5025
    auto_start: false

logging:
  level: "INFO"
  file: "data/logs/station.log"
  max_size: "10MB"
  backup_count: 5
```

## 6. 기술 스택 상세

| 구성요소 | 기술 | 버전 | 용도 |
|----------|------|------|------|
| **Station Service** |
| Runtime | Python | 3.11+ | 메인 런타임 |
| Web Framework | FastAPI | 0.100+ | REST API, WebSocket |
| Async | asyncio | - | 비동기 처리 |
| IPC | ZeroMQ (pyzmq) | 25+ | Batch 통신 |
| Database | SQLite + aiosqlite | - | 로컬 저장소 |
| **Station UI** |
| Framework | React | 18+ | UI 프레임워크 |
| Language | TypeScript | 5+ | 타입 안전성 |
| Build | Vite | 5+ | 빌드 도구 |
| State | Zustand | 4+ | 상태 관리 |
| WebSocket | socket.io-client | 4+ | 실시간 통신 |
| **Sequence Package** |
| Decorators | Custom | - | @sequence, @step |
| Hardware | pyserial, opcua | - | 장비 통신 |

## 7. 보안 고려사항

### 7.1 네트워크

- Station Service는 **로컬 네트워크**에서만 접근
- Backend 통신은 **API Key** 기반 인증
- HTTPS 사용 권장 (프로덕션)

### 7.2 인증

- Station UI: **인증 없음** (로컬 전용 환경)
- Backend API: JWT 토큰 또는 API Key

### 7.3 데이터

- 민감 설정은 환경 변수로 관리
- 로컬 DB 암호화 (선택)

## 8. 향후 개선 사항 (Recommended Enhancements)

### 8.1 프로세스 복구 및 체크포인팅 (Process Recovery with Checkpointing)

Batch 프로세스의 안정성 향상을 위한 자동 복구 메커니즘입니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BATCH RECOVERY SYSTEM                                 │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Batch Manager (Enhanced)                          │  │
│  │                                                                        │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │  │
│  │  │  Health Monitor │    │  Recovery Engine │    │  State Persister│   │  │
│  │  │                 │    │                  │    │                 │   │  │
│  │  │  - heartbeat    │    │  - auto restart  │    │  - checkpoint   │   │  │
│  │  │  - timeout      │───>│  - backoff       │───>│  - resume state │   │  │
│  │  │  - crash detect │    │  - max retries   │    │  - rollback     │   │  │
│  │  │                 │    │                  │    │                 │   │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │  │
│  │                                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Recovery Flow:                                                              │
│                                                                              │
│    Crash ──> Detect ──> Log ──> Wait(backoff) ──> Restart ──> Resume        │
│                │                     │                            │          │
│                ▼                     ▼                            ▼          │
│           Alert UI            Increment Count            Load Checkpoint     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**주요 기능:**
- **Heartbeat 모니터링**: Batch 프로세스 상태를 주기적으로 확인
- **자동 재시작**: 크래시 감지 시 exponential backoff로 재시작
- **체크포인트 저장**: Step 완료 시마다 상태 저장
- **상태 복구**: 재시작 시 마지막 체크포인트부터 재개

**설정 예시:**
```yaml
recovery:
  enabled: true
  max_retries: 3
  backoff_base: 2  # seconds
  backoff_max: 60  # seconds
  checkpoint_interval: 1  # steps
```

### 8.2 리소스 제한 (Resource Limits for Batch Processes)

각 Batch 프로세스의 리소스 사용량을 제한하여 시스템 안정성을 확보합니다.

```yaml
# station.yaml 확장
batches:
  - id: "batch_1"
    name: "Batch 1"
    sequence_package: "sequences/pcb_test_v1"

    # 리소스 제한 설정
    resource_limits:
      max_memory_mb: 512        # 최대 메모리 사용량
      cpu_affinity: [0, 1]      # 사용할 CPU 코어
      priority: "normal"        # low, normal, high
      timeout_sequence: 3600    # 시퀀스 최대 실행 시간 (초)
      timeout_step: 300         # Step 최대 실행 시간 (초)
```

**리소스 모니터링:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Batch Resource Monitor                                          │
│                                                                  │
│  Batch 1:  Memory [████████░░] 78%   CPU [███░░░░░░░] 32%       │
│  Batch 2:  Memory [██████░░░░] 58%   CPU [████░░░░░░] 41%       │
│  Batch 3:  Memory [████░░░░░░] 42%   CPU [██░░░░░░░░] 18%       │
│                                                                  │
│  [!] Warning: Batch 1 approaching memory limit                   │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 에러 처리 계층 (Enhanced Error Hierarchy)

구조화된 에러 처리로 다양한 상황에 대응합니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ERROR HANDLING HIERARCHY                             │
│                                                                              │
│  Level 1: Step Error                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Step fails ──> Retry (if configured) ──> Continue/Fail based on type  ││
│  │                                                                          ││
│  │  Types:                                                                  ││
│  │    - CRITICAL: 시퀀스 즉시 중단                                          ││
│  │    - RECOVERABLE: Backoff와 함께 재시도                                  ││
│  │    - WARNING: 로그 기록 후 계속 진행                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Level 2: Hardware Error                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Connection lost ──> Reconnect (3x) ──> Pause sequence ──> Alert UI    ││
│  │                                                                          ││
│  │  Actions:                                                                ││
│  │    - AUTO_RECONNECT: 자동 재연결 시도                                    ││
│  │    - PAUSE_WAIT: 일시 중지 후 운영자 대기                                ││
│  │    - SAFE_STOP: Cleanup 실행 후 안전 종료                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Level 3: Process Error                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Batch crash ──> Detect ──> Save state ──> Restart ──> Resume/Restart  ││
│  │                                                                          ││
│  │  Recovery:                                                               ││
│  │    - FULL_RESTART: 시퀀스 처음부터 재시작                                ││
│  │    - RESUME: 마지막 체크포인트부터 재개                                  ││
│  │    - SKIP_FAILED: 실패한 Step 건너뛰고 계속                              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**에러 설정 예시:**
```yaml
error_handling:
  step_errors:
    default_action: "retry"
    max_retries: 3

  hardware_errors:
    reconnect_attempts: 3
    reconnect_delay: 5  # seconds
    on_failure: "pause_wait"  # auto_reconnect, pause_wait, safe_stop

  process_errors:
    recovery_mode: "resume"  # full_restart, resume, skip_failed
```

### 8.4 선택적 인증 (Optional Authentication for Non-local Access)

로컬 네트워크 외부 접근 시 인증을 지원합니다.

```yaml
# station.yaml 확장
server:
  host: "0.0.0.0"
  port: 8080

  # 인증 설정 (선택)
  auth:
    enabled: false              # true로 설정 시 인증 활성화
    type: "basic"               # basic, jwt, api_key

    # Basic Auth
    basic:
      username: "admin"
      password_hash: "..."      # bcrypt hash

    # JWT (선택)
    jwt:
      secret_key: "${JWT_SECRET}"
      algorithm: "HS256"
      expire_minutes: 60

    # 허용 IP 목록 (인증 우회)
    whitelist:
      - "127.0.0.1"
      - "192.168.1.0/24"
```

**인증 흐름:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │     │   Service    │     │   Auth       │
│   Request    │     │   Gateway    │     │   Module     │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │  Request           │                    │
       │───────────────────>│                    │
       │                    │                    │
       │                    │  Check IP          │
       │                    │───────────────────>│
       │                    │                    │
       │                    │  IP Whitelisted?   │
       │                    │<───────────────────│
       │                    │                    │
       │  [If not whitelisted]                  │
       │                    │  Validate Token    │
       │                    │───────────────────>│
       │                    │                    │
       │                    │  Token Valid?      │
       │                    │<───────────────────│
       │                    │                    │
       │  Response          │                    │
       │<───────────────────│                    │
```

### 8.5 메트릭 엔드포인트 (Metrics Endpoint for Monitoring)

Prometheus 호환 메트릭을 제공하여 외부 모니터링 시스템과 통합합니다.

**엔드포인트:** `GET /metrics`

```
# HELP station_batches_total Total number of configured batches
# TYPE station_batches_total gauge
station_batches_total 5

# HELP station_batches_running Number of currently running batches
# TYPE station_batches_running gauge
station_batches_running 3

# HELP station_sequences_completed_total Total completed sequences
# TYPE station_sequences_completed_total counter
station_sequences_completed_total{batch="batch_1",result="pass"} 127
station_sequences_completed_total{batch="batch_1",result="fail"} 12

# HELP station_sequence_duration_seconds Sequence execution duration
# TYPE station_sequence_duration_seconds histogram
station_sequence_duration_seconds_bucket{batch="batch_1",le="60"} 45
station_sequence_duration_seconds_bucket{batch="batch_1",le="120"} 89
station_sequence_duration_seconds_bucket{batch="batch_1",le="300"} 127
station_sequence_duration_seconds_sum{batch="batch_1"} 12456.78
station_sequence_duration_seconds_count{batch="batch_1"} 127

# HELP station_hardware_status Hardware connection status
# TYPE station_hardware_status gauge
station_hardware_status{batch="batch_1",hardware="dmm"} 1
station_hardware_status{batch="batch_1",hardware="power"} 1

# HELP station_backend_connected Backend connection status
# TYPE station_backend_connected gauge
station_backend_connected 1

# HELP station_sync_queue_size Pending items in sync queue
# TYPE station_sync_queue_size gauge
station_sync_queue_size 0
```

**Grafana 대시보드 연동:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'station'
    static_configs:
      - targets: ['station-1:8080', 'station-2:8080']
    metrics_path: '/metrics'
```

**제공 메트릭:**

| 메트릭 | 타입 | 설명 |
|--------|------|------|
| `station_batches_total` | Gauge | 설정된 전체 Batch 수 |
| `station_batches_running` | Gauge | 실행 중인 Batch 수 |
| `station_sequences_completed_total` | Counter | 완료된 시퀀스 수 (pass/fail) |
| `station_sequence_duration_seconds` | Histogram | 시퀀스 실행 시간 분포 |
| `station_step_duration_seconds` | Histogram | Step 실행 시간 분포 |
| `station_hardware_status` | Gauge | 하드웨어 연결 상태 (1=연결, 0=해제) |
| `station_backend_connected` | Gauge | Backend 연결 상태 |
| `station_sync_queue_size` | Gauge | 동기화 대기 항목 수 |
| `station_errors_total` | Counter | 에러 발생 횟수 (타입별) |
| `station_process_memory_bytes` | Gauge | 프로세스 메모리 사용량 |
| `station_process_cpu_percent` | Gauge | 프로세스 CPU 사용률 |

### 8.6 확장된 폴더 구조

향후 개선 사항을 반영한 폴더 구조입니다.

```
/opt/station/
├── station-service/           # Station Service
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   └── recovery.py        # [NEW] 복구 로직
│   ├── batch/
│   │   ├── manager.py
│   │   ├── process.py
│   │   ├── worker.py
│   │   ├── ipc.py
│   │   └── checkpoint.py      # [NEW] 체크포인트 관리
│   ├── sequence/
│   ├── api/
│   │   ├── endpoints/
│   │   │   └── metrics.py     # [NEW] 메트릭 엔드포인트
│   │   └── middleware/
│   │       └── auth.py        # [NEW] 인증 미들웨어
│   ├── storage/
│   └── sync/
│
├── data/
│   ├── station.db
│   ├── logs/
│   ├── checkpoints/           # [NEW] 체크포인트 저장
│   └── results/
│
└── config/
    ├── station.yaml
    └── station.yaml.backup    # [NEW] 설정 백업
```
