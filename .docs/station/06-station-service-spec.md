# 06. Station Service 요구사항 명세

## 구현 체크리스트

> Phase 3.1 - 프로젝트 구조 생성

### 프로젝트 스켈레톤
- [x] `station_service/` 루트 디렉토리 생성
- [x] `station_service/__init__.py`
- [x] `station_service/main.py` - FastAPI 앱 진입점
- [x] `station_service/models/config.py` - 설정 모델

### 디렉토리 구조
- [x] `station_service/api/` - REST API 라우터
- [x] `station_service/batch/` - Batch 관리
- [x] `station_service/sequence/` - 시퀀스 패키지 로더
- [x] `station_service/storage/` - SQLite 저장소
- [x] `station_service/sync/` - Backend 동기화
- [x] `station_service/ipc/` - ZeroMQ 통신
- [x] `station_service/core/` - 예외 및 이벤트 정의

### 설정 파일
- [x] `station_service/config/station.yaml.example` - 설정 예제
- [x] `station_service/requirements.txt` - 의존성

---

## Document Information
- **Version**: 1.0.0
- **Date**: 2025-12-30
- **Type**: Requirements Specification
- **Related**: [07-station-service-design.md](./07-station-service-design.md) (상세 설계)

---

## 1. 개요

Station Service는 Station PC에서 실행되는 마스터 프로세스로, 시퀀스 패키지의 로딩/실행/관리를 담당합니다.

### 1.1 시스템 개요도

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

---

## 2. 기능 요구사항

### 2.1 Batch 관리

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| BR-001 | Batch 프로세스를 생성하고 시작할 수 있어야 한다 | High |
| BR-002 | Batch 프로세스를 정상 종료할 수 있어야 한다 | High |
| BR-003 | Batch 프로세스 상태를 실시간으로 조회할 수 있어야 한다 | High |
| BR-004 | Batch 프로세스 크래시를 감지하고 알림을 발송해야 한다 | Medium |
| BR-005 | auto_start 설정된 Batch는 서비스 시작 시 자동 실행되어야 한다 | Medium |
| BR-006 | 개별 Batch를 선택적으로 재시작할 수 있어야 한다 | Medium |

### 2.2 시퀀스 실행

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| SR-001 | 시퀀스 패키지를 로딩하고 검증할 수 있어야 한다 | High |
| SR-002 | 런타임 파라미터를 적용하여 시퀀스를 실행할 수 있어야 한다 | High |
| SR-003 | 실행 중인 시퀀스를 중단할 수 있어야 한다 | High |
| SR-004 | Step 진행 상황을 실시간으로 UI에 전달해야 한다 | High |
| SR-005 | 시퀀스 완료 결과를 로컬에 저장해야 한다 | High |

### 2.3 Backend 동기화

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| SY-001 | 실행 결과를 Backend에 전송해야 한다 | High |
| SY-002 | 오프라인 상태에서도 결과를 로컬에 저장해야 한다 | High |
| SY-003 | 네트워크 복구 시 미동기화 결과를 자동 전송해야 한다 | High |
| SY-004 | 동기화 실패 시 재시도 메커니즘을 제공해야 한다 | Medium |
| SY-005 | 동기화 상태를 조회할 수 있어야 한다 | Low |

### 2.4 수동 제어

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| MC-001 | 수동 모드에서 개별 하드웨어 명령을 실행할 수 있어야 한다 | Medium |
| MC-002 | 수동 명령 결과를 즉시 반환해야 한다 | Medium |
| MC-003 | 시퀀스 실행 중 수동 제어가 불가능해야 한다 (안전) | High |

---

## 3. API 명세

### 3.1 REST API

#### 3.1.1 시스템 API

| 엔드포인트 | 메서드 | 설명 | 응답 |
|-----------|--------|------|------|
| `/api/system/info` | GET | 시스템 정보 조회 | StationInfo |
| `/api/system/health` | GET | 헬스 체크 | HealthStatus |
| `/api/system/sync` | POST | 수동 동기화 트리거 | SyncResult |

#### 3.1.2 Batch API

| 엔드포인트 | 메서드 | 설명 | 요청 | 응답 |
|-----------|--------|------|------|------|
| `/api/batches` | GET | Batch 목록 조회 | - | BatchStatus[] |
| `/api/batches/{id}` | GET | Batch 상세 조회 | - | BatchDetail |
| `/api/batches/{id}/start` | POST | Batch 프로세스 시작 | - | { status, pid } |
| `/api/batches/{id}/stop` | POST | Batch 프로세스 종료 | - | { status } |
| `/api/batches/{id}/sequence/start` | POST | 시퀀스 실행 | { parameters } | { executionId } |
| `/api/batches/{id}/sequence/stop` | POST | 시퀀스 중단 | - | { status } |
| `/api/batches/{id}/manual` | POST | 수동 명령 실행 | { hardware, command, params } | CommandResult |

#### 3.1.3 시퀀스 API

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/sequences` | GET | 시퀀스 패키지 목록 |
| `/api/sequences/{name}` | GET | 시퀀스 패키지 상세 |

#### 3.1.4 결과 API

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/results` | GET | 결과 목록 (페이징) |
| `/api/results/{id}` | GET | 결과 상세 |
| `/api/results/{id}/export` | GET | 결과 내보내기 (JSON/CSV) |

### 3.2 WebSocket API

#### 3.2.1 연결

```
ws://localhost:8080/ws
```

#### 3.2.2 클라이언트 → 서버

```typescript
// Batch 구독
{ type: "subscribe", batch_ids: ["batch_1", "batch_2"] }

// Batch 구독 해제
{ type: "unsubscribe", batch_ids: ["batch_1"] }
```

#### 3.2.3 서버 → 클라이언트

```typescript
// Batch 상태 변경
{ type: "batch_status", batch_id: "batch_1", data: {
  status: "running",
  currentStep: "measure",
  progress: 0.75
}}

// Step 시작
{ type: "step_start", batch_id: "batch_1", data: {
  step: "measure",
  index: 2,
  total: 5
}}

// Step 완료
{ type: "step_complete", batch_id: "batch_1", data: {
  step: "measure",
  duration: 2.5,
  pass: true,
  result: {...}
}}

// 시퀀스 완료
{ type: "sequence_complete", batch_id: "batch_1", data: {
  executionId: "exec_123",
  overallPass: true,
  duration: 45.2,
  steps: [...]
}}

// 로그
{ type: "log", batch_id: "batch_1", data: {
  level: "info",
  message: "Measuring voltage...",
  timestamp: "2025-01-01T12:00:00Z"
}}

// 에러
{ type: "error", batch_id: "batch_1", data: {
  code: "HARDWARE_ERROR",
  message: "Connection timeout",
  step: "initialize"
}}
```

---

## 4. 데이터 모델 (개념)

### 4.1 Batch

```typescript
interface Batch {
  id: string;                    // 고유 식별자
  name: string;                  // 표시 이름
  sequencePackage: string;       // 시퀀스 패키지 경로
  hardware: Record<string, HardwareConfig>;  // 하드웨어 설정
  autoStart: boolean;            // 자동 시작 여부
}
```

### 4.2 Batch Status

```typescript
interface BatchStatus {
  id: string;
  name: string;
  status: 'idle' | 'starting' | 'running' | 'stopping' | 'error';
  pid?: number;                  // 프로세스 ID
  currentStep?: string;
  stepIndex?: number;
  totalSteps?: number;
  progress?: number;             // 0.0 ~ 1.0
  sequenceName?: string;
  sequenceVersion?: string;
  startedAt?: Date;
  elapsed?: number;              // 경과 시간 (초)
}
```

### 4.3 Execution Result

```typescript
interface ExecutionResult {
  id: string;
  batchId: string;
  sequenceName: string;
  sequenceVersion: string;
  status: 'running' | 'completed' | 'failed' | 'stopped';
  overallPass: boolean;
  parameters: Record<string, any>;
  steps: StepResult[];
  startedAt: Date;
  completedAt?: Date;
  duration?: number;
  syncedAt?: Date;               // Backend 동기화 시간
}
```

### 4.4 Step Result

```typescript
interface StepResult {
  name: string;
  order: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  pass: boolean;
  startedAt?: Date;
  completedAt?: Date;
  duration?: number;
  result?: Record<string, any>;
  error?: string;
}
```

---

## 5. 비기능 요구사항

### 5.1 성능

| 항목 | 요구사항 |
|------|----------|
| API 응답 시간 | < 100ms (95th percentile) |
| WebSocket 지연 | < 50ms |
| Batch 시작 시간 | < 3초 |
| 동시 Batch 수 | 최소 10개 지원 |

### 5.2 안정성

| 항목 | 요구사항 |
|------|----------|
| Batch 프로세스 격리 | Batch 크래시가 다른 Batch에 영향 없음 |
| 데이터 영속성 | 결과는 항상 로컬에 먼저 저장 |
| 자동 복구 | Batch 크래시 감지 및 알림 |

### 5.3 가용성

| 항목 | 요구사항 |
|------|----------|
| 오프라인 동작 | Backend 연결 없이도 시퀀스 실행 가능 |
| 자동 재연결 | Backend 연결 복구 시 자동 동기화 |

---

## 6. 운영 가이드

### 6.1 시작/종료 흐름

#### 시작

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

#### 종료

```
1. SIGTERM/SIGINT 수신
2. 새 요청 거부
3. 실행 중인 시퀀스 중단
4. 모든 Batch 프로세스 종료
5. 동기화 큐 플러시 (가능하면)
6. Database 연결 종료
7. 프로세스 종료
```

### 6.2 모니터링 체크리스트

| 항목 | 확인 방법 | 정상 기준 |
|------|-----------|-----------|
| 프로세스 상태 | `ps aux \| grep station` | 마스터 + Batch 프로세스 실행 중 |
| 포트 상태 | `netstat -tlnp \| grep 8080` | 8080 포트 LISTEN |
| ZeroMQ 상태 | IPC 로그 확인 | 연결 에러 없음 |
| 디스크 사용량 | `df -h /opt/station/data` | 80% 미만 |
| Backend 연결 | `/api/system/health` | `backend_connected: true` |

### 6.3 트러블슈팅

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

### 6.4 백업 전략

```bash
#!/bin/bash
# 일일 백업 스크립트 예시
BACKUP_DIR="/backup/station/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# SQLite 백업 (온라인 백업)
sqlite3 /opt/station/data/station.db ".backup '$BACKUP_DIR/station.db'"

# 설정 파일 백업
cp /opt/station/config/station.yaml $BACKUP_DIR/

# 7일 이상 오래된 백업 삭제
find /backup/station -type d -mtime +7 -exec rm -rf {} +
```

---

## 7. 보안 고려사항

### 7.1 네트워크 보안

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

### 7.2 민감 정보 관리

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

---

## 8. 향후 확장 계획

### 8.1 단기 개선 (Phase 1)

- [ ] 프로세스 체크포인팅 (크래시 복구)
- [ ] Prometheus 메트릭 엔드포인트
- [ ] 향상된 에러 분류 및 처리

### 8.2 중기 개선 (Phase 2)

- [ ] 리소스 제한 (메모리/CPU)
- [ ] 선택적 인증 지원
- [ ] 분산 Batch 지원 (멀티 노드)

### 8.3 장기 개선 (Phase 3)

- [ ] 시퀀스 핫 리로딩
- [ ] A/B 테스트 지원
- [ ] ML 기반 이상 감지

---

## 부록 A: 의존성 목록

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
| 1.0.0 | 2025-12-30 | 초기 요구사항 명세 분리 |
