# Backend 요구사항

> user-specification 및 backend/docs/api 기반 Backend 관련 요구사항 통합 정리

---

## 1. 기술 스택

### 1.1 핵심 기술
- **언어**: Python 3.11+
- **프레임워크**: FastAPI
- **ASGI 서버**: Uvicorn (multi-worker)
- **프로세스 관리**: Gunicorn + Uvicorn workers
- **ORM**: SQLAlchemy 2.0 (async)
- **마이그레이션**: Alembic

### 1.2 캐시
- **Redis 7.0+**
  - 용도: 세션, 임시 데이터, API 캐시
  - TTL: 5분~1시간
  - 메모리: 4GB 권장
  - Persistence: AOF

### 1.3 성능 최적화 설정
- Worker 프로세스: CPU 코어 수 × 2
- Connection Pool: min 10, max 50, overflow 20
- 비동기 I/O: asyncio, httpx

---

## 2. API 기본 정보

### 2.1 Base URL
```
Development: http://localhost:8000
Production: https://api.f2x-neurohub.com
```

### 2.2 API Version
- Current Version: **v1** (`/api/v1`)
- Future: v2 (Phase 2 AI 기능)

### 2.3 Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 2.4 Authentication
모든 보호된 엔드포인트는 JWT 인증 필요:
```
Authorization: Bearer <access_token>
```

---

## 3. API 엔드포인트

### 3.1 인증 API (Authentication)

#### POST /api/v1/auth/login
사용자 로그인

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200 OK):
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "role": "ADMIN"
  }
}
```

#### GET /api/v1/auth/me
현재 인증된 사용자 정보

**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "ADMIN",
  "is_active": true
}
```

#### POST /api/v1/auth/refresh
Access Token 갱신

#### POST /api/v1/auth/logout
로그아웃

---

### 3.2 사용자 관리 API (User Management)

#### GET /api/v1/users
사용자 목록 조회

**Authentication**: Required (ADMIN, MANAGER)

**Query Parameters**:
- `skip`: int (default: 0)
- `limit`: int (default: 100)
- `role`: UserRole (ADMIN, MANAGER, OPERATOR)
- `is_active`: boolean

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "department": "IT",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### POST /api/v1/users
사용자 생성

**Authentication**: Required (ADMIN)

**Request Body**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "New User",
  "role": "OPERATOR",
  "department": "Production"
}
```

#### GET /api/v1/users/{user_id}
사용자 상세 조회

#### PUT /api/v1/users/{user_id}
사용자 정보 수정

#### DELETE /api/v1/users/{user_id}
사용자 삭제

---

### 3.3 제품 모델 API (Product Models)

#### GET /api/v1/product-models
제품 모델 목록 조회

**Query Parameters**:
- `skip`: int
- `limit`: int
- `is_active`: boolean

#### POST /api/v1/product-models
제품 모델 생성

**Authentication**: Required (ADMIN, MANAGER)

**Request Body**:
```json
{
  "model_code": "NH-1000",
  "model_name": "NeuroHub Pro",
  "description": "Professional model",
  "bom_data": {},
  "specifications": {},
  "is_active": true
}
```

---

### 3.4 공정 관리 API (Process Management)

#### GET /api/v1/processes
공정 목록 조회

**Response**:
```json
[
  {
    "id": 1,
    "process_number": 1,
    "process_code": "P001",
    "process_name_ko": "검사",
    "process_name_en": "Inspection",
    "description": "Initial inspection",
    "estimated_duration_seconds": 300,
    "is_active": true
  }
]
```

#### GET /api/v1/processes/{process_id}
공정 상세 조회

#### POST /api/v1/process/start
착공 등록

**Request Body**:
```json
{
  "lot_number": "WF-KR-251110D-001",
  "serial_number": "WF-KR-251110D-001-0001",
  "process_id": 1,
  "worker_id": "W001",
  "equipment_id": "EQ-001"
}
```

**Validation Rules**:
- 공정 순서 검증: 이전 공정이 PASS 완료되어야 착공 가능
- **공정 7 (라벨 프린팅) 특별 검증**: 공정 1~6 모두 PASS여야 착공 가능

**Error Responses**:
- `400 Bad Request`: 공정 순서 위반
- `400 Bad Request`: 공정 7 착공 시 공정 1~6 PASS 미달
  - Response: `{"detail": "Process 7 requires all previous processes (1-6) to be PASS. Current PASS count: N"}`

#### POST /api/v1/process/complete
완공 등록

**Request Body**:
```json
{
  "lot_number": "WF-KR-251110D-001",
  "serial_number": "WF-KR-251110D-001-0001",
  "process_id": 1,
  "result": "PASS",
  "measurement_data": {
    "temperature": 25.5,
    "humidity": 60
  }
}
```

#### GET /api/v1/process/history/{serial_number}
공정 이력 조회

---

### 3.5 LOT 관리 API (Lot Management)

#### GET /api/v1/lots
LOT 목록 조회

**Query Parameters**:
- `skip`: int
- `limit`: int
- `status`: LotStatus (CREATED, IN_PROGRESS, COMPLETED, CANCELLED)
- `product_model_id`: int

#### POST /api/v1/lots
LOT 생성

**Request Body**:
```json
{
  "lot_number": "LOT-2025-001",
  "product_model_id": 1,
  "target_quantity": 50,
  "work_order": "WO-2025-001"
}
```

#### GET /api/v1/lots/{lot_id}
LOT 상세 조회

#### PUT /api/v1/lots/{lot_number}/status
LOT 상태 변경

---

### 3.6 시리얼 관리 API (Serial Management)

#### GET /api/v1/serials
시리얼 목록 조회

**Query Parameters**:
- `lot_id`: int
- `status`: SerialStatus
- `skip`: int
- `limit`: int

#### POST /api/v1/serials
시리얼 생성

**Request Body**:
```json
{
  "serial_number": "SN-2025-001-001",
  "lot_id": 1,
  "sequence_in_lot": 1
}
```

#### GET /api/v1/serials/{serial_number}
시리얼 상세 조회

#### GET /api/v1/serials/{serial_number}/trace
시리얼 추적성 조회

#### POST /api/v1/serials/{serial_number}/rework
재작업 승인

---

### 3.7 공정 데이터 API (Process Data)

#### GET /api/v1/process-data
공정 실행 기록 조회

**Query Parameters**:
- `lot_id`: int
- `serial_id`: int
- `process_id`: int
- `data_level`: DataLevel (LOT, SERIAL)

#### POST /api/v1/process-data
공정 실행 데이터 기록

**Request Body**:
```json
{
  "lot_id": 1,
  "serial_id": 1,
  "process_id": 1,
  "operator_id": 1,
  "data_level": "SERIAL",
  "measurement_data": {
    "temperature": 25.5,
    "humidity": 60
  },
  "result": "PASS"
}
```

---

### 3.8 라벨 출력 API (Label Printing)

#### POST /api/v1/label/print
라벨 출력 요청

**Request Body**:
```json
{
  "serial_number": "WF-KR-251110D-001-0001",
  "printer_id": "ZEBRA-01",
  "copies": 1
}
```

#### POST /api/v1/label/reprint
라벨 재출력

---

### 3.9 펌웨어 API (Firmware)

#### GET /api/v1/firmware/latest
최신 펌웨어 정보 조회

#### GET /api/v1/firmware/download/{version}
펌웨어 다운로드

---

### 3.10 분석 API (Analytics)

#### GET /api/v1/analytics/overview
생산 개요 메트릭 조회

**Authentication**: Required

**Response**:
```json
{
  "total_lots": 100,
  "active_lots": 25,
  "total_serials": 5000,
  "passed_serials": 4850,
  "failed_serials": 150,
  "pass_rate": 97.0
}
```

#### GET /api/v1/analytics/process-efficiency
공정 효율성 메트릭 조회

#### GET /api/v1/analytics/quality-metrics
품질 관리 메트릭 조회

---

### 3.11 대시보드 API (Dashboard)

#### GET /api/v1/dashboard/summary
금일 생산 현황

#### GET /api/v1/dashboard/lots
LOT별 진행 상태

#### GET /api/v1/dashboard/processes
공정별 현황

---

### 3.12 알림 API (Alerts)

#### GET /api/v1/alerts
알림 목록 조회

#### PUT /api/v1/alerts/{alert_id}/read
알림 읽음 처리

---

### 3.13 감사 로그 API (Audit Logs)

#### GET /api/v1/audit-logs
감사 로그 조회

**Authentication**: Required (ADMIN)

**Query Parameters**:
- `user_id`: int
- `entity_type`: string
- `action`: AuditAction (CREATE, UPDATE, DELETE)
- `start_date`: datetime
- `end_date`: datetime

---

### 3.14 Health Check API

#### GET /api/v1/health
종합 상태 확인 (Database, Redis 연결)

#### GET /api/v1/health/liveness
Liveness Probe (컨테이너 생존 확인)

#### GET /api/v1/health/readiness
Readiness Probe (서비스 준비 상태)

#### GET /api/v1/health/circuit-breakers
Circuit Breaker 상태 확인

---

## 4. 핵심 기능 요구사항

### 4.1 LOT 관리 (FR-LOT)
- **FR-LOT-001**: LOT 생성 및 번호 자동 발급
  - 형식: `{모델코드}-{생산지}-{YYMMDD}{교대}-{순번}`
  - 예: `WF-KR-251110D-001`
- **FR-LOT-002**: LOT 바코드 라벨 출력
- **FR-LOT-003**: LOT 상태 관리
  - CREATED → IN_PROGRESS → COMPLETED → CLOSED

### 4.2 시리얼 번호 관리 (FR-SN)
- **FR-SN-001**: 시리얼 번호 자동 생성
  - 형식: `{LOT번호}-{순번}`
  - 예: `WF-KR-251110D-001-0001`
- **FR-SN-002**: 시리얼 라벨 자동 출력
- **FR-SN-003**: 라벨 재출력 (이력 기록)

### 4.3 공정 관리 (FR-PROC)
- **FR-PROC-001**: 착공 처리
  - LOT 바코드 스캔으로 등록
  - 실시간 검증 (이전 공정 완료 여부)
- **FR-PROC-002**: 완공 처리
  - JSON 파일 기반 File Watcher
  - 공정별 데이터 수집
- **FR-PROC-003**: 공정 순서 제어
  - 직전 공정 PASS 완공 필수
  - 예외: 공정 1(시작), 공정 7(불량품 라벨)

### 4.4 품질 및 불량 관리 (FR-DEFECT)
- **FR-DEFECT-001**: 불량 등록 및 분류
- **FR-DEFECT-002**: 불량 원인 기록 및 분석
- **FR-DEFECT-003**: 불량 상태 관리
  - DEFECTED → REWORK → IN_PROGRESS/SCRAPPED
- **FR-DEFECT-004**: 재작업 프로세스 (최대 3회)

### 4.5 사용자 및 권한 관리 (FR-USER)
- **FR-USER-001**: 사용자 등록 및 관리
  - 역할: Worker, Manager, Admin
- **FR-USER-002**: RBAC (역할 기반 접근 제어)

---

## 5. API 응답 형식

### 5.1 성공 응답
```json
{
  "status": "success",
  "message": "요청이 성공적으로 처리되었습니다",
  "data": { ... }
}
```

### 5.2 에러 응답

#### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

### 5.3 주요 에러 코드

| 에러 코드 | HTTP | 설명 |
|----------|------|------|
| LOT_NOT_FOUND | 404 | LOT 번호 없음 |
| PREVIOUS_PROCESS_NOT_COMPLETED | 400 | 이전 공정 미완료 |
| DUPLICATE_START | 409 | 이미 착공된 공정 |
| INVALID_PROCESS_SEQUENCE | 400 | 잘못된 공정 순서 |
| PROCESS_ALREADY_PASSED | 409 | 이미 PASS 완공됨 |
| PRINTER_NOT_CONNECTED | 503 | 프린터 연결 끊김 |

---

## 6. 인증 및 보안

### 6.1 JWT 인증
- Access Token TTL: 15분
- Refresh Token TTL: 7일
- 세션 유효 시간: 8시간

### 6.2 패스워드 정책
- 최소 길이: 8자
- 복잡도: 대문자, 소문자, 숫자, 특수문자 중 3종 이상
- 로그인 실패 5회 시 계정 잠금 (10분)

### 6.3 통신 보안
- HTTPS 강제 (TLS 1.3)
- SQL Injection 방어 (ORM)
- Rate Limiting: 100 req/min per IP

### 6.4 감사 로그
- 모든 CUD 작업 기록
- 로그인/로그아웃 이력
- 민감 정보 마스킹

---

## 7. 성능 요구사항 (NFR-PERF)

### 7.1 API 응답 시간

| API | P95 목표 |
|-----|---------|
| 착공 API | < 1초 |
| 완공 API | < 2초 |
| 대시보드 초기 로딩 | < 3초 |
| LOT 상세 조회 | < 2초 |

### 7.2 처리량
- 동시 접속자: 100명 (피크 200명)
- 일일 트랜잭션: 50,000건
- TPS: 최소 20 TPS

---

## 8. 안정성 패턴

### 8.1 Circuit Breaker

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def upload_firmware_to_device(serial_number: str, firmware_path: str):
    # 펌웨어 업로드 로직
    pass

@circuit(failure_threshold=3, recovery_timeout=30)
async def print_label(printer_id: str, label_data: dict):
    # 라벨 출력 로직
    pass
```

### 8.2 Health Check

```python
@router.get("/health")
async def health_check():
    # Database, Redis 연결 확인
    # 디스크/메모리 사용률 확인
    # Circuit Breaker 상태 확인
    pass
```

---

## 9. File Watcher 서비스

### 9.1 동작 방식
1. 외부 공정 앱이 JSON 파일 생성
2. 프론트엔드 File Watcher가 `C:\neurohub_work\pending\` 감시
3. 파일 감지 시 HTTP POST로 백엔드 전송
4. 처리 완료: `completed/`, 실패: `error/`로 이동

### 9.2 완공 JSON 스키마

```json
{
  "schema_version": "1.0",
  "lot_number": "WF-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-003",
  "process_name": "센서 검사",
  "equipment_id": "SENSOR-CHECK-01",
  "worker_id": "W001",
  "start_time": "2025-01-10T09:00:00+09:00",
  "complete_time": "2025-01-10T09:15:00+09:00",
  "process_data": { ... }
}
```

### 9.3 파일명 규칙
`{LOT_NUMBER}_{PROCESS_ID}_{TIMESTAMP}.json`

---

## 10. 펌웨어 배포 서비스

### 10.1 동기화 프로세스
1. 착공 시 최신 펌웨어 버전 확인 (폴링: 2초, 최대 5회)
2. 버전 불일치 시 다운로드 (재시도: 3회)
3. 로컬 앱이 MD5 해시 검증 후 업로드

### 10.2 firmware_meta.json
```json
{
  "version": "v1.2.3",
  "filename": "firmware_v1.2.3.bin",
  "file_size": 65536,
  "md5_hash": "5d41402abc4b2a76b9719d911017c592",
  "downloaded_at": "2025-01-10T10:00:15+09:00",
  "status": "READY"
}
```

---

## 11. 알림 서비스

### 11.1 알림 유형

| 유형 코드 | 설명 | 심각도 |
|----------|------|--------|
| DEFECT_DETECTED | 불량 발생 | HIGH |
| TARGET_NOT_MET | 생산 목표 미달 | MEDIUM |
| PROCESS_DELAYED | 공정 지연 | MEDIUM |
| LOT_COMPLETED | LOT 완료 | LOW |
| FIRMWARE_UPDATE | 펌웨어 업데이트 | LOW |

### 11.2 폴링 주기
- 관리자 대시보드: 30초
- 작업자 화면: 60초
- HIGH 알림 발생 시: 10초 (5분간)

---

## 12. API 버전 관리

### 12.1 버전 정책
- 현재: v1 (Phase 1)
- 향후: v2 (Phase 2 AI 기능)
- 이전 버전 최소 1년 유지
- 폐기 6개월 전 사전 공지

### 12.2 하위 호환성 원칙

**허용:**
- 선택적 필드 추가
- 새 API 엔드포인트 추가
- 새 enum 값 추가

**금지 (새 버전 필요):**
- 필수 필드 추가/제거
- 필드 타입/이름 변경
- enum 값 제거

---

## 13. 모니터링 및 로깅

### 13.1 로깅
- 구조화 로깅: structlog (JSON)
- 로그 레벨: INFO (prod), DEBUG (dev)
- 로그 파일: 30일 rotation, 90일 보관

### 13.2 메트릭 수집
- CPU, 메모리, 디스크, 네트워크 (15초 간격)
- API 응답 시간 (P95, P99)
- 에러율

### 13.3 알림 기준
- CPU > 80% (5분 이상)
- 메모리 > 85%
- API 응답 시간 > 500ms (P95)
- 에러율 > 1%

---

## 14. 배포 구성

### 14.1 온프레미스
- Nginx (Load Balancer) → FastAPI (8 Workers)
- PostgreSQL + Redis
- systemd 또는 Docker

### 14.2 Railway
- 자동 배포 (GitHub Push)
- railway.toml 설정
- 환경 변수: Railway Dashboard

### 14.3 AWS
- ALB → EC2 (2대) → RDS + ElastiCache
- Terraform으로 인프라 프로비저닝
- CloudWatch 모니터링

---

## 15. 테스트 요구사항

### 15.1 테스트 유형
- **단위 테스트**: pytest
- **API 테스트**: pytest + httpx
- **부하 테스트**: Locust (20 TPS, 100 동시 사용자)

### 15.2 커버리지
- 목표: 80% 이상
- CI/CD에서 자동 실행

---

## 관련 문서

- [backend/docs/api/API_ENDPOINTS.md](../../backend/docs/api/API_ENDPOINTS.md) - API 엔드포인트 상세
- [03-1-functional.md](../user-specification/03-requirements/03-1-functional.md) - 기능 요구사항
- [03-2-api-specs.md](../user-specification/03-requirements/03-2-api-specs.md) - API 명세
- [04-3-tech-stack.md](../user-specification/04-architecture/04-3-tech-stack.md) - 기술 스택