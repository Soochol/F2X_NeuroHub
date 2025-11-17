# 데이터 사전 (Data Dictionary)

> F2X NeuroHub MES 데이터베이스 전체 컬럼 참조 문서

## 📋 테이블 목록

| 테이블명 | 한글명 | 레코드 수 (예상) | 컬럼 수 | 설명 |
|---------|--------|-----------------|--------|------|
| product_models | 제품 모델 | ~10 | 7 | 제품 유형 마스터 |
| lots | LOT | ~50K/year | 11 | 생산 LOT 관리 |
| serials | 시리얼 번호 | ~5M/year | 10 | 개별 제품 추적 |
| processes | 공정 | 8 (고정) | 8 | 공정 정의 |
| process_data | 공정 데이터 | ~40M/year | 14 | 작업 이력 및 측정 |
| users | 사용자 | ~100 | 12 | 인증 및 권한 |
| audit_logs | 감사 로그 | ~100M/year | 10 | 변경 이력 추적 |
| firmware_versions | 펌웨어 버전 | ~500 | 11 | 펌웨어 관리 |

**총 컬럼 수**: 83

---

## 📖 컬럼 사전 (알파벳 순)

### A

#### audit_logs.action
- **타입**: VARCHAR(20)
- **NULL**: NO
- **설명**: 작업 유형 (INSERT/UPDATE/DELETE)
- **제약**: CHECK (3가지 값)
- **예시**: 'INSERT', 'UPDATE', 'DELETE'

#### audit_logs.created_at
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: NO
- **기본값**: NOW()
- **설명**: 감사 로그 생성 시간
- **인덱스**: idx_audit_time

---

### C

#### lots.closed_at
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: YES
- **설명**: LOT 종료 시간
- **제약**: status = 'CLOSED' 시 설정

#### lots.completed_at
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: YES
- **설명**: LOT 완료 시간
- **제약**: status = 'COMPLETED' 시 자동 설정 (Trigger)

#### lots.created_at
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: NO
- **기본값**: NOW()
- **설명**: LOT 생성 시간
- **인덱스**: idx_lot_created_at

#### lots.created_by
- **타입**: VARCHAR(50)
- **NULL**: YES
- **설명**: LOT 생성자 (사용자 ID)

---

### E

#### process_data.equipment_id
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: 설비 ID (예: LASER-01)
- **인덱스**: idx_process_data_equipment

---

### F

#### firmware_versions.file_path
- **타입**: VARCHAR(500)
- **NULL**: NO
- **설명**: 펌웨어 파일 경로
- **예시**: '/firmware/v1.0.0.bin'

#### firmware_versions.file_size
- **타입**: BIGINT
- **NULL**: NO
- **설명**: 파일 크기 (bytes)
- **예시**: 524288

#### firmware_versions.filename
- **타입**: VARCHAR(255)
- **NULL**: NO
- **설명**: 파일명
- **예시**: 'firmware_v1.0.0.bin'

---

### I

#### product_models.is_active
- **타입**: BOOLEAN
- **NULL**: NO
- **기본값**: TRUE
- **설명**: 활성화 여부 (단종 제품 비활성화)
- **인덱스**: idx_product_models_active (Partial)

#### process_data.is_rework
- **타입**: BOOLEAN
- **NULL**: NO
- **기본값**: FALSE
- **설명**: 재작업 여부
- **인덱스**: idx_process_data_rework (Partial)

#### firmware_versions.is_active
- **타입**: BOOLEAN
- **NULL**: NO
- **기본값**: FALSE
- **설명**: 현재 배포 중인 버전 (1개만 TRUE)
- **인덱스**: idx_firmware_active (Partial)

---

### L

#### process_data.line_id
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: 라인 ID (예: LINE-A)
- **인덱스**: idx_process_data_line

#### lots.lot_number
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: LOT 번호 (예: WF-KR-251110D-001)
- **제약**: UNIQUE
- **인덱스**: idx_lot_number (UNIQUE)
- **포맷**: `{model}-KR-{YYMMDD}{shift}-{sequence}`

---

### M

#### firmware_versions.md5_hash
- **타입**: VARCHAR(32)
- **NULL**: NO
- **설명**: MD5 체크섬 (무결성 검증)
- **예시**: '5d41402abc4b2a76b9719d911017c592'

#### product_models.model_code
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: 제품 모델 코드 (예: WF)
- **제약**: UNIQUE
- **인덱스**: idx_product_models_code (UNIQUE)

#### product_models.model_name
- **타입**: VARCHAR(200)
- **NULL**: NO
- **설명**: 제품 모델 전체 이름
- **예시**: 'Withforce Wearable Robot'

---

### P

#### users.password_hash
- **타입**: VARCHAR(255)
- **NULL**: NO
- **설명**: 비밀번호 해시 (bcrypt)
- **보안**: 평문 저장 금지

#### process_data.process_specific_data
- **타입**: JSONB
- **NULL**: YES
- **설명**: 공정별 측정 데이터 (유연한 구조)
- **인덱스**: idx_process_data_jsonb (GIN)
- **예시**: `{"temp_sensor": {"measured_value": 60.5, "result": "PASS"}}`

#### processes.process_id
- **타입**: VARCHAR(20)
- **NULL**: NO
- **설명**: 공정 ID (예: PROC-001)
- **제약**: UNIQUE
- **인덱스**: idx_process_id (UNIQUE)

#### processes.process_name
- **타입**: VARCHAR(100)
- **NULL**: NO
- **설명**: 공정명 (예: 레이저 마킹)

---

### R

#### process_data.result
- **타입**: VARCHAR(20)
- **NULL**: YES
- **설명**: 공정 결과
- **제약**: CHECK (PASS/FAIL/PENDING)
- **완공 시 필수**

#### serials.rework_count
- **타입**: INTEGER
- **NULL**: NO
- **기본값**: 0
- **설명**: 재작업 횟수
- **제약**: CHECK (0~3)
- **Trigger**: 3회 초과 시 자동 SCRAPPED

#### serials.rework_approved_at
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: YES
- **설명**: 재작업 승인 시간
- **Trigger**: 설정 시 rework_count 자동 증가

#### serials.rework_approved_by
- **타입**: VARCHAR(50)
- **NULL**: YES
- **설명**: 재작업 승인자 (사용자 ID)

#### serials.rework_reason
- **타입**: TEXT
- **NULL**: YES
- **설명**: 재작업 사유

#### users.role
- **타입**: VARCHAR(20)
- **NULL**: NO
- **기본값**: 'WORKER'
- **설명**: 역할 (ADMIN/MANAGER/WORKER/VIEWER)
- **제약**: CHECK (4가지 역할)
- **인덱스**: idx_user_role

---

### S

#### serials.sequence
- **타입**: INTEGER
- **NULL**: NO
- **설명**: LOT 내 순번 (1~200)
- **제약**: CHECK (1~200), UNIQUE(lot_id, sequence)
- **인덱스**: idx_serial_lot_sequence

#### serials.serial_number
- **타입**: VARCHAR(100)
- **NULL**: NO
- **설명**: 시리얼 번호 (예: WF-KR-251110D-001-0001)
- **제약**: UNIQUE
- **인덱스**: idx_serial_number (UNIQUE)
- **포맷**: `{lot_number}-{sequence:04d}`

#### lots.shift
- **타입**: CHAR(1)
- **NULL**: NO
- **설명**: 교대조 (D=주간, N=야간)
- **제약**: CHECK ('D', 'N')

#### lots.status
- **타입**: VARCHAR(20)
- **NULL**: NO
- **기본값**: 'CREATED'
- **설명**: LOT 상태
- **제약**: CHECK (4가지 상태)
- **인덱스**: idx_lot_status
- **전이**: CREATED → IN_PROGRESS → COMPLETED → CLOSED
- **Trigger**: BR-001 (상태 전이 검증)

#### serials.status
- **타입**: VARCHAR(20)
- **NULL**: NO
- **기본값**: 'CREATED'
- **설명**: 시리얼 상태
- **제약**: CHECK (6가지 상태)
- **인덱스**: idx_serial_status
- **전이**: CREATED → IN_PROGRESS → PASSED/FAILED → REWORK → SCRAPPED
- **Trigger**: BR-003 (자동 업데이트)

---

### T

#### lots.target_quantity
- **타입**: INTEGER
- **NULL**: NO
- **기본값**: 100
- **설명**: 목표 수량
- **제약**: CHECK (1~200)
- **Trigger**: BR-004 (초과 방지)

#### firmware_versions.target_mcu
- **타입**: VARCHAR(100)
- **NULL**: YES
- **설명**: 대상 MCU (예: STM32F4)

---

### U

#### lots.updated_at
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: NO
- **기본값**: NOW()
- **설명**: 수정 시간
- **Trigger**: BR-008 (자동 갱신)

#### users.user_id
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: 사용자 ID (로그인용)
- **제약**: UNIQUE
- **인덱스**: idx_user_id (UNIQUE)

#### users.username
- **타입**: VARCHAR(100)
- **NULL**: NO
- **설명**: 사용자명 (한글 가능)
- **예시**: '작업자1', '생산관리자1'

---

### V

#### firmware_versions.version
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: 펌웨어 버전 (Semantic Versioning)
- **제약**: UNIQUE
- **인덱스**: idx_firmware_version (UNIQUE)
- **예시**: 'v1.0.0', 'v1.2.3'

---

### W

#### process_data.worker_id
- **타입**: VARCHAR(50)
- **NULL**: YES
- **설명**: 작업자 ID (사용자 ID)
- **예시**: 'worker01'

---

## 📊 컬럼 통계

### 데이터 타입별 분포

| 데이터 타입 | 컬럼 수 | 비율 |
|-----------|--------|------|
| VARCHAR | 35 | 42% |
| TIMESTAMPTZ | 24 | 29% |
| BIGINT | 10 | 12% |
| INTEGER | 7 | 8% |
| BOOLEAN | 5 | 6% |
| JSONB | 2 | 2% |

### NULL 허용 여부

| NULL 허용 | 컬럼 수 | 비율 |
|---------|--------|------|
| NOT NULL | 58 | 70% |
| NULL | 25 | 30% |

### 제약조건 통계

| 제약조건 | 개수 |
|---------|------|
| PRIMARY KEY | 8 |
| FOREIGN KEY | 5 |
| UNIQUE | 12 |
| CHECK | 15 |
| Trigger | 8 |

---

## 🔍 자주 사용되는 컬럼

### 1. 시간 관련 컬럼

| 테이블 | 컬럼 | 용도 | 인덱스 |
|--------|------|------|--------|
| lots | created_at | LOT 생성 시간 | ✅ |
| lots | completed_at | LOT 완료 시간 | - |
| serials | created_at | 시리얼 생성 시간 | - |
| process_data | start_time | 공정 착공 시간 | ✅ |
| process_data | complete_time | 공정 완공 시간 | ✅ |
| audit_logs | created_at | 로그 생성 시간 | ✅ |

### 2. 상태 컬럼

| 테이블 | 컬럼 | 값 | 인덱스 |
|--------|------|------|--------|
| lots | status | CREATED, IN_PROGRESS, COMPLETED, CLOSED | ✅ |
| serials | status | CREATED, IN_PROGRESS, PASSED, FAILED, REWORK, SCRAPPED | ✅ |
| process_data | result | PASS, FAIL, PENDING | - |

### 3. 식별자 컬럼

| 테이블 | 컬럼 | 예시 | 인덱스 |
|--------|------|------|--------|
| lots | lot_number | WF-KR-251110D-001 | ✅ UNIQUE |
| serials | serial_number | WF-KR-251110D-001-0001 | ✅ UNIQUE |
| processes | process_id | PROC-001 | ✅ UNIQUE |
| users | user_id | worker01 | ✅ UNIQUE |

---

## 📚 관련 문서

- [02-entity-definitions.md](02-entity-definitions.md) - 테이블 상세 정의
- [03-relationship-specs.md](03-relationship-specs.md) - FK 관계
- [04-business-rules.md](04-business-rules.md) - Trigger/Function

---

**마지막 업데이트**: 2025-01-17
