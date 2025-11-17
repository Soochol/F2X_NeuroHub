# 관계 명세서 (Relationship Specifications)

> F2X NeuroHub MES 데이터베이스 Foreign Key 관계 및 제약조건 상세 명세

## 📋 Foreign Key 관계 목록

| FK 이름 | 부모 테이블 | 자식 테이블 | 컬럼 | ON DELETE | ON UPDATE | 설명 |
|---------|-----------|-----------|------|-----------|-----------|------|
| fk_lots_product_model | product_models | lots | product_model_id | RESTRICT | CASCADE | 모델 삭제 시 LOT 존재하면 거부 |
| fk_serials_lot | lots | serials | lot_id | RESTRICT | CASCADE | LOT 삭제 시 시리얼 존재하면 거부 |
| fk_process_data_lot | lots | process_data | lot_id | RESTRICT | CASCADE | LOT 삭제 시 공정 데이터 존재하면 거부 |
| fk_process_data_serial | serials | process_data | serial_id | RESTRICT | CASCADE | 시리얼 삭제 시 공정 데이터 존재하면 거부 |
| fk_process_data_process | processes | process_data | process_id | RESTRICT | CASCADE | 공정 삭제 시 공정 데이터 존재하면 거부 |

---

## 관계별 상세 설명

### 1. product_models → lots (1:N)

**관계 유형**: One-to-Many (필수)

**FK 정의**:
```sql
ALTER TABLE lots
ADD CONSTRAINT fk_lots_product_model
FOREIGN KEY (product_model_id)
REFERENCES product_models(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

**비즈니스 규칙**:
- 한 제품 모델은 여러 LOT 보유 가능 (1:N)
- LOT 생성 시 반드시 제품 모델 지정 필요
- 제품 모델이 비활성화(`is_active=FALSE`)되어도 FK는 유지
- 제품 모델 삭제는 LOT이 존재하면 불가능 (RESTRICT)

**카디널리티**:
- 평균: 1 모델당 5,000 LOT/year
- 최대: 무제한

**ON DELETE RESTRICT 이유**:
- 제품 모델 삭제 시 관련 LOT 데이터 손실 방지
- 단종 제품은 `is_active = FALSE` 처리

**데이터 무결성 검증**:
```sql
-- 고아 레코드 확인 (있으면 안 됨)
SELECT COUNT(*) FROM lots l
LEFT JOIN product_models pm ON l.product_model_id = pm.id
WHERE pm.id IS NULL;
-- Expected: 0
```

**사용 예시**:
```sql
-- 제품 모델의 모든 LOT 조회
SELECT l.*
FROM lots l
JOIN product_models pm ON l.product_model_id = pm.id
WHERE pm.model_code = 'WF';

-- 제품 모델 삭제 시도 (LOT 존재 시 실패)
DELETE FROM product_models WHERE id = 1;
-- ERROR: update or delete on table "product_models" violates foreign key constraint
```

---

### 2. lots → serials (1:N)

**관계 유형**: One-to-Many (필수, 수량 제한)

**FK 정의**:
```sql
ALTER TABLE serials
ADD CONSTRAINT fk_serials_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

**비즈니스 규칙**:
- 한 LOT은 최대 `target_quantity`개 시리얼 보유 (기본 100, 최대 200)
- 시리얼 번호는 `{lot_number}-{sequence:04d}` 형식
- LOT 상태가 `CLOSED`이면 새 시리얼 생성 불가 (Trigger 검증)
- 첫 시리얼 생성 시 LOT 상태 자동 `IN_PROGRESS` 전환 (Trigger BR-007)

**카디널리티**:
- 평균: 1 LOT당 100 serials
- 최대: 1 LOT당 200 serials

**제약조건**:
```sql
-- Trigger: 목표 수량 초과 방지
CREATE TRIGGER trg_validate_serial_creation
BEFORE INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_serial_creation();
```

**ON DELETE RESTRICT 이유**:
- LOT 삭제 시 시리얼 데이터 손실 방지
- LOT은 논리 삭제만 허용 (status = CLOSED)

**데이터 무결성 검증**:
```sql
-- LOT당 시리얼 수 확인
SELECT lot_id, COUNT(*) as serial_count, MAX(target_quantity) as target
FROM serials s
JOIN lots l ON s.lot_id = l.id
GROUP BY lot_id
HAVING COUNT(*) > MAX(target_quantity);
-- Expected: 0 (목표 수량 초과 없음)

-- 시리얼 순번 중복 확인
SELECT lot_id, sequence, COUNT(*) as count
FROM serials
GROUP BY lot_id, sequence
HAVING COUNT(*) > 1;
-- Expected: 0 (순번 중복 없음)
```

**사용 예시**:
```sql
-- LOT의 모든 시리얼 조회
SELECT s.*
FROM serials s
WHERE s.lot_id = 1
ORDER BY s.sequence;

-- LOT별 시리얼 현황
SELECT l.lot_number, l.target_quantity,
       COUNT(s.id) as actual_count,
       COUNT(s.id) FILTER (WHERE s.status = 'PASSED') as passed_count,
       COUNT(s.id) FILTER (WHERE s.status = 'FAILED') as failed_count
FROM lots l
LEFT JOIN serials s ON l.id = s.lot_id
GROUP BY l.id;
```

---

### 3. lots → process_data (1:N)

**관계 유형**: One-to-Many (필수)

**FK 정의**:
```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

**비즈니스 규칙**:
- 한 LOT의 모든 공정 작업 데이터 추적
- 공정 1~6은 serial_id = NULL (LOT 단위 작업)
- 공정 7~8은 serial_id NOT NULL (시리얼 단위 작업)

**카디널리티**:
- 평균: 1 LOT당 800 process_data (8공정 × 100 시리얼)
- 최대: 1 LOT당 1,600 process_data (재작업 포함)

**ON DELETE RESTRICT 이유**:
- LOT 삭제 시 공정 데이터 손실 방지
- 추적성 (Traceability) 유지

**데이터 무결성 검증**:
```sql
-- LOT별 공정 데이터 수 확인
SELECT lot_id, COUNT(*) as process_count
FROM process_data
GROUP BY lot_id;

-- serial_id NULL인 공정 확인 (공정 1~6)
SELECT pd.*, p.sequence_order
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE pd.serial_id IS NULL AND p.sequence_order > 6;
-- Expected: 0 (공정 7~8은 serial_id 필수)
```

**사용 예시**:
```sql
-- LOT의 모든 공정 데이터 조회
SELECT pd.*, p.process_name
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE pd.lot_id = 1
ORDER BY p.sequence_order;
```

---

### 4. serials → process_data (1:N)

**관계 유형**: One-to-Many (선택적, NULL 허용)

**FK 정의**:
```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_serial
FOREIGN KEY (serial_id)
REFERENCES serials(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

**비즈니스 규칙**:
- 한 시리얼의 모든 공정 작업 데이터 추적
- serial_id NULL 허용 (공정 1~6은 시리얼 미발급)
- 공정 순서 제어: 이전 공정 PASS 완료 확인 (Trigger BR-002)
- 완공 시 시리얼 상태 자동 업데이트 (Trigger BR-003)

**카디널리티**:
- 평균: 1 시리얼당 8 process_data (8공정)
- 최대: 1 시리얼당 16 process_data (재작업 포함)

**ON DELETE RESTRICT 이유**:
- 시리얼 삭제 시 공정 데이터 손실 방지
- 완벽한 추적성 유지

**데이터 무결성 검증**:
```sql
-- 시리얼당 공정 데이터 수 확인
SELECT serial_id, COUNT(*) as process_count
FROM process_data
WHERE serial_id IS NOT NULL
GROUP BY serial_id
HAVING COUNT(*) > 16;
-- Expected: 0 (최대 16개)

-- 공정 순서 위반 확인
WITH process_sequence AS (
    SELECT pd.serial_id, pd.process_id, p.sequence_order,
           LAG(p.sequence_order) OVER (PARTITION BY pd.serial_id ORDER BY p.sequence_order) as prev_seq
    FROM process_data pd
    JOIN processes p ON pd.process_id = p.id
    WHERE pd.serial_id IS NOT NULL
)
SELECT * FROM process_sequence
WHERE prev_seq IS NOT NULL AND sequence_order != prev_seq + 1;
-- Expected: 0 (순서 위반 없음)
```

**사용 예시**:
```sql
-- 시리얼의 모든 공정 이력 조회
SELECT pd.*, p.process_name, pd.result
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE pd.serial_id = 1
ORDER BY p.sequence_order;
```

---

### 5. processes → process_data (1:N)

**관계 유형**: One-to-Many (필수)

**FK 정의**:
```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_process
FOREIGN KEY (process_id)
REFERENCES processes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

**비즈니스 규칙**:
- 한 공정의 모든 작업 이력 추적
- 공정 순서 (`sequence_order`) 기반 제어
- 공정 8개 고정 (변경 없음)

**카디널리티**:
- 평균: 1 공정당 5M process_data/year
- 최대: 무제한

**ON DELETE RESTRICT 이유**:
- 공정 삭제 시 작업 데이터 손실 방지
- 공정은 삭제 금지 (is_active = FALSE 처리)

**데이터 무결성 검증**:
```sql
-- 공정별 작업 데이터 수 확인
SELECT p.process_name, COUNT(pd.id) as work_count
FROM processes p
LEFT JOIN process_data pd ON p.id = pd.process_id
GROUP BY p.id, p.process_name
ORDER BY p.sequence_order;
```

**사용 예시**:
```sql
-- 특정 공정의 모든 작업 데이터 조회
SELECT pd.*
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE p.process_id = 'PROC-003'
ORDER BY pd.start_time DESC
LIMIT 100;
```

---

## 🔒 참조 무결성 제약조건

### ON DELETE RESTRICT 전략

**모든 FK에 RESTRICT 적용 이유**:
1. **데이터 보호**: 의도치 않은 Cascade Delete 방지
2. **추적성 유지**: 제조 이력 데이터 보존
3. **명시적 삭제**: 삭제 전 종속 데이터 확인 강제
4. **감사 요구사항**: 제조 데이터 보존 규정 준수

### 논리적 삭제 (Soft Delete)

물리적 삭제 대신 논리적 삭제 사용:

```sql
-- 제품 모델 단종
UPDATE product_models SET is_active = FALSE WHERE id = 1;

-- LOT 종료
UPDATE lots SET status = 'CLOSED', closed_at = NOW() WHERE id = 1;

-- 공정 비활성화
UPDATE processes SET is_active = FALSE WHERE id = 1;

-- 사용자 비활성화
UPDATE users SET is_active = FALSE WHERE id = 1;
```

---

## 📊 관계 카디널리티 요약

| 관계 | 카디널리티 | 평균 | 최대 | 제약 |
|------|----------|------|------|------|
| product_models → lots | 1:N | 1:5K | 무제한 | - |
| lots → serials | 1:N | 1:100 | 1:200 | target_quantity |
| lots → process_data | 1:N | 1:800 | 1:1.6K | - |
| serials → process_data | 1:N | 1:8 | 1:16 | 8공정 × 2(재작업) |
| processes → process_data | 1:N | 1:5M | 무제한 | - |

---

## 🔍 데이터 무결성 검증 쿼리 모음

### 1. 고아 레코드 (Orphan Records) 검증

```sql
-- lots 테이블 고아 레코드
SELECT COUNT(*) FROM lots l
LEFT JOIN product_models pm ON l.product_model_id = pm.id
WHERE pm.id IS NULL;

-- serials 테이블 고아 레코드
SELECT COUNT(*) FROM serials s
LEFT JOIN lots l ON s.lot_id = l.id
WHERE l.id IS NULL;

-- process_data 테이블 고아 레코드 (lot_id)
SELECT COUNT(*) FROM process_data pd
LEFT JOIN lots l ON pd.lot_id = l.id
WHERE l.id IS NULL;

-- process_data 테이블 고아 레코드 (serial_id, NULL 제외)
SELECT COUNT(*) FROM process_data pd
LEFT JOIN serials s ON pd.serial_id = s.id
WHERE pd.serial_id IS NOT NULL AND s.id IS NULL;

-- process_data 테이블 고아 레코드 (process_id)
SELECT COUNT(*) FROM process_data pd
LEFT JOIN processes p ON pd.process_id = p.id
WHERE p.id IS NULL;
```

### 2. 제약조건 위반 검증

```sql
-- LOT당 시리얼 수 초과 검증
SELECT lot_id, COUNT(*) as count, MAX(target_quantity) as target
FROM serials s
JOIN lots l ON s.lot_id = l.id
GROUP BY lot_id
HAVING COUNT(*) > MAX(target_quantity);

-- 시리얼 순번 중복 검증
SELECT lot_id, sequence, COUNT(*) as count
FROM serials
GROUP BY lot_id, sequence
HAVING COUNT(*) > 1;

-- 재작업 횟수 초과 검증
SELECT * FROM serials WHERE rework_count > 3;
```

### 3. 참조 무결성 통계

```sql
-- 테이블별 FK 참조 카운트
SELECT
    'lots' as table_name,
    COUNT(*) as total_records,
    COUNT(DISTINCT product_model_id) as distinct_parents
FROM lots
UNION ALL
SELECT
    'serials',
    COUNT(*),
    COUNT(DISTINCT lot_id)
FROM serials
UNION ALL
SELECT
    'process_data',
    COUNT(*),
    COUNT(DISTINCT lot_id)
FROM process_data;
```

---

## 📚 관련 문서

- [01-erd.md](01-erd.md) - ERD 다이어그램
- [02-entity-definitions.md](02-entity-definitions.md) - 테이블 상세 정의
- [04-business-rules.md](04-business-rules.md) - Trigger 기반 비즈니스 규칙

---

**마지막 업데이트**: 2025-01-17
