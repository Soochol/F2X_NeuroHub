# 비즈니스 규칙 (Business Rules)

> F2X NeuroHub MES 데이터베이스 레벨 비즈니스 로직 (Trigger 및 Function)

## 📋 규칙 목록

| 규칙 ID | 규칙명 | 구현 | 우선순위 | 설명 |
|---------|--------|------|---------|------|
| BR-001 | LOT 상태 전이 검증 | Trigger | P0 | CREATED → IN_PROGRESS → COMPLETED → CLOSED |
| BR-002 | 공정 순서 제어 | Trigger | P0 | 이전 공정 PASS 완료 확인 |
| BR-003 | 시리얼 상태 자동 업데이트 | Trigger | P0 | 공정 완공 시 상태 자동 전환 |
| BR-004 | 시리얼 생성 제한 | Trigger | P0 | 목표 수량 초과 방지 |
| BR-005 | 재작업 횟수 제한 | Trigger | P1 | 최대 3회, 초과 시 SCRAPPED |
| BR-006 | 감사 로그 자동 생성 | Trigger | P1 | 모든 CUD 작업 기록 |
| BR-007 | LOT 자동 IN_PROGRESS | Trigger | P1 | 첫 시리얼 생성 시 |
| BR-008 | updated_at 자동 갱신 | Trigger | P2 | 모든 UPDATE 시 |

---

## BR-001: LOT 상태 전이 검증

### 목적
LOT의 상태 전이 규칙을 데이터베이스 레벨에서 강제

### 상태 전이 다이어그램
```
┌─────────┐
│ CREATED │ (LOT 생성)
└────┬────┘
     │ 첫 시리얼 생성 시
     ↓
┌─────────────┐
│ IN_PROGRESS │ (생산 진행 중)
└──────┬──────┘
       │ 모든 시리얼 완료 시
       ↓
┌───────────┐
│ COMPLETED │ (생산 완료)
└─────┬─────┘
      │ 관리자 승인
      ↓
┌────────┐
│ CLOSED │ (종료)
└────────┘
```

### Function 구현
```sql
CREATE OR REPLACE FUNCTION validate_lot_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- CREATED → IN_PROGRESS
    IF OLD.status = 'CREATED' AND NEW.status = 'IN_PROGRESS' THEN
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;

    -- IN_PROGRESS → COMPLETED
    IF OLD.status = 'IN_PROGRESS' AND NEW.status = 'COMPLETED' THEN
        -- 모든 시리얼이 완료 상태인지 검증
        IF EXISTS (
            SELECT 1 FROM serials
            WHERE lot_id = NEW.id
            AND status NOT IN ('PASSED', 'FAILED', 'SCRAPPED')
        ) THEN
            RAISE EXCEPTION 'Cannot complete LOT %: pending serials exist', NEW.lot_number;
        END IF;

        NEW.completed_at = NOW();
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;

    -- COMPLETED → CLOSED
    IF OLD.status = 'COMPLETED' AND NEW.status = 'CLOSED' THEN
        NEW.closed_at = NOW();
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;

    -- 기타 전이 거부
    RAISE EXCEPTION 'Invalid LOT status transition: % → % for LOT %',
        OLD.status, NEW.status, NEW.lot_number;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_lot_status
BEFORE UPDATE ON lots
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION validate_lot_status_transition();
```

### 테스트 케이스
```sql
-- ✅ 성공: CREATED → IN_PROGRESS
UPDATE lots SET status = 'IN_PROGRESS' WHERE lot_number = 'WF-KR-251110D-001';

-- ❌ 실패: CREATED → COMPLETED (건너뛰기 불가)
UPDATE lots SET status = 'COMPLETED' WHERE lot_number = 'WF-KR-251110D-001';
-- ERROR: Invalid LOT status transition: CREATED → COMPLETED

-- ❌ 실패: IN_PROGRESS → COMPLETED (대기 중인 시리얼 존재)
UPDATE lots SET status = 'COMPLETED' WHERE lot_number = 'WF-KR-251110D-001';
-- ERROR: Cannot complete LOT WF-KR-251110D-001: pending serials exist
```

---

## BR-002: 공정 순서 제어

### 목적
이전 공정 PASS 완료 확인 후 착공 허용

### Function 구현
```sql
CREATE OR REPLACE FUNCTION validate_process_sequence()
RETURNS TRIGGER AS $$
DECLARE
    current_sequence INTEGER;
    prev_process_complete BOOLEAN;
BEGIN
    -- 현재 공정의 sequence_order 조회
    SELECT sequence_order INTO current_sequence
    FROM processes WHERE id = NEW.process_id;

    -- 첫 번째 공정(1)이 아닌 경우, 직전 공정 완료 여부 확인
    IF current_sequence > 1 THEN
        -- serial_id가 NULL인 경우 (공정 1~6: 시리얼 미발급)
        IF NEW.serial_id IS NULL THEN
            -- LOT 단위 확인
            SELECT EXISTS (
                SELECT 1 FROM process_data pd
                JOIN processes p ON pd.process_id = p.id
                WHERE pd.lot_id = NEW.lot_id
                AND p.sequence_order = current_sequence - 1
                AND pd.result = 'PASS'
                AND pd.complete_time IS NOT NULL
            ) INTO prev_process_complete;
        ELSE
            -- 시리얼 단위 확인 (공정 7~8)
            SELECT EXISTS (
                SELECT 1 FROM process_data pd
                JOIN processes p ON pd.process_id = p.id
                WHERE pd.serial_id = NEW.serial_id
                AND p.sequence_order = current_sequence - 1
                AND pd.result = 'PASS'
                AND pd.complete_time IS NOT NULL
            ) INTO prev_process_complete;
        END IF;

        IF NOT prev_process_complete THEN
            RAISE EXCEPTION 'Previous process (sequence=%) not completed for lot_id=%, serial_id=%',
                current_sequence - 1, NEW.lot_id, NEW.serial_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_process_sequence
BEFORE INSERT ON process_data
FOR EACH ROW
EXECUTE FUNCTION validate_process_sequence();
```

---

## BR-003: 시리얼 상태 자동 업데이트

### 목적
공정 완공 결과에 따라 시리얼 상태 자동 전환

### Function 구현
```sql
CREATE OR REPLACE FUNCTION auto_update_serial_status()
RETURNS TRIGGER AS $$
DECLARE
    last_process_sequence INTEGER;
    current_process_sequence INTEGER;
BEGIN
    -- 완공 데이터가 아니면 무시
    IF NEW.complete_time IS NULL THEN
        RETURN NEW;
    END IF;

    -- serial_id가 NULL이면 무시 (공정 1~6: 시리얼 미발급)
    IF NEW.serial_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- 마지막 공정 sequence_order 조회
    SELECT MAX(sequence_order) INTO last_process_sequence FROM processes WHERE is_active = TRUE;

    -- 현재 공정 sequence_order 조회
    SELECT sequence_order INTO current_process_sequence
    FROM processes WHERE id = NEW.process_id;

    -- 불합격 처리
    IF NEW.result = 'FAIL' THEN
        UPDATE serials
        SET status = 'FAILED', updated_at = NOW()
        WHERE id = NEW.serial_id;

    -- 마지막 공정 합격 처리
    ELSIF NEW.result = 'PASS' AND current_process_sequence = last_process_sequence THEN
        UPDATE serials
        SET status = 'PASSED', updated_at = NOW()
        WHERE id = NEW.serial_id;

    -- 중간 공정 합격 처리
    ELSIF NEW.result = 'PASS' THEN
        UPDATE serials
        SET status = 'IN_PROGRESS', updated_at = NOW()
        WHERE id = NEW.serial_id AND status = 'CREATED';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_serial_status
AFTER INSERT OR UPDATE ON process_data
FOR EACH ROW
EXECUTE FUNCTION auto_update_serial_status();
```

---

## BR-004: 시리얼 생성 제한

### Function 구현
```sql
CREATE OR REPLACE FUNCTION validate_serial_creation()
RETURNS TRIGGER AS $$
DECLARE
    lot_status VARCHAR(20);
    serial_count INTEGER;
    target_qty INTEGER;
BEGIN
    -- LOT 상태 조회
    SELECT status, target_quantity INTO lot_status, target_qty
    FROM lots WHERE id = NEW.lot_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'LOT not found: %', NEW.lot_id;
    END IF;

    -- LOT이 CREATED 또는 IN_PROGRESS 상태가 아니면 거부
    IF lot_status NOT IN ('CREATED', 'IN_PROGRESS') THEN
        RAISE EXCEPTION 'Cannot create serial for LOT in % status', lot_status;
    END IF;

    -- 목표 수량 초과 여부 확인
    SELECT COUNT(*) INTO serial_count
    FROM serials WHERE lot_id = NEW.lot_id;

    IF serial_count >= target_qty THEN
        RAISE EXCEPTION 'LOT already has maximum serials (%, target=%)', serial_count, target_qty;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_serial_creation
BEFORE INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_serial_creation();
```

---

## BR-005: 재작업 횟수 제한

### Function 구현
```sql
CREATE OR REPLACE FUNCTION increment_rework_count()
RETURNS TRIGGER AS $$
BEGIN
    -- rework_approved_at이 새로 설정된 경우
    IF NEW.rework_approved_at IS NOT NULL AND OLD.rework_approved_at IS NULL THEN
        NEW.rework_count = COALESCE(OLD.rework_count, 0) + 1;

        -- 재작업 횟수 3회 초과 시 자동 SCRAPPED
        IF NEW.rework_count > 3 THEN
            NEW.status = 'SCRAPPED';
            RAISE NOTICE 'Serial % auto-scrapped due to rework count > 3', NEW.serial_number;
        END IF;
    END IF;

    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_rework_count
BEFORE UPDATE ON serials
FOR EACH ROW
WHEN (NEW.rework_approved_at IS DISTINCT FROM OLD.rework_approved_at)
EXECUTE FUNCTION increment_rework_count();
```

---

## BR-006: 감사 로그 자동 생성

### Function 구현
```sql
CREATE OR REPLACE FUNCTION create_audit_log()
RETURNS TRIGGER AS $$
DECLARE
    action_type VARCHAR(20);
BEGIN
    -- 액션 타입 결정
    IF TG_OP = 'INSERT' THEN
        action_type = 'INSERT';
    ELSIF TG_OP = 'UPDATE' THEN
        action_type = 'UPDATE';
    ELSIF TG_OP = 'DELETE' THEN
        action_type = 'DELETE';
    END IF;

    -- 감사 로그 삽입
    INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, user_id)
    VALUES (
        TG_TABLE_NAME,
        CASE
            WHEN TG_OP = 'DELETE' THEN OLD.id
            ELSE NEW.id
        END,
        action_type,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
        CURRENT_USER
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 주요 테이블에 적용
CREATE TRIGGER trg_audit_lots
AFTER INSERT OR UPDATE OR DELETE ON lots
FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER trg_audit_serials
AFTER INSERT OR UPDATE OR DELETE ON serials
FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER trg_audit_process_data
AFTER INSERT OR UPDATE OR DELETE ON process_data
FOR EACH ROW EXECUTE FUNCTION create_audit_log();
```

---

## BR-007: LOT 자동 IN_PROGRESS

### Function 구현
```sql
CREATE OR REPLACE FUNCTION auto_update_lot_status_on_serial_insert()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE lots
    SET status = 'IN_PROGRESS', updated_at = NOW()
    WHERE id = NEW.lot_id AND status = 'CREATED';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_lot_in_progress
AFTER INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION auto_update_lot_status_on_serial_insert();
```

---

## BR-008: updated_at 자동 갱신

### Function 구현
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 모든 주요 테이블에 적용
CREATE TRIGGER trg_update_product_models_updated_at
BEFORE UPDATE ON product_models
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_lots_updated_at
BEFORE UPDATE ON lots
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_serials_updated_at
BEFORE UPDATE ON serials
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_processes_updated_at
BEFORE UPDATE ON processes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_process_data_updated_at
BEFORE UPDATE ON process_data
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 📚 관련 문서

- [02-entity-definitions.md](02-entity-definitions.md) - 테이블 정의
- [03-relationship-specs.md](03-relationship-specs.md) - FK 관계
- [diagrams/state-diagram.mermaid](diagrams/state-diagram.mermaid) - 상태 전이 다이어그램

---

**마지막 업데이트**: 2025-01-17
