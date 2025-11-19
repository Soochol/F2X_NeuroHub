# Database 요구사항

> user-specification 및 database/docs 기반 Database 관련 요구사항 통합 정리

---

## 1. 데이터베이스 기술 스택

### 1.1 핵심 기술
- **DBMS**: PostgreSQL 14+ (15+ 권장)
- **ORM**: SQLAlchemy 2.0 (async)
- **마이그레이션**: Alembic
- **Connection Pool**: asyncpg
  - pool_size: 20-50
  - max_overflow: 10

### 1.2 성능 요구사항
- **쿼리 응답 시간**: < 500ms (복잡한 집계 쿼리)
- **Connection Pool**: 50 동시 연결 지원
- **TPS**: 최소 20 TPS

### 1.3 설계 원칙
- ACID compliance
- 완벽한 추적성 (Traceability)
- 감사 추적 (Audit trail)
- 확장성 (Scalability)
- **명명 규칙**: snake_case
- **문자셋**: UTF-8 (한글 지원)

---

## 2. 테이블 구조

### 2.1 테이블 목록 및 예상 데이터량

| 테이블명 | 한글명 | 목적 | 레코드 수 (예상) | 우선순위 |
|---------|--------|------|-----------------|---------|
| `product_models` | 제품 모델 | 제품 유형 마스터 | ~10 | P0 |
| `lots` | LOT | 생산 LOT 관리 | ~50K/year | P0 |
| `serials` | 시리얼 번호 | 개별 제품 추적 | ~5M/year | P0 |
| `processes` | 공정 | 공정 정의 (8개 고정) | 8 | P0 |
| `process_data` | 공정 데이터 | 작업 이력 및 측정 | ~40M/year | P0 |
| `users` | 사용자 | 인증 및 권한 | ~100 | P1 |
| `audit_logs` | 감사 로그 | 변경 이력 추적 | ~100M/year | P1 |
| `production_lines` | 생산 라인 | 라인 마스터 | ~10 | P2 |
| `equipment` | 설비 | 장비 마스터 | ~100 | P2 |

---

## 3. 상세 스키마

### 3.1 product_models (제품 모델)

**목적**: 제품 모델 마스터 데이터 관리 (예: NH-F2X-001)

**비즈니스 규칙**:
- 제품 단종 시 `status = 'DISCONTINUED'` 처리 (DELETE 금지)
- `model_code`는 대문자 + 숫자 조합
- 한 모델은 여러 LOT 생성 가능 (1:N)

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key |
| model_code | VARCHAR(50) | NOT NULL | - | 고유 모델 코드 (예: NH-F2X-001) |
| model_name | VARCHAR(255) | NOT NULL | - | 제품명 (한글/영문) |
| category | VARCHAR(100) | NULL | NULL | 제품 카테고리 |
| production_cycle_days | INTEGER | NULL | NULL | 생산 주기 (일) |
| specifications | JSONB | NULL | '{}' | 기술 사양 |
| status | VARCHAR(20) | NOT NULL | 'ACTIVE' | ACTIVE/INACTIVE/DISCONTINUED |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 생성일시 |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 수정일시 |

**Constraints**:
```sql
ALTER TABLE product_models ADD CONSTRAINT pk_product_models PRIMARY KEY (id);
ALTER TABLE product_models ADD CONSTRAINT uk_product_models_model_code UNIQUE (model_code);
ALTER TABLE product_models ADD CONSTRAINT chk_product_models_status
CHECK (status IN ('ACTIVE', 'INACTIVE', 'DISCONTINUED'));
```

---

### 3.2 lots (생산 LOT)

**목적**: 생산 배치 추적 (LOT당 최대 100대)

**비즈니스 규칙**:
- **LOT 번호 포맷**: `{MODEL_CODE}-KR-YYMMDD{D|N}-nnn`
  - 예: `PSA10-KR-251110D-001`
- **상태 전이**: `CREATED → IN_PROGRESS → COMPLETED → CLOSED`
- **목표 수량**: 기본 100, 최대 200
- **첫 시리얼 생성 시**: LOT 상태 자동 `IN_PROGRESS` 전환

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key |
| lot_number | VARCHAR(50) | NOT NULL | AUTO | LOT 번호 (자동 생성) |
| product_model_id | BIGINT | NOT NULL | - | FK: product_models |
| production_line_id | BIGINT | NULL | - | FK: production_lines |
| production_date | DATE | NOT NULL | - | 생산 일자 |
| shift | VARCHAR(1) | NOT NULL | - | 교대 (D: 주간, N: 야간) |
| target_quantity | INTEGER | NOT NULL | 100 | 목표 수량 |
| actual_quantity | INTEGER | NOT NULL | 0 | 실제 수량 |
| passed_quantity | INTEGER | NOT NULL | 0 | 합격 수량 |
| failed_quantity | INTEGER | NOT NULL | 0 | 불량 수량 |
| status | VARCHAR(20) | NOT NULL | 'CREATED' | LOT 상태 |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 생성일시 |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 수정일시 |
| closed_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | 마감일시 |

**LOT 번호 자동 생성 Trigger**:
```sql
CREATE OR REPLACE FUNCTION generate_lot_number()
RETURNS TRIGGER AS $$
DECLARE
    v_model_code VARCHAR(50);
    v_date_part VARCHAR(6);
    v_sequence INTEGER;
BEGIN
    SELECT model_code INTO v_model_code
    FROM product_models WHERE id = NEW.product_model_id;

    v_date_part := TO_CHAR(NEW.production_date, 'YYMMDD');

    SELECT COALESCE(MAX(
        CAST(SUBSTRING(lot_number FROM LENGTH(lot_number) - 2) AS INTEGER)
    ), 0) + 1 INTO v_sequence
    FROM lots
    WHERE lot_number LIKE v_model_code || '-KR-' || v_date_part || NEW.shift || '-%';

    NEW.lot_number := v_model_code || '-KR-' || v_date_part || NEW.shift || '-' ||
                      LPAD(v_sequence::TEXT, 3, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

### 3.3 serials (시리얼 번호)

**목적**: 개별 제품 추적 및 상태 관리

**비즈니스 규칙**:
- **시리얼 번호 포맷**: `{LOT_NUMBER}-XXXX`
  - 예: `PSA10-KR-251110D-001-0001`
- **상태 전이**: `CREATED → IN_PROGRESS → PASSED/FAILED`
- **재작업 제한**: 최대 3회
- **LOT당 시리얼 수**: `target_quantity` 초과 불가

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key |
| serial_number | VARCHAR(50) | NOT NULL | AUTO | 시리얼 번호 (자동 생성) |
| lot_id | BIGINT | NOT NULL | - | FK: lots |
| sequence_in_lot | INTEGER | NOT NULL | AUTO | LOT 내 순번 (1-100) |
| status | VARCHAR(20) | NOT NULL | 'CREATED' | 상태 |
| rework_count | INTEGER | NOT NULL | 0 | 재작업 횟수 (0-3) |
| failure_reason | TEXT | NULL | NULL | 불량 사유 |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 생성일시 |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 수정일시 |
| completed_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | 완료일시 |

**상태 전이 다이어그램**:
```
CREATED → IN_PROGRESS → PASSED
                      ↓
                    FAILED → IN_PROGRESS (rework, max 3x)
```

---

### 3.4 processes (제조 공정)

**목적**: 8개 제조 공정 정의 및 순서 관리

| Number | Code | Korean Name | English Name | Duration (sec) |
|--------|------|-------------|--------------|----------------|
| 1 | LASER_MARKING | 레이저 마킹 | Laser Marking | 60 |
| 2 | LMA_ASSEMBLY | LMA 조립 | LMA Assembly | 180 |
| 3 | SENSOR_INSPECTION | 센서 검사 | Sensor Inspection | 120 |
| 4 | FIRMWARE_UPLOAD | 펌웨어 업로드 | Firmware Upload | 300 |
| 5 | ROBOT_ASSEMBLY | 로봇 조립 | Robot Assembly | 300 |
| 6 | PERFORMANCE_TEST | 성능검사 | Performance Test | 180 |
| 7 | LABEL_PRINTING | 라벨 프린팅 | Label Printing | 30 |
| 8 | PACKAGING_INSPECTION | 포장 + 외관검사 | Packaging & Visual Inspection | 90 |

---

### 3.5 process_data (공정 실행 데이터)

**목적**: 공정별 작업 이력 및 측정 데이터 저장

**비즈니스 규칙**:
- **data_level**: LOT (배치) 또는 SERIAL (개별)
- **JSONB measurements**: 공정별 유연한 측정 데이터 저장
- **공정 순서 제어**: 이전 공정 PASS 완료 확인
- **각 시리얼**: 완료 시 8개의 PASS 기록 필요

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key |
| lot_id | BIGINT | NOT NULL | - | FK: lots |
| serial_id | BIGINT | NULL | NULL | FK: serials (NULL: LOT 레벨) |
| process_id | BIGINT | NOT NULL | - | FK: processes |
| operator_id | BIGINT | NOT NULL | - | FK: users |
| equipment_id | BIGINT | NULL | NULL | FK: equipment |
| data_level | VARCHAR(10) | NOT NULL | - | LOT/SERIAL |
| result | VARCHAR(10) | NOT NULL | - | PASS/FAIL/REWORK |
| measurements | JSONB | NULL | '{}' | 측정 데이터 |
| defects | JSONB | NULL | '[]' | 불량 정보 |
| notes | TEXT | NULL | NULL | 비고 |
| started_at | TIMESTAMP WITH TIME ZONE | NOT NULL | - | 착공 시간 |
| completed_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | 완공 시간 |
| duration_seconds | INTEGER | NULL | NULL | 소요 시간 (자동 계산) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | 생성일시 |

**Partial Unique Index** (동일 시리얼+공정에 PASS 1개만):
```sql
CREATE UNIQUE INDEX uk_process_data_serial_process
ON process_data(serial_id, process_id)
WHERE serial_id IS NOT NULL AND result = 'PASS';
```

---

### 3.6 users (사용자)

**역할별 권한**:

| Role | Description | Permissions |
|------|-------------|-------------|
| ADMIN | 시스템 관리자 | 전체 권한 |
| MANAGER | 생산 관리자 | LOT 생성, 재작업 승인, 대시보드 |
| WORKER | 작업자 | 공정 착공/완공, 시리얼 조회 |

---

### 3.7 audit_logs (감사 로그)

**목적**: 모든 CUD 작업 이력 추적 (불변)

**불변성 보장 Trigger**:
```sql
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_logs_immutable
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_modification();
```

---

## 4. Foreign Key 관계 명세

### 4.1 관계 다이어그램

```
product_models (1) ──────< (N) lots (1) ──────< (N, max 100) serials
                                │                        │
                                └────< (N) ──────────────┘
                                        process_data
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │                     │                     │
                  (N) >─────< (1)       (N) >─────< (1)       (N) >─────< (1)
                     lots              serials              processes

users (1) ──────< (N) process_data
  │
  └──────< (N) audit_logs
```

### 4.2 관계 상세

| Parent Table | Child Table | FK Column | Cardinality | Delete Rule |
|--------------|-------------|-----------|-------------|-------------|
| product_models | lots | product_model_id | 1:N | RESTRICT |
| lots | serials | lot_id | 1:N (max 100) | RESTRICT |
| lots | process_data | lot_id | 1:N | RESTRICT |
| serials | process_data | serial_id | 1:8 (expected) | RESTRICT |
| processes | process_data | process_id | 1:N | RESTRICT |
| users | process_data | operator_id | 1:N | RESTRICT |
| users | audit_logs | user_id | 1:N | RESTRICT |

---

## 5. 인덱스 전략

### 5.1 주요 인덱스

| 테이블 | 인덱스명 | 타입 | 목적 | 효과 |
|--------|---------|------|------|------|
| lots | idx_lots_active | Partial | 활성 LOT 조회 | 500ms → 10ms |
| serials | idx_serials_failed | Partial | 불량 분석 | 1s → 50ms |
| process_data | idx_process_data_serial_process | Composite | 공정 순서 검증 | 2s → 10ms |
| process_data | idx_process_data_measurements | GIN | JSONB 검색 | 5s → 100ms |
| audit_logs | idx_audit_logs_entity_history | Composite | 엔티티 이력 | - |

### 5.2 인덱스 생성 SQL

```sql
-- lots: 활성 LOT 부분 인덱스
CREATE INDEX idx_lots_active
ON lots(status, production_date)
WHERE status IN ('CREATED', 'IN_PROGRESS');

-- serials: 불량품 부분 인덱스
CREATE INDEX idx_serials_failed
ON serials(lot_id, failure_reason)
WHERE status = 'FAILED';

-- process_data: GIN 인덱스
CREATE INDEX idx_process_data_measurements
ON process_data USING GIN (measurements);

-- audit_logs: 엔티티 이력 조회
CREATE INDEX idx_audit_logs_entity_history
ON audit_logs(entity_type, entity_id, created_at DESC);
```

---

## 6. 비즈니스 규칙 (Trigger)

### 6.1 규칙 목록

| ID | 규칙명 | 설명 |
|----|--------|------|
| BR-001 | LOT 상태 전이 검증 | CREATED → IN_PROGRESS → COMPLETED → CLOSED |
| BR-002 | 공정 순서 제어 | 이전 공정 PASS 완료 확인 |
| BR-003 | 시리얼 상태 자동 업데이트 | 공정 완공 시 상태 전환 |
| BR-004 | 시리얼 생성 제한 | LOT target_quantity 초과 방지 |
| BR-005 | 재작업 횟수 제한 | 최대 3회 |
| BR-006 | 감사 로그 자동 생성 | 모든 CUD 작업 기록 |
| BR-007 | 공정 7 착공 조건 강화 | 라벨 프린팅 시작 전 공정 1~6 모두 PASS 필수 |

### 6.2 BR-002: 공정 순서 제어

```sql
CREATE OR REPLACE FUNCTION validate_process_sequence()
RETURNS TRIGGER AS $$
DECLARE
    v_current_process_number INTEGER;
    v_max_completed INTEGER;
    v_passed_count INTEGER;
BEGIN
    IF NEW.data_level != 'SERIAL' OR NEW.serial_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT process_number INTO v_current_process_number
    FROM processes WHERE id = NEW.process_id;

    SELECT COALESCE(MAX(p.process_number), 0)
    INTO v_max_completed
    FROM process_data pd
    JOIN processes p ON pd.process_id = p.id
    WHERE pd.serial_id = NEW.serial_id AND pd.result = 'PASS';

    IF v_current_process_number > v_max_completed + 1 THEN
        RAISE EXCEPTION 'Cannot execute process % before completing process %',
            v_current_process_number, v_max_completed + 1;
    END IF;

    -- BR-007: Special validation for Process 7 (Label Printing)
    -- All processes 1-6 must be PASS before starting Process 7
    IF v_current_process_number = 7 THEN
        SELECT COUNT(DISTINCT p.process_number)
        INTO v_passed_count
        FROM process_data pd
        JOIN processes p ON pd.process_id = p.id
        WHERE pd.serial_id = NEW.serial_id
          AND p.process_number BETWEEN 1 AND 6
          AND pd.result = 'PASS';

        IF v_passed_count < 6 THEN
            RAISE EXCEPTION 'Process 7 (Label Printing) requires all previous processes (1-6) to be PASS. Current PASS count: %', v_passed_count;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 6.3 BR-007: 공정 7 착공 조건 강화

**목적**: 라벨 프린팅 공정은 모든 제조 공정이 완료된 제품에만 수행되어야 함

**검증 로직**:
1. 공정 7 착공 요청 시 해당 시리얼의 공정 1~6 완료 여부 확인
2. 공정 1~6 중 하나라도 PASS가 아니면 착공 거부
3. 에러 메시지에 현재 PASS된 공정 수 표시

**에러 상황**:
- 공정 1~6 중 일부만 완료된 경우
- 일부 공정이 FAIL 또는 REWORK 상태인 경우

### 6.3 BR-006: 감사 로그 자동 생성

```sql
CREATE OR REPLACE FUNCTION log_audit_event()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id BIGINT;
    v_action VARCHAR(10);
BEGIN
    v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::BIGINT;
    v_action := CASE TG_OP WHEN 'INSERT' THEN 'CREATE' WHEN 'UPDATE' THEN 'UPDATE' ELSE 'DELETE' END;

    INSERT INTO audit_logs (user_id, entity_type, entity_id, action, old_values, new_values)
    VALUES (
        COALESCE(v_user_id, 1),
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        v_action,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD)::JSONB END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW)::JSONB END
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

---

## 7. JSONB 데이터 구조

### 7.1 공정별 measurements 스키마

#### SENSOR_INSPECTION
```json
{
  "sensor_channels_tested": 8,
  "signal_quality_avg": 0.92,
  "noise_level_db": -45,
  "calibration_offset": [0.01, -0.02, 0.00, 0.01, -0.01, 0.02, 0.00, -0.01]
}
```

#### PERFORMANCE_TEST
```json
{
  "response_time_ms": 42,
  "accuracy_percent": 96.5,
  "test_scenarios": [
    {"scenario": "idle", "result": "PASS"},
    {"scenario": "load", "result": "PASS"}
  ]
}
```

### 7.2 defects 배열 구조
```json
[
  {
    "defect_code": "E001",
    "defect_name": "Voltage out of range",
    "severity": "CRITICAL",
    "measured_value": 3.55,
    "expected_range": "3.2-3.4"
  }
]
```

---

## 8. 마이그레이션 및 초기화

### 8.1 DDL 실행 순서

```sql
-- 1. 기본 테이블
CREATE TABLE product_models, processes, users;

-- 2. 1차 의존 테이블
CREATE TABLE lots;

-- 3. 2차 의존 테이블
CREATE TABLE serials, process_data;

-- 4. 감사 테이블
CREATE TABLE audit_logs;

-- 5. 인덱스, 트리거, 마스터 데이터
```

### 8.2 마스터 데이터 초기화

```sql
INSERT INTO processes (process_number, process_code, process_name_ko, process_name_en, estimated_duration_seconds, sort_order) VALUES
(1, 'LASER_MARKING', '레이저 마킹', 'Laser Marking', 60, 1),
(2, 'LMA_ASSEMBLY', 'LMA 조립', 'LMA Assembly', 180, 2),
(3, 'SENSOR_INSPECTION', '센서 검사', 'Sensor Inspection', 120, 3),
(4, 'FIRMWARE_UPLOAD', '펌웨어 업로드', 'Firmware Upload', 300, 4),
(5, 'ROBOT_ASSEMBLY', '로봇 조립', 'Robot Assembly', 300, 5),
(6, 'PERFORMANCE_TEST', '성능검사', 'Performance Test', 180, 6),
(7, 'LABEL_PRINTING', '라벨 프린팅', 'Label Printing', 30, 7),
(8, 'PACKAGING_INSPECTION', '포장 + 외관검사', 'Packaging & Visual Inspection', 90, 8);
```

---

## 9. 데이터 보관 및 백업

### 9.1 보관 기간

| 데이터 유형 | 보관 기간 |
|------------|----------|
| 생산 데이터 | 영구 |
| 감사 로그 | 3년 (규정 준수) |

### 9.2 파티셔닝

```sql
-- process_data 월별 파티셔닝
CREATE TABLE process_data_y2025m11 PARTITION OF process_data
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

### 9.3 백업 일정

| 타입 | 일정 | 보관 |
|------|------|------|
| 전체 백업 | 일일 02:00 | 30일 |
| 증분 백업 | 6시간마다 | 7일 |

---

## 10. 비기능 요구사항

- **NFR-PERF-008**: 쿼리 응답 시간 < 500ms
- **NFR-PERF-009**: Connection Pool 50 동시 연결
- **NFR-RECOV-001**: RTO < 4시간
- **NFR-RECOV-002**: RPO < 6시간
- **보안**: ORM 사용, bcrypt 해시, RBAC

---

## 관련 문서

- [database/docs/requirements/01-ERD.md](../../database/docs/requirements/01-ERD.md) - ERD 다이어그램
- [database/docs/requirements/02-entity-definitions.md](../../database/docs/requirements/02-entity-definitions.md) - 엔티티 상세 정의
- [database/docs/requirements/03-relationship-specifications.md](../../database/docs/requirements/03-relationship-specifications.md) - 관계 명세
