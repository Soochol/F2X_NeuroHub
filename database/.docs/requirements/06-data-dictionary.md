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
| wip_items | WIP 항목 | ~100K/year | 10 | 공정 1-6 중 제품 추적 ⭐ **NEW** |
| wip_process_history | WIP 공정 이력 | ~600K/year | 12 | WIP 각 공정 단계별 이력 ⭐ **NEW** |
| users | 사용자 | ~100 | 12 | 인증 및 권한 |
| audit_logs | 감사 로그 | ~100M/year | 10 | 변경 이력 추적 |
| firmware_versions | 펌웨어 버전 | ~500 | 11 | 펌웨어 관리 |

**총 컬럼 수**: 107 (WIP 추가로 +24)

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

#### wip_items.completed_at ⭐ **NEW**
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: YES
- **설명**: WIP 항목 완료 시간 (모든 공정 1-6 통과)
- **Trigger**: 마지막 공정 통과 시 자동 설정
- **인덱스**: idx_wip_items_completed_at (Partial)

#### wip_items.converted_at ⭐ **NEW**
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: YES
- **설명**: WIP를 시리얼로 변환한 시간
- **Trigger**: 공정 7 완료 시 자동 설정

#### wip_process_history.completed_at ⭐ **NEW**
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: NO
- **설명**: WIP 공정 완료 시간
- **제약**: started_at보다 이후여야 함

#### wip_process_history.created_at ⭐ **NEW**
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: NO
- **기본값**: NOW()
- **설명**: WIP 공정 이력 레코드 생성 시간
- **인덱스**: idx_wip_process_history_composite의 일부

---

### D

#### wip_process_history.defects ⭐ **NEW**
- **타입**: JSON
- **NULL**: NO
- **기본값**: '[]'
- **설명**: 불량 항목 리스트 (FAIL 결과일 때)
- **예시**: `[{"code": "D001", "description": "Surface scratch"}]`

#### wip_process_history.duration_seconds ⭐ **NEW**
- **타입**: INTEGER
- **NULL**: NO
- **설명**: 공정 소요 시간 (초)
- **계산**: completed_at - started_at
- **예시**: 3600

---

### E

#### process_data.equipment_id
- **타입**: BIGINT
- **NULL**: YES
- **설명**: 설비 FK (equipment 테이블 참조)
- **인덱스**: idx_process_data_equipment
- **참조**: FK → equipment(id)
- **비고**: 착공 시 설비 코드(예: LASER-001)를 ID로 변환하여 저장

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
- **설명**: 라인 ID (예: KR01) - 생산라인 코드 (국가코드 2자리 + 라인번호 2자리)
- **인덱스**: idx_process_data_line

#### lots.lot_number
- **타입**: VARCHAR(50)
- **NULL**: NO
- **설명**: LOT 번호 (예: KR01PSA2511001)
- **제약**: UNIQUE
- **인덱스**: idx_lot_number (UNIQUE)
- **포맷**: `{line}{model}{YYMM}{sequence}` (14자리)

#### lots.production_line_id
- **타입**: BIGINT
- **NULL**: YES
- **설명**: 생산 라인 FK (첫 착공 시 자동 할당)
- **참조**: FK → production_lines(id)
- **비고**: 첫 공정 착공 시 line_id 파라미터 기반으로 할당

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

#### wip_process_history.measurements ⭐ **NEW**
- **타입**: JSON
- **NULL**: NO
- **기본값**: '{}'
- **설명**: 공정 측정값 (온도, 시간, 전압 등 유연한 구조)
- **인덱스**: 부분 검색 시 GIN 인덱스 사용 가능
- **예시**: `{"temp": 60.5, "duration": 120, "voltage": 48.2}`

---

### N

#### wip_process_history.notes ⭐ **NEW**
- **타입**: TEXT
- **NULL**: YES
- **설명**: WIP 공정 완료 시 추가 메모
- **예시**: 'Sensor recalibration required before next process'

---

### O

#### wip_process_history.operator_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: NO
- **설명**: 작업자 FK (users 테이블 참조)
- **참조**: FK → users(id) RESTRICT
- **인덱스**: idx_wip_process_history_operator

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

#### wip_process_history.result ⭐ **NEW**
- **타입**: VARCHAR(20)
- **NULL**: NO
- **설명**: WIP 공정 결과
- **제약**: CHECK (PASS/FAIL/REWORK)
- **인덱스**: idx_wip_process_history_composite의 일부 (검색용)
- **비즈니스 규칙**: BR-004 (중복 PASS 방지), BR-003 (순서 검증)

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
- **설명**: 시리얼 번호 (예: KR01PSA25110010001)
- **제약**: UNIQUE
- **인덱스**: idx_serial_number (UNIQUE)
- **포맷**: `{lot_number}{sequence:04d}` (18자리)

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

#### wip_items.sequence_in_lot ⭐ **NEW**
- **타입**: INTEGER
- **NULL**: NO
- **설명**: LOT 내 WIP 항목 순번 (1~100)
- **제약**: CHECK (1~100)
- **관계**: serials.sequence와 일치 (WIP → Serial 변환 시)

#### wip_items.status ⭐ **NEW**
- **타입**: VARCHAR(20)
- **NULL**: NO
- **기본값**: 'CREATED'
- **설명**: WIP 상태
- **제약**: CHECK ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CONVERTED')
- **인덱스**: idx_wip_items_status
- **전이**: CREATED → IN_PROGRESS → COMPLETED/FAILED → CONVERTED
- **비즈니스 규칙**: 공정 1-6 모두 PASS 시 COMPLETED

#### wip_items.serial_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: YES
- **설명**: 시리얼 FK (serials 테이블 참조)
- **참조**: FK → serials(id) SET NULL
- **인덱스**: idx_wip_items_serial
- **비고**: WIP → Serial 변환 시 설정

#### wip_items.status ⭐ **NEW** (Status Transitions)
- **상태도**:
  - CREATED: 생성 직후
  - IN_PROGRESS: 첫 공정 시작
  - COMPLETED: 공정 1-6 모두 PASS
  - FAILED: 공정 중 FAIL 발생
  - CONVERTED: 시리얼로 변환 완료

#### wip_process_history.started_at ⭐ **NEW**
- **타입**: TIMESTAMP WITH TIME ZONE
- **NULL**: NO
- **설명**: WIP 공정 시작 시간
- **비즈니스 규칙**: BR-003 (이전 공정이 PASS여야만 시작 가능)

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

#### wip_items.wip_id ⭐ **NEW**
- **타입**: VARCHAR(19)
- **NULL**: NO
- **설명**: WIP 고유 ID
- **제약**: UNIQUE
- **인덱스**: idx_wip_items_wip_id
- **포맷**: `WIP-{LOT 11}-{SEQ 3}` (19자리)
- **예시**: 'WIP-KR01PSA2511-001'
- **비즈니스 규칙**: BR-001 (LOT 당 최대 100개)

#### wip_items.lot_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: NO
- **설명**: LOT FK (lots 테이블 참조)
- **참조**: FK → lots(id) CASCADE
- **인덱스**: idx_wip_items_lot
- **관계**: 1 LOT = 1~100 WIP items

#### wip_items.current_process_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: YES
- **설명**: 현재 진행 중인 공정 FK (processes 테이블 참조)
- **참조**: FK → processes(id) SET NULL
- **인덱스**: idx_wip_items_current_process
- **비고**: 공정 시작 시 설정, 완료 시 NULL로 변경

#### wip_process_history.wip_item_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: NO
- **설명**: WIP 항목 FK (wip_items 테이블 참조)
- **참조**: FK → wip_items(id) CASCADE
- **인덱스**: idx_wip_process_history_wip_item
- **관계**: 1 WIP = 1~6 process history records

#### wip_process_history.process_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: NO
- **설명**: 공정 FK (processes 테이블 참조)
- **참조**: FK → processes(id) RESTRICT
- **인덱스**: idx_wip_process_history_process
- **제약**: 공정 1-6만 허용 (공정 7은 serial 변환)

#### wip_process_history.equipment_id ⭐ **NEW**
- **타입**: BIGINT
- **NULL**: YES
- **설명**: 설비 FK (equipment 테이블 참조)
- **참조**: FK → equipment(id) SET NULL
- **비고**: 일부 공정에서만 필수

---

## 📊 컬럼 통계

### 데이터 타입별 분포

| 데이터 타입 | 컬럼 수 | 비율 |
|-----------|--------|------|
| VARCHAR | 38 | 35% |
| TIMESTAMPTZ | 31 | 29% |
| BIGINT | 14 | 13% |
| INTEGER | 9 | 8% |
| BOOLEAN | 5 | 5% |
| JSON | 4 | 4% |
| TEXT | 6 | 6% |

### NULL 허용 여부

| NULL 허용 | 컬럼 수 | 비율 |
|---------|--------|------|
| NOT NULL | 76 | 71% |
| NULL | 31 | 29% |

### 제약조건 통계

| 제약조건 | 개수 |
|---------|------|
| PRIMARY KEY | 10 |
| FOREIGN KEY | 9 |
| UNIQUE | 14 |
| CHECK | 20 |
| Trigger | 12 |

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
| wip_items | completed_at | WIP 완료 시간 | ✅ (Partial) |
| wip_items | converted_at | Serial 변환 시간 | - |
| wip_process_history | started_at | WIP 공정 시작 시간 | ✅ (Composite) |
| wip_process_history | completed_at | WIP 공정 완료 시간 | ✅ (Composite) |
| audit_logs | created_at | 로그 생성 시간 | ✅ |

### 2. 상태 컬럼

| 테이블 | 컬럼 | 값 | 인덱스 |
|--------|------|------|--------|
| lots | status | CREATED, IN_PROGRESS, COMPLETED, CLOSED | ✅ |
| serials | status | CREATED, IN_PROGRESS, PASSED, FAILED, REWORK, SCRAPPED | ✅ |
| wip_items | status | CREATED, IN_PROGRESS, COMPLETED, FAILED, CONVERTED | ✅ |
| process_data | result | PASS, FAIL, PENDING | - |
| wip_process_history | result | PASS, FAIL, REWORK | ✅ (Composite) |

### 3. 식별자 컬럼

| 테이블 | 컬럼 | 예시 | 인덱스 |
|--------|------|------|--------|
| lots | lot_number | KR01PSA2511001 | ✅ UNIQUE |
| serials | serial_number | KR01PSA25110010001 | ✅ UNIQUE |
| processes | process_id | PROC-001 | ✅ UNIQUE |
| users | user_id | worker01 | ✅ UNIQUE |
| wip_items | wip_id | WIP-KR01PSA2511-001 | ✅ UNIQUE |

---

## 📚 관련 문서

- [README.md](./README.md) - 문서 가이드
- [DATABASE-REQUIREMENTS.md](./DATABASE-REQUIREMENTS.md) - 통합 데이터베이스 요구사항
- [02-entity-definitions.md](./02-entity-definitions.md) - 테이블 상세 정의
- [04-index-strategy.md](./04-index-strategy.md) - 인덱스 및 성능 최적화
- [05-migration-plan.md](./05-migration-plan.md) - Alembic 마이그레이션 계획

---

**마지막 업데이트**: 2025-11-21
