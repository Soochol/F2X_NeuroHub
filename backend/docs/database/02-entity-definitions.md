# 엔티티 정의서 (Entity Definitions)

> F2X NeuroHub MES 데이터베이스 테이블 상세 정의

## 📋 테이블 목록

| 테이블명 | 한글명 | 목적 | 레코드 수 (예상) | 우선순위 |
|---------|--------|------|-----------------|---------|
| [product_models](#1-product_models-제품-모델) | 제품 모델 | 제품 유형 마스터 | ~10 | P0 |
| [lots](#2-lots-lot-관리) | LOT | 생산 LOT 관리 | ~50K/year | P0 |
| [serials](#3-serials-시리얼-번호) | 시리얼 번호 | 개별 제품 추적 | ~5M/year | P0 |
| [processes](#4-processes-공정) | 공정 | 공정 정의 | 8 (고정) | P0 |
| [process_data](#5-process_data-공정-데이터) | 공정 데이터 | 작업 이력 및 측정 | ~40M/year | P0 |
| [users](#6-users-사용자) | 사용자 | 인증 및 권한 | ~100 | P1 |
| [audit_logs](#7-audit_logs-감사-로그) | 감사 로그 | 변경 이력 추적 | ~100M/year | P1 |
| [firmware_versions](#8-firmware_versions-펌웨어-버전) | 펌웨어 버전 | 펌웨어 관리 | ~500 | P2 |

---

## 1. product_models (제품 모델)

### 목적
제품 모델 마스터 데이터 관리. Withforce 웨어러블 로봇의 제품 유형을 정의.

### 비즈니스 규칙
- 제품 단종 시 `is_active = FALSE` 처리 (DELETE 금지)
- `model_code`는 2~5자 대문자 (예: WF, AG)
- 한 모델은 여러 LOT 생성 가능 (1:N)

### DDL

```sql
CREATE TABLE product_models (
    id BIGSERIAL PRIMARY KEY,
    model_code VARCHAR(50) UNIQUE NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE product_models IS '제품 모델 마스터 테이블';
COMMENT ON COLUMN product_models.model_code IS '제품 모델 코드 (예: WF=Withforce)';
COMMENT ON COLUMN product_models.model_name IS '제품 모델 전체 이름';
COMMENT ON COLUMN product_models.is_active IS '활성화 여부 (단종 제품 비활성화)';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK (자동 증가) | PRIMARY KEY |
| **model_code** | VARCHAR(50) | NO | - | 모델 코드 (예: WF) | UNIQUE, NOT NULL |
| **model_name** | VARCHAR(200) | NO | - | 모델명 (예: Withforce Wearable Robot) | NOT NULL |
| **description** | TEXT | YES | NULL | 제품 설명 | - |
| **is_active** | BOOLEAN | NO | TRUE | 활성화 여부 | NOT NULL |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |
| **updated_at** | TIMESTAMPTZ | NO | NOW() | 수정 시간 | Trigger 자동 갱신 |

### 인덱스

```sql
-- PRIMARY KEY (자동 생성)
CREATE UNIQUE INDEX pk_product_models ON product_models(id);

-- UNIQUE INDEX (model_code 중복 방지)
CREATE UNIQUE INDEX idx_product_models_code ON product_models(model_code);

-- PARTIAL INDEX (활성화된 모델만 조회)
CREATE INDEX idx_product_models_active ON product_models(is_active)
WHERE is_active = TRUE;
```

### 예상 데이터량
- **초기**: 1~2 rows (WF 모델)
- **3년 후**: ~5 rows
- **5년 후**: ~10 rows (신제품 라인 확장)

### 샘플 데이터

```sql
INSERT INTO product_models (model_code, model_name, description) VALUES
('WF', 'Withforce Wearable Robot', '산업용/농업용 허리 보조 로봇'),
('AG', 'Agriculture Robot', '농업용 특화 모델 (미래 확장)');
```

### 사용 예시

```sql
-- 활성화된 제품 모델 조회
SELECT * FROM product_models WHERE is_active = TRUE;

-- 특정 모델 코드로 조회
SELECT * FROM product_models WHERE model_code = 'WF';

-- 제품 단종 처리 (DELETE 금지, is_active = FALSE)
UPDATE product_models SET is_active = FALSE WHERE model_code = 'OLD_MODEL';
```

---

## 2. lots (LOT 관리)

### 목적
생산 LOT 단위 관리. 100대/LOT 기준으로 생산 진행 상황 추적.

### 비즈니스 규칙
- **LOT 번호 포맷**: `{model}-KR-{YYMMDD}{shift}-{sequence}`
  - 예: `WF-KR-251110D-001` (Withforce, 한국, 2025년 11월 10일, 주간, 1번째 LOT)
- **상태 전이**: `CREATED → IN_PROGRESS → COMPLETED → CLOSED` (Trigger 검증)
- **목표 수량**: 기본 100, 최대 200
- **첫 시리얼 생성 시**: LOT 상태 자동 `IN_PROGRESS` 전환 (Trigger)
- **모든 시리얼 완료 시**: `COMPLETED` 가능 (Trigger 검증)

### DDL

```sql
CREATE TABLE lots (
    id BIGSERIAL PRIMARY KEY,
    lot_number VARCHAR(50) UNIQUE NOT NULL,
    product_model_id BIGINT NOT NULL REFERENCES product_models(id) ON DELETE RESTRICT,
    target_quantity INTEGER DEFAULT 100 NOT NULL CHECK (target_quantity > 0 AND target_quantity <= 200),
    shift CHAR(1) NOT NULL CHECK (shift IN ('D', 'N')),
    status VARCHAR(20) DEFAULT 'CREATED' NOT NULL CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(50),
    CONSTRAINT chk_lot_status_timestamps CHECK (
        (status = 'COMPLETED' AND completed_at IS NOT NULL) OR
        (status != 'COMPLETED' AND completed_at IS NULL)
    )
);

COMMENT ON TABLE lots IS 'LOT 관리 테이블 (LOT 단위: 100대)';
COMMENT ON COLUMN lots.lot_number IS 'LOT 번호 (예: WF-KR-251110D-001)';
COMMENT ON COLUMN lots.shift IS '교대조 (D=주간, N=야간)';
COMMENT ON COLUMN lots.status IS 'LOT 상태 (CREATED → IN_PROGRESS → COMPLETED → CLOSED)';
COMMENT ON COLUMN lots.completed_at IS 'COMPLETED 상태일 때 자동 설정 (Trigger)';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **lot_number** | VARCHAR(50) | NO | - | LOT 번호 | UNIQUE, NOT NULL |
| **product_model_id** | BIGINT | NO | - | 제품 모델 FK | FK → product_models(id) |
| **target_quantity** | INTEGER | NO | 100 | 목표 수량 | CHECK (1~200) |
| **shift** | CHAR(1) | NO | - | 교대조 (D/N) | CHECK ('D', 'N') |
| **status** | VARCHAR(20) | NO | 'CREATED' | 상태 | CHECK (4가지 상태) |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |
| **updated_at** | TIMESTAMPTZ | NO | NOW() | 수정 시간 | Trigger 자동 갱신 |
| **completed_at** | TIMESTAMPTZ | YES | NULL | 완료 시간 | CHECK (COMPLETED 시 필수) |
| **closed_at** | TIMESTAMPTZ | YES | NULL | 종료 시간 | - |
| **created_by** | VARCHAR(50) | YES | NULL | 생성자 | - |

### 상태 전이 규칙

```
CREATED ──→ IN_PROGRESS ──→ COMPLETED ──→ CLOSED
   ↑                              ↓
   └──────────── (재오픈) ─────────┘
```

| 전이 | 조건 | 액션 | Trigger |
|------|------|------|---------|
| CREATED → IN_PROGRESS | 첫 시리얼 생성 | `updated_at = NOW()` | BR-007 |
| IN_PROGRESS → COMPLETED | 모든 시리얼 완료 | `completed_at = NOW()` | BR-001 |
| COMPLETED → CLOSED | 관리자 승인 | `closed_at = NOW()` | BR-001 |

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_lots ON lots(id);

-- UNIQUE INDEX (LOT 번호 중복 방지)
CREATE UNIQUE INDEX idx_lot_number ON lots(lot_number);

-- INDEX (상태별 조회)
CREATE INDEX idx_lot_status ON lots(status);

-- INDEX (생성 시간 역순 조회)
CREATE INDEX idx_lot_created_at ON lots(created_at DESC);

-- INDEX (제품 모델별 LOT 조회)
CREATE INDEX idx_lot_product_model ON lots(product_model_id);

-- COMPOSITE INDEX (상태 + 생성 시간)
CREATE INDEX idx_lot_status_created ON lots(status, created_at DESC);
```

### 예상 데이터량
- **연간**: ~50,000 LOT
- **3년 후**: ~150,000 LOT
- **5년 후**: ~250,000 LOT

### 샘플 데이터

```sql
INSERT INTO lots (lot_number, product_model_id, target_quantity, shift, created_by) VALUES
('WF-KR-251110D-001', 1, 100, 'D', 'manager01'),
('WF-KR-251110D-002', 1, 100, 'D', 'manager01'),
('WF-KR-251110N-001', 1, 100, 'N', 'manager02');
```

### 사용 예시

```sql
-- 진행 중인 LOT 조회
SELECT * FROM lots WHERE status = 'IN_PROGRESS' ORDER BY created_at DESC;

-- 오늘 생성된 LOT 조회
SELECT * FROM lots WHERE created_at >= CURRENT_DATE;

-- LOT 상태 전환
UPDATE lots SET status = 'COMPLETED' WHERE lot_number = 'WF-KR-251110D-001';
-- → Trigger 검증: 모든 시리얼 완료 확인
```

---

## 3. serials (시리얼 번호)

### 목적
개별 제품 추적 및 상태 관리. LOT 내 각 제품의 공정 진행 상황 및 불량/재작업 이력 추적.

### 비즈니스 규칙
- **시리얼 번호 포맷**: `{lot_number}-{sequence:04d}`
  - 예: `WF-KR-251110D-001-0001` (LOT 001의 1번째 제품)
- **상태 전이**: `CREATED → IN_PROGRESS → PASSED/FAILED → REWORK → SCRAPPED`
- **재작업 제한**: 최대 3회, 초과 시 자동 `SCRAPPED` (Trigger)
- **LOT당 시리얼 수**: `target_quantity` 초과 불가 (Trigger 검증)
- **LOT 내 순번 고유성**: `UNIQUE(lot_id, sequence)`

### DDL

```sql
CREATE TABLE serials (
    id BIGSERIAL PRIMARY KEY,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    lot_id BIGINT NOT NULL REFERENCES lots(id) ON DELETE RESTRICT,
    sequence INTEGER NOT NULL CHECK (sequence > 0 AND sequence <= 200),
    status VARCHAR(20) DEFAULT 'CREATED' NOT NULL CHECK (status IN ('CREATED', 'IN_PROGRESS', 'PASSED', 'FAILED', 'REWORK', 'SCRAPPED')),
    rework_count INTEGER DEFAULT 0 NOT NULL CHECK (rework_count >= 0 AND rework_count <= 3),
    rework_approved_by VARCHAR(50),
    rework_approved_at TIMESTAMP WITH TIME ZONE,
    rework_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE(lot_id, sequence)
);

COMMENT ON TABLE serials IS '시리얼 번호 관리 테이블 (제품 개체 추적)';
COMMENT ON COLUMN serials.serial_number IS '시리얼 번호 (예: WF-KR-251110D-001-0001)';
COMMENT ON COLUMN serials.sequence IS 'LOT 내 순번 (1~100)';
COMMENT ON COLUMN serials.status IS '제품 상태 (CREATED → IN_PROGRESS → PASSED/FAILED)';
COMMENT ON COLUMN serials.rework_count IS '재작업 횟수 (최대 3회)';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **serial_number** | VARCHAR(100) | NO | - | 시리얼 번호 | UNIQUE, NOT NULL |
| **lot_id** | BIGINT | NO | - | LOT FK | FK → lots(id) |
| **sequence** | INTEGER | NO | - | LOT 내 순번 (1~200) | CHECK (1~200) |
| **status** | VARCHAR(20) | NO | 'CREATED' | 제품 상태 | CHECK (6가지 상태) |
| **rework_count** | INTEGER | NO | 0 | 재작업 횟수 (0~3) | CHECK (0~3) |
| **rework_approved_by** | VARCHAR(50) | YES | NULL | 재작업 승인자 | - |
| **rework_approved_at** | TIMESTAMPTZ | YES | NULL | 재작업 승인 시간 | - |
| **rework_reason** | TEXT | YES | NULL | 재작업 사유 | - |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |
| **updated_at** | TIMESTAMPTZ | NO | NOW() | 수정 시간 | Trigger 자동 갱신 |

### 상태 전이 규칙

```
CREATED ──→ IN_PROGRESS ──→ PASSED (최종 합격)
                │
                ├──→ FAILED ──→ REWORK (재작업 승인)
                │                 │
                │                 └──→ IN_PROGRESS (재작업 시작)
                │
                └──→ FAILED ──→ SCRAPPED (재작업 3회 초과)
```

| 상태 | 의미 | 전이 조건 | Trigger |
|------|------|----------|---------|
| CREATED | 시리얼 생성 | 초기 상태 | - |
| IN_PROGRESS | 공정 진행 중 | 첫 공정 착공 | BR-003 |
| PASSED | 전체 공정 합격 | 마지막 공정 PASS | BR-003 |
| FAILED | 불합격 | 공정 FAIL | BR-003 |
| REWORK | 재작업 승인 | 관리자 승인 | BR-005 |
| SCRAPPED | 폐기 처리 | rework_count > 3 | BR-005 |

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_serials ON serials(id);

-- UNIQUE INDEX (시리얼 번호 중복 방지)
CREATE UNIQUE INDEX idx_serial_number ON serials(serial_number);

-- INDEX (LOT별 시리얼 조회)
CREATE INDEX idx_serial_lot ON serials(lot_id);

-- INDEX (상태별 조회)
CREATE INDEX idx_serial_status ON serials(status);

-- COMPOSITE INDEX (LOT + 순번)
CREATE INDEX idx_serial_lot_sequence ON serials(lot_id, sequence);

-- PARTIAL INDEX (불량품 조회 최적화)
CREATE INDEX idx_serial_failed ON serials(lot_id, status) WHERE status = 'FAILED';

-- PARTIAL INDEX (재작업 중인 제품 조회)
CREATE INDEX idx_serial_rework ON serials(status) WHERE status = 'REWORK';
```

### 예상 데이터량
- **연간**: ~5,000,000 serials
- **3년 후**: ~15,000,000 serials
- **5년 후**: ~25,000,000 serials

### 샘플 데이터

```sql
INSERT INTO serials (serial_number, lot_id, sequence) VALUES
('WF-KR-251110D-001-0001', 1, 1),
('WF-KR-251110D-001-0002', 1, 2),
('WF-KR-251110D-001-0003', 1, 3);
```

### 사용 예시

```sql
-- LOT의 모든 시리얼 조회
SELECT * FROM serials WHERE lot_id = 1 ORDER BY sequence;

-- 불량품 조회
SELECT * FROM serials WHERE status = 'FAILED';

-- 재작업 승인
UPDATE serials
SET rework_approved_at = NOW(), rework_approved_by = 'manager01', rework_reason = '센서 불량 재검사'
WHERE serial_number = 'WF-KR-251110D-001-0001';
-- → Trigger: rework_count 자동 증가
```

---

## 4. processes (공정)

### 목적
공정 마스터 데이터. 8개 제조 공정 정의 및 순서 관리.

### 비즈니스 규칙
- **공정 수**: 8개 고정 (변경 없음)
- **순서**: `sequence_order` 1~8 (공정 순서 제어에 사용)
- **공정 ID 포맷**: `PROC-{sequence:03d}` (예: PROC-001)

### DDL

```sql
CREATE TABLE processes (
    id BIGSERIAL PRIMARY KEY,
    process_id VARCHAR(20) UNIQUE NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    sequence_order INTEGER UNIQUE NOT NULL,
    description TEXT,
    estimated_duration_seconds INTEGER,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE processes IS '공정 마스터 테이블 (8개 공정 고정)';
COMMENT ON COLUMN processes.process_id IS '공정 ID (예: PROC-001)';
COMMENT ON COLUMN processes.sequence_order IS '공정 순서 (1~8)';
COMMENT ON COLUMN processes.estimated_duration_seconds IS '예상 소요 시간 (초)';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **process_id** | VARCHAR(20) | NO | - | 공정 ID | UNIQUE, NOT NULL |
| **process_name** | VARCHAR(100) | NO | - | 공정명 | NOT NULL |
| **sequence_order** | INTEGER | NO | - | 공정 순서 (1~8) | UNIQUE, NOT NULL |
| **description** | TEXT | YES | NULL | 공정 설명 | - |
| **estimated_duration_seconds** | INTEGER | YES | NULL | 예상 소요 시간 (초) | - |
| **is_active** | BOOLEAN | NO | TRUE | 활성화 여부 | NOT NULL |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |
| **updated_at** | TIMESTAMPTZ | NO | NOW() | 수정 시간 | Trigger 자동 갱신 |

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_processes ON processes(id);

-- UNIQUE INDEX (공정 ID 중복 방지)
CREATE UNIQUE INDEX idx_process_id ON processes(process_id);

-- UNIQUE INDEX (순서 중복 방지)
CREATE UNIQUE INDEX idx_process_sequence ON processes(sequence_order);

-- PARTIAL INDEX (활성화된 공정만 조회)
CREATE INDEX idx_process_active ON processes(is_active) WHERE is_active = TRUE;
```

### 예상 데이터량
- **고정**: 8 rows (변경 없음)

### 초기 데이터 (Seed Data)

```sql
INSERT INTO processes (process_id, process_name, sequence_order, estimated_duration_seconds, description) VALUES
('PROC-001', '레이저 마킹', 1, 60, 'LMA 케이스에 시리얼 번호 레이저 마킹'),
('PROC-002', 'LMA 조립', 2, 3600, 'SMA 스프링, 모선, 링크 조립'),
('PROC-003', '센서 검사', 3, 60, '온도 센서, TOF 센서 자동 검사'),
('PROC-004', '펌웨어 업로드', 4, 60, '제어 보드에 최신 펌웨어 업로드'),
('PROC-005', '로봇 조립', 5, 3600, '하우징, 벨트, 배터리 최종 조립'),
('PROC-006', '성능검사', 6, 600, '온도/변위/힘 자동 측정 및 판정'),
('PROC-007', '라벨 프린팅', 7, 40, 'Zebra 프린터로 라벨 출력 및 부착'),
('PROC-008', '포장+외관검사', 8, 120, '외관 검사 및 박스 포장');
```

### 사용 예시

```sql
-- 공정 순서대로 조회
SELECT * FROM processes ORDER BY sequence_order;

-- 특정 공정 조회
SELECT * FROM processes WHERE process_id = 'PROC-003';

-- 다음 공정 조회
SELECT * FROM processes
WHERE sequence_order = (SELECT sequence_order + 1 FROM processes WHERE process_id = 'PROC-003');
```

---

## 5. process_data (공정 데이터)

### 목적
공정별 작업 이력 및 측정 데이터 저장. LOT/시리얼별 모든 공정의 착공/완공 시간, 작업자, 측정값 추적.

### 비즈니스 규칙
- **serial_id NULL 허용**: 공정 1~6은 시리얼 미발급 상태 (LOT 단위 작업)
- **JSONB process_specific_data**: 공정별 유연한 측정 데이터 저장
- **공정 순서 제어**: 이전 공정 PASS 완료 확인 (Trigger BR-002)
- **시리얼 상태 자동 업데이트**: 완공 시 시리얼 상태 자동 전환 (Trigger BR-003)

### DDL

```sql
CREATE TABLE process_data (
    id BIGSERIAL PRIMARY KEY,
    lot_id BIGINT NOT NULL REFERENCES lots(id) ON DELETE RESTRICT,
    serial_id BIGINT REFERENCES serials(id) ON DELETE RESTRICT,
    process_id BIGINT NOT NULL REFERENCES processes(id) ON DELETE RESTRICT,
    line_id VARCHAR(50) NOT NULL,
    equipment_id VARCHAR(50) NOT NULL,
    worker_id VARCHAR(50),
    process_specific_data JSONB,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    complete_time TIMESTAMP WITH TIME ZONE,
    result VARCHAR(20) CHECK (result IN ('PASS', 'FAIL', 'PENDING')),
    is_rework BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT chk_process_data_completion CHECK (
        (complete_time IS NOT NULL AND result IS NOT NULL) OR
        (complete_time IS NULL AND result IS NULL)
    )
);

COMMENT ON TABLE process_data IS '공정 작업 데이터 테이블 (작업 이력 + 측정 데이터)';
COMMENT ON COLUMN process_data.serial_id IS '시리얼 FK (NULL 허용: 공정 1~6은 시리얼 미발급)';
COMMENT ON COLUMN process_data.process_specific_data IS '공정별 측정 데이터 (JSONB)';
COMMENT ON COLUMN process_data.result IS '공정 결과 (PASS/FAIL/PENDING)';
COMMENT ON COLUMN process_data.is_rework IS '재작업 여부';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **lot_id** | BIGINT | NO | - | LOT FK | FK → lots(id) |
| **serial_id** | BIGINT | YES | NULL | 시리얼 FK (NULL 허용) | FK → serials(id) |
| **process_id** | BIGINT | NO | - | 공정 FK | FK → processes(id) |
| **line_id** | VARCHAR(50) | NO | - | 라인 ID | NOT NULL |
| **equipment_id** | VARCHAR(50) | NO | - | 설비 ID | NOT NULL |
| **worker_id** | VARCHAR(50) | YES | NULL | 작업자 ID | - |
| **process_specific_data** | JSONB | YES | NULL | 공정별 측정 데이터 | - |
| **start_time** | TIMESTAMPTZ | NO | - | 착공 시간 | NOT NULL |
| **complete_time** | TIMESTAMPTZ | YES | NULL | 완공 시간 | - |
| **result** | VARCHAR(20) | YES | NULL | 공정 결과 | CHECK (PASS/FAIL/PENDING) |
| **is_rework** | BOOLEAN | NO | FALSE | 재작업 여부 | NOT NULL |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |
| **updated_at** | TIMESTAMPTZ | NO | NOW() | 수정 시간 | Trigger 자동 갱신 |

### JSONB 스키마 예시

#### 공정 3 (센서 검사)
```json
{
  "temp_sensor": {
    "measured_value": 60.5,
    "min_threshold": 59.0,
    "max_threshold": 61.0,
    "result": "PASS"
  },
  "tof_sensor": {
    "measured_distance": 195.2,
    "min_threshold": 190.0,
    "max_threshold": 200.0,
    "result": "PASS"
  },
  "overall_result": "PASS",
  "inspection_duration_ms": 5420
}
```

#### 공정 6 (성능검사)
```json
{
  "test_results": [
    {"test_id": "T1", "온도": 60.2, "변위": 198.3, "힘": 15.2, "result": "PASS"},
    {"test_id": "T2", "온도": 60.4, "변위": 199.1, "힘": 15.4, "result": "PASS"},
    {"test_id": "T3", "온도": 60.1, "변위": 197.8, "힘": 15.1, "result": "PASS"}
  ],
  "overall_result": "PASS",
  "test_duration_seconds": 550
}
```

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_process_data ON process_data(id);

-- INDEX (LOT별 조회)
CREATE INDEX idx_process_data_lot ON process_data(lot_id);

-- INDEX (시리얼별 조회)
CREATE INDEX idx_process_data_serial ON process_data(serial_id);

-- INDEX (공정별 조회)
CREATE INDEX idx_process_data_process ON process_data(process_id);

-- INDEX (라인별 조회)
CREATE INDEX idx_process_data_line ON process_data(line_id);

-- INDEX (설비별 조회)
CREATE INDEX idx_process_data_equipment ON process_data(equipment_id);

-- INDEX (착공 시간 역순)
CREATE INDEX idx_process_data_time ON process_data(start_time DESC);

-- COMPOSITE INDEX (시리얼 + 공정) - 공정 순서 검증 최적화
CREATE INDEX idx_process_data_serial_process ON process_data(serial_id, process_id);

-- PARTIAL INDEX (미완료 공정 조회)
CREATE INDEX idx_process_data_incomplete ON process_data(serial_id, process_id)
WHERE complete_time IS NULL;

-- COMPOSITE INDEX (완공 시간 + 결과) - 통계 조회 최적화
CREATE INDEX idx_process_data_completed ON process_data(complete_time DESC, result)
WHERE complete_time IS NOT NULL;

-- GIN INDEX (JSONB 검색 최적화)
CREATE INDEX idx_process_data_jsonb ON process_data USING GIN (process_specific_data);

-- PARTIAL INDEX (재작업 조회)
CREATE INDEX idx_process_data_rework ON process_data(is_rework) WHERE is_rework = TRUE;
```

### 예상 데이터량
- **연간**: ~40,000,000 records
- **3년 후**: ~120,000,000 records
- **5년 후**: ~200,000,000 records

### 샘플 데이터

```sql
-- 공정 1 착공 (시리얼 미발급)
INSERT INTO process_data (lot_id, serial_id, process_id, line_id, equipment_id, worker_id, start_time)
VALUES (1, NULL, 1, 'LINE-A', 'LASER-01', 'worker01', NOW());

-- 공정 1 완공
UPDATE process_data SET
    complete_time = NOW(),
    result = 'PASS'
WHERE id = 1;

-- 공정 3 완공 (센서 검사 데이터 포함)
UPDATE process_data SET
    complete_time = NOW(),
    result = 'PASS',
    process_specific_data = '{
        "temp_sensor": {"measured_value": 60.5, "result": "PASS"},
        "tof_sensor": {"measured_distance": 195.2, "result": "PASS"},
        "overall_result": "PASS"
    }'::jsonb
WHERE id = 3;
```

### 사용 예시

```sql
-- 시리얼의 모든 공정 이력 조회
SELECT pd.*, p.process_name
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE pd.serial_id = 1
ORDER BY p.sequence_order;

-- 미완료 공정 조회
SELECT * FROM process_data
WHERE complete_time IS NULL
ORDER BY start_time;

-- JSONB 검색 (온도 센서 FAIL)
SELECT * FROM process_data
WHERE process_specific_data @> '{"temp_sensor": {"result": "FAIL"}}'::jsonb;
```

---

## 6. users (사용자)

### 목적
사용자 인증 및 권한 관리. 작업자, 생산관리자, 관리자 계정 관리.

### 비즈니스 규칙
- **역할 (Role)**: ADMIN, MANAGER, WORKER, VIEWER
- **로그인 실패 제한**: 5회 실패 시 계정 잠금 (30분)
- **비밀번호**: bcrypt 해시 저장 (평문 저장 금지)
- **JWT 토큰**: Access Token 15분, Refresh Token 7일

### DDL

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'WORKER' NOT NULL CHECK (role IN ('ADMIN', 'MANAGER', 'WORKER', 'VIEWER')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_login_at TIMESTAMP WITH TIME ZONE,
    failed_login_count INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE users IS '사용자 관리 테이블 (인증 + 권한)';
COMMENT ON COLUMN users.role IS '역할 (ADMIN=관리자, MANAGER=생산관리자, WORKER=작업자, VIEWER=조회자)';
COMMENT ON COLUMN users.failed_login_count IS '로그인 실패 횟수 (5회 초과 시 계정 잠금)';
COMMENT ON COLUMN users.locked_until IS '계정 잠금 해제 시간';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **user_id** | VARCHAR(50) | NO | - | 사용자 ID (로그인용) | UNIQUE, NOT NULL |
| **username** | VARCHAR(100) | NO | - | 사용자명 | NOT NULL |
| **email** | VARCHAR(255) | YES | NULL | 이메일 | UNIQUE |
| **password_hash** | VARCHAR(255) | NO | - | 비밀번호 해시 (bcrypt) | NOT NULL |
| **role** | VARCHAR(20) | NO | 'WORKER' | 역할 | CHECK (4가지 역할) |
| **is_active** | BOOLEAN | NO | TRUE | 활성화 여부 | NOT NULL |
| **last_login_at** | TIMESTAMPTZ | YES | NULL | 마지막 로그인 시간 | - |
| **failed_login_count** | INTEGER | NO | 0 | 로그인 실패 횟수 | NOT NULL |
| **locked_until** | TIMESTAMPTZ | YES | NULL | 계정 잠금 해제 시간 | - |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |
| **updated_at** | TIMESTAMPTZ | NO | NOW() | 수정 시간 | Trigger 자동 갱신 |

### 역할 (Role) 권한

| 역할 | 설명 | 권한 |
|------|------|------|
| **ADMIN** | 시스템 관리자 | 전체 권한 (사용자 관리, 시스템 설정) |
| **MANAGER** | 생산 관리자 | LOT 생성, 재작업 승인, 대시보드 조회 |
| **WORKER** | 작업자 | 공정 착공/완공, 시리얼 조회 |
| **VIEWER** | 조회자 | 읽기 전용 (대시보드, 이력 조회) |

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_users ON users(id);

-- UNIQUE INDEX (사용자 ID 중복 방지)
CREATE UNIQUE INDEX idx_user_id ON users(user_id);

-- UNIQUE INDEX (이메일 중복 방지)
CREATE UNIQUE INDEX idx_user_email ON users(email);

-- INDEX (역할별 조회)
CREATE INDEX idx_user_role ON users(role);

-- PARTIAL INDEX (활성화된 사용자만 조회)
CREATE INDEX idx_user_active ON users(is_active) WHERE is_active = TRUE;
```

### 예상 데이터량
- **초기**: 10~20 users
- **3년 후**: ~50 users
- **5년 후**: ~100 users

### 초기 데이터 (Seed Data)

```sql
-- 관리자 계정 (비밀번호: admin123, bcrypt 해시)
INSERT INTO users (user_id, username, email, password_hash, role) VALUES
('admin', '시스템 관리자', 'admin@withforce.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyC6pY4T4OGC', 'ADMIN'),
('manager01', '생산관리자1', 'manager@withforce.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyC6pY4T4OGC', 'MANAGER'),
('worker01', '작업자1', 'worker01@withforce.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyC6pY4T4OGC', 'WORKER');
```

### 사용 예시

```sql
-- 사용자 인증
SELECT * FROM users WHERE user_id = 'worker01' AND is_active = TRUE;

-- 로그인 성공 시 업데이트
UPDATE users SET
    last_login_at = NOW(),
    failed_login_count = 0
WHERE user_id = 'worker01';

-- 로그인 실패 시 업데이트
UPDATE users SET
    failed_login_count = failed_login_count + 1,
    locked_until = CASE
        WHEN failed_login_count + 1 >= 5 THEN NOW() + INTERVAL '30 minutes'
        ELSE locked_until
    END
WHERE user_id = 'worker01';
```

---

## 7. audit_logs (감사 로그)

### 목적
모든 CUD (Create, Update, Delete) 작업 이력 추적. 보안 감사 및 데이터 변경 추적.

### 비즈니스 규칙
- **자동 생성**: Trigger를 통해 모든 주요 테이블의 CUD 작업 자동 기록
- **JSONB 저장**: 변경 전/후 데이터를 JSONB로 저장
- **삭제 금지**: INSERT만 허용 (UPDATE/DELETE 금지)
- **파티셔닝**: 3개월 단위 날짜 파티셔닝 (선택사항)

### DDL

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    user_id VARCHAR(50),
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE audit_logs IS '감사 로그 테이블 (모든 CUD 작업 기록)';
COMMENT ON COLUMN audit_logs.table_name IS '변경된 테이블명';
COMMENT ON COLUMN audit_logs.record_id IS '변경된 레코드 ID';
COMMENT ON COLUMN audit_logs.old_data IS '변경 전 데이터 (JSON)';
COMMENT ON COLUMN audit_logs.new_data IS '변경 후 데이터 (JSON)';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **table_name** | VARCHAR(100) | NO | - | 테이블명 | NOT NULL |
| **record_id** | BIGINT | YES | NULL | 레코드 ID | - |
| **action** | VARCHAR(20) | NO | - | 작업 유형 | CHECK (INSERT/UPDATE/DELETE) |
| **user_id** | VARCHAR(50) | YES | NULL | 사용자 ID | - |
| **old_data** | JSONB | YES | NULL | 변경 전 데이터 | - |
| **new_data** | JSONB | YES | NULL | 변경 후 데이터 | - |
| **ip_address** | INET | YES | NULL | IP 주소 | - |
| **user_agent** | TEXT | YES | NULL | User Agent | - |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_audit_logs ON audit_logs(id);

-- INDEX (테이블별 조회)
CREATE INDEX idx_audit_table ON audit_logs(table_name);

-- INDEX (생성 시간 역순)
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);

-- INDEX (사용자별 조회)
CREATE INDEX idx_audit_user ON audit_logs(user_id);

-- INDEX (작업 유형별 조회)
CREATE INDEX idx_audit_action ON audit_logs(action);

-- COMPOSITE INDEX (테이블 + 레코드 ID)
CREATE INDEX idx_audit_record ON audit_logs(table_name, record_id);
```

### 파티셔닝 (선택사항)

```sql
-- 3개월 단위 파티셔닝
CREATE TABLE audit_logs_2025_q1 PARTITION OF audit_logs
FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE audit_logs_2025_q2 PARTITION OF audit_logs
FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
```

### 예상 데이터량
- **연간**: ~100,000,000 records
- **3년 후**: ~300,000,000 records
- **5년 후**: ~500,000,000 records

### 샘플 데이터

```sql
-- Trigger 자동 생성 예시
-- (실제로는 Trigger가 자동으로 INSERT)
INSERT INTO audit_logs (table_name, record_id, action, user_id, new_data) VALUES
('lots', 1, 'INSERT', 'manager01', '{"lot_number": "WF-KR-251110D-001", "status": "CREATED"}'::jsonb);

INSERT INTO audit_logs (table_name, record_id, action, user_id, old_data, new_data) VALUES
('lots', 1, 'UPDATE', 'system',
 '{"status": "CREATED"}'::jsonb,
 '{"status": "IN_PROGRESS"}'::jsonb);
```

### 사용 예시

```sql
-- 특정 LOT의 변경 이력 조회
SELECT * FROM audit_logs
WHERE table_name = 'lots' AND record_id = 1
ORDER BY created_at DESC;

-- 최근 1시간 내 모든 변경 이력
SELECT * FROM audit_logs
WHERE created_at >= NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

-- 특정 사용자의 작업 이력
SELECT * FROM audit_logs
WHERE user_id = 'worker01'
ORDER BY created_at DESC
LIMIT 100;
```

---

## 8. firmware_versions (펌웨어 버전)

### 목적
펌웨어 파일 버전 관리 및 배포. 제어 보드 업데이트용 펌웨어 추적.

### 비즈니스 규칙
- **버전 포맷**: Semantic Versioning (v1.2.3)
- **현재 배포 버전**: `is_active = TRUE` (1개만 TRUE)
- **MD5 체크섬**: 다운로드 무결성 검증
- **파일 위치**: 로컬 스토리지 또는 S3

### DDL

```sql
CREATE TABLE firmware_versions (
    id BIGSERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    md5_hash VARCHAR(32) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    release_notes TEXT,
    target_mcu VARCHAR(100),
    is_active BOOLEAN DEFAULT FALSE NOT NULL,
    released_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

COMMENT ON TABLE firmware_versions IS '펌웨어 버전 관리 테이블';
COMMENT ON COLUMN firmware_versions.is_active IS '현재 배포 중인 버전 (1개만 TRUE)';
COMMENT ON COLUMN firmware_versions.md5_hash IS 'MD5 체크섬 (무결성 검증)';
```

### 컬럼 정의

| 컬럼명 | 타입 | NULL | 기본값 | 설명 | 제약조건 |
|--------|------|------|--------|------|---------|
| **id** | BIGSERIAL | NO | AUTO | PK | PRIMARY KEY |
| **version** | VARCHAR(50) | NO | - | 버전 (예: v1.2.3) | UNIQUE, NOT NULL |
| **filename** | VARCHAR(255) | NO | - | 파일명 | NOT NULL |
| **file_size** | BIGINT | NO | - | 파일 크기 (bytes) | NOT NULL |
| **md5_hash** | VARCHAR(32) | NO | - | MD5 체크섬 | NOT NULL |
| **file_path** | VARCHAR(500) | NO | - | 파일 경로 | NOT NULL |
| **release_notes** | TEXT | YES | NULL | 릴리스 노트 | - |
| **target_mcu** | VARCHAR(100) | YES | NULL | 대상 MCU | - |
| **is_active** | BOOLEAN | NO | FALSE | 현재 배포 버전 | NOT NULL |
| **released_at** | TIMESTAMPTZ | YES | NULL | 배포 시간 | - |
| **created_by** | VARCHAR(50) | YES | NULL | 생성자 | - |
| **created_at** | TIMESTAMPTZ | NO | NOW() | 생성 시간 | NOT NULL |

### 인덱스

```sql
-- PRIMARY KEY
CREATE UNIQUE INDEX pk_firmware_versions ON firmware_versions(id);

-- UNIQUE INDEX (버전 중복 방지)
CREATE UNIQUE INDEX idx_firmware_version ON firmware_versions(version);

-- PARTIAL INDEX (현재 배포 버전)
CREATE INDEX idx_firmware_active ON firmware_versions(is_active) WHERE is_active = TRUE;

-- INDEX (배포 시간 역순)
CREATE INDEX idx_firmware_released ON firmware_versions(released_at DESC);
```

### 예상 데이터량
- **연간**: ~50 versions
- **3년 후**: ~150 versions
- **5년 후**: ~500 versions

### 샘플 데이터

```sql
INSERT INTO firmware_versions (version, filename, file_size, md5_hash, file_path, target_mcu, is_active, released_at, created_by) VALUES
('v1.0.0', 'firmware_v1.0.0.bin', 524288, '5d41402abc4b2a76b9719d911017c592', '/firmware/v1.0.0.bin', 'STM32F4', TRUE, NOW(), 'admin'),
('v1.0.1', 'firmware_v1.0.1.bin', 524800, '7d793037a0760186574b0282f2f435e7', '/firmware/v1.0.1.bin', 'STM32F4', FALSE, NOW() - INTERVAL '7 days', 'admin');
```

### 사용 예시

```sql
-- 현재 배포 중인 버전 조회
SELECT * FROM firmware_versions WHERE is_active = TRUE;

-- 최신 버전 조회
SELECT * FROM firmware_versions ORDER BY released_at DESC LIMIT 1;

-- 새 버전 배포 (기존 활성화 해제 + 신규 활성화)
BEGIN;
UPDATE firmware_versions SET is_active = FALSE WHERE is_active = TRUE;
UPDATE firmware_versions SET is_active = TRUE WHERE version = 'v1.0.2';
COMMIT;
```

---

## 📚 관련 문서

- [01-erd.md](01-erd.md) - ERD 다이어그램
- [03-relationship-specs.md](03-relationship-specs.md) - FK 관계 상세
- [04-business-rules.md](04-business-rules.md) - Trigger/Function 설명
- [05-index-strategy.md](05-index-strategy.md) - 인덱스 최적화
- [07-data-dictionary.md](07-data-dictionary.md) - 전체 컬럼 사전

---

**마지막 업데이트**: 2025-01-17
