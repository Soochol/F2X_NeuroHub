# 인덱스 최적화 전략 (Index Strategy)

> F2X NeuroHub MES 데이터베이스 성능 최적화를 위한 인덱스 설계

## 🎯 인덱스 설계 원칙

1. **조회 패턴 기반**: 자주 사용되는 WHERE, JOIN, ORDER BY 컬럼
2. **카디널리티 고려**: 고유값이 많은 컬럼 우선
3. **복합 인덱스**: 여러 컬럼을 함께 조회하는 경우
4. **부분 인덱스**: WHERE 조건으로 데이터 범위 제한
5. **쓰기 성능 고려**: 인덱스가 많으면 INSERT/UPDATE 느려짐

---

## 📊 인덱스 목록 (총 30+개)

### lots 테이블 (6개)

| 인덱스명 | 타입 | 컬럼 | 목적 | 예상 효과 |
|---------|------|------|------|-----------|
| pk_lots | B-Tree | id | Primary Key | - |
| idx_lot_number | UNIQUE | lot_number | LOT 조회 | 100ms → 1ms |
| idx_lot_status | B-Tree | status | 상태별 LOT 목록 | 500ms → 50ms |
| idx_lot_created_at | B-Tree | created_at DESC | 최신 LOT 조회 | 300ms → 20ms |
| idx_lot_product_model | B-Tree | product_model_id | 모델별 LOT 조회 | 200ms → 10ms |
| idx_lot_status_created | Composite | status, created_at DESC | 상태+날짜 조회 | 500ms → 10ms |

**쿼리 예시**:
```sql
-- 진행 중인 LOT 최신순 조회 (idx_lot_status_created 사용)
SELECT * FROM lots
WHERE status = 'IN_PROGRESS'
ORDER BY created_at DESC
LIMIT 20;
-- Execution time: 10ms (before: 500ms)
```

---

### serials 테이블 (7개)

| 인덱스명 | 타입 | 컬럼 | 목적 | 예상 효과 |
|---------|------|------|------|-----------|
| pk_serials | B-Tree | id | Primary Key | - |
| idx_serial_number | UNIQUE | serial_number | 시리얼 추적 | 200ms → 1ms |
| idx_serial_lot | B-Tree | lot_id | LOT별 시리얼 조회 | 300ms → 10ms |
| idx_serial_status | B-Tree | status | 상태별 시리얼 조회 | 500ms → 50ms |
| idx_serial_lot_sequence | Composite | lot_id, sequence | LOT 내 순번 조회 | 200ms → 5ms |
| idx_serial_failed | Partial | lot_id, status WHERE status='FAILED' | 불량품 조회 | 1s → 50ms |
| idx_serial_rework | Partial | status WHERE status='REWORK' | 재작업 중 조회 | 800ms → 30ms |

**부분 인덱스 효과**:
```sql
-- 불량품 조회 (idx_serial_failed 사용)
SELECT * FROM serials
WHERE status = 'FAILED' AND lot_id = 1;
-- Index size: 1% of table (불량품만 인덱싱)
-- Execution time: 50ms (before: 1s)
```

---

### process_data 테이블 (13개)

| 인덱스명 | 타입 | 컬럼 | 목적 | 예상 효과 |
|---------|------|------|------|-----------|
| pk_process_data | B-Tree | id | Primary Key | - |
| idx_process_data_lot | B-Tree | lot_id | LOT별 조회 | 500ms → 20ms |
| idx_process_data_serial | B-Tree | serial_id | 시리얼별 조회 | 500ms → 20ms |
| idx_process_data_process | B-Tree | process_id | 공정별 조회 | 1s → 50ms |
| idx_process_data_line | B-Tree | line_id | 라인별 조회 | 800ms → 40ms |
| idx_process_data_equipment | B-Tree | equipment_id | 설비별 조회 | 800ms → 40ms |
| idx_process_data_time | B-Tree | start_time DESC | 시간 역순 조회 | 500ms → 30ms |
| idx_process_data_serial_process | Composite | serial_id, process_id | 공정 순서 검증 | 2s → 10ms |
| idx_process_data_incomplete | Partial | serial_id, process_id WHERE complete_time IS NULL | 미완료 공정 조회 | 3s → 50ms |
| idx_process_data_completed | Composite | complete_time DESC, result WHERE complete_time IS NOT NULL | 완공 데이터 조회 | 2s → 100ms |
| idx_process_data_jsonb | GIN | process_specific_data | JSONB 검색 | 5s → 100ms |
| idx_process_data_rework | Partial | is_rework WHERE is_rework = TRUE | 재작업 조회 | 1s → 30ms |

**GIN 인덱스 활용**:
```sql
-- JSONB 검색 (idx_process_data_jsonb 사용)
SELECT * FROM process_data
WHERE process_specific_data @> '{"temp_sensor": {"result": "FAIL"}}'::jsonb;
-- Execution time: 100ms (before: 5s)
```

---

### product_models 테이블 (3개)

| 인덱스명 | 타입 | 컬럼 | 목적 |
|---------|------|------|------|
| pk_product_models | B-Tree | id | Primary Key |
| idx_product_models_code | UNIQUE | model_code | 모델 코드 조회 |
| idx_product_models_active | Partial | is_active WHERE is_active = TRUE | 활성화된 모델만 |

---

### processes 테이블 (4개)

| 인덱스명 | 타입 | 컬럼 | 목적 |
|---------|------|------|------|
| pk_processes | B-Tree | id | Primary Key |
| idx_process_id | UNIQUE | process_id | 공정 ID 조회 |
| idx_process_sequence | UNIQUE | sequence_order | 공정 순서 조회 |
| idx_process_active | Partial | is_active WHERE is_active = TRUE | 활성화된 공정만 |

---

### users 테이블 (5개)

| 인덱스명 | 타입 | 컬럼 | 목적 |
|---------|------|------|------|
| pk_users | B-Tree | id | Primary Key |
| idx_user_id | UNIQUE | user_id | 사용자 ID 조회 |
| idx_user_email | UNIQUE | email | 이메일 조회 |
| idx_user_role | B-Tree | role | 역할별 조회 |
| idx_user_active | Partial | is_active WHERE is_active = TRUE | 활성화된 사용자만 |

---

### audit_logs 테이블 (6개)

| 인덱스명 | 타입 | 컬럼 | 목적 |
|---------|------|------|------|
| pk_audit_logs | B-Tree | id | Primary Key |
| idx_audit_table | B-Tree | table_name | 테이블별 조회 |
| idx_audit_time | B-Tree | created_at DESC | 시간 역순 조회 |
| idx_audit_user | B-Tree | user_id | 사용자별 조회 |
| idx_audit_action | B-Tree | action | 작업 유형별 조회 |
| idx_audit_record | Composite | table_name, record_id | 레코드 이력 조회 |

---

### firmware_versions 테이블 (4개)

| 인덱스명 | 타입 | 컬럼 | 목적 |
|---------|------|------|------|
| pk_firmware_versions | B-Tree | id | Primary Key |
| idx_firmware_version | UNIQUE | version | 버전 조회 |
| idx_firmware_active | Partial | is_active WHERE is_active = TRUE | 현재 배포 버전 |
| idx_firmware_released | B-Tree | released_at DESC | 최신 버전 조회 |

---

## 📐 인덱스 유형 설명

### 1. B-Tree Index (기본)
- **용도**: 일반적인 조회, 정렬, 범위 검색
- **장점**: 빠른 조회, ORDER BY 최적화
- **단점**: 쓰기 성능 저하 (INSERT/UPDATE 시)

### 2. Unique Index
- **용도**: 중복 방지 (lot_number, serial_number 등)
- **장점**: 데이터 무결성 + 조회 성능
- **단점**: INSERT 시 중복 검사 오버헤드

### 3. Composite Index (복합 인덱스)
- **용도**: 여러 컬럼을 함께 조회
- **장점**: 복합 조건 쿼리 최적화
- **단점**: 인덱스 크기 증가

**인덱스 순서 중요**:
```sql
-- ✅ CORRECT: (status, created_at)
SELECT * FROM lots WHERE status = 'IN_PROGRESS' ORDER BY created_at DESC;
-- Uses idx_lot_status_created efficiently

-- ❌ WRONG: (created_at, status)
-- Cannot use index efficiently for "WHERE status =" clause
```

### 4. Partial Index (부분 인덱스)
- **용도**: 특정 조건의 데이터만 인덱싱
- **장점**: 인덱스 크기 감소, 쓰기 성능 향상
- **단점**: 조건에 맞지 않는 쿼리는 사용 불가

**예시**:
```sql
-- Partial Index
CREATE INDEX idx_serial_failed ON serials(lot_id, status)
WHERE status = 'FAILED';

-- Index size: ~1% of table (불량품만)
-- vs Full Index: 100% of table
```

### 5. GIN Index (Generalized Inverted Index)
- **용도**: JSONB, 배열, 전문 검색
- **장점**: JSONB 검색 빠름
- **단점**: 쓰기 성능 큰 저하

**JSONB 쿼리**:
```sql
-- GIN 인덱스 사용
SELECT * FROM process_data
WHERE process_specific_data @> '{"검사결과": "FAIL"}'::jsonb;

-- GIN 인덱스 미사용 (Seq Scan)
SELECT * FROM process_data
WHERE process_specific_data->>'검사결과' = 'FAIL';
```

---

## ⚡ 성능 최적화 사례

### 사례 1: LOT 조회 최적화

**Before (No Index)**:
```sql
SELECT * FROM lots
WHERE status = 'IN_PROGRESS'
ORDER BY created_at DESC
LIMIT 20;

-- Execution Plan: Seq Scan + Sort
-- Execution Time: 500ms (50,000 rows scan)
```

**After (Composite Index)**:
```sql
CREATE INDEX idx_lot_status_created ON lots(status, created_at DESC);

-- Execution Plan: Index Scan
-- Execution Time: 10ms (20 rows scan)
-- Performance Improvement: 50x
```

---

### 사례 2: 불량품 조회 최적화

**Before (Full Index)**:
```sql
CREATE INDEX idx_serial_status ON serials(status);

-- Index Size: 100% of table (5M rows)
-- Write Performance: -20%
```

**After (Partial Index)**:
```sql
CREATE INDEX idx_serial_failed ON serials(lot_id, status)
WHERE status = 'FAILED';

-- Index Size: 1% of table (50K rows, 불량률 1%)
-- Write Performance: -2% (부분 인덱스 크기 작음)
-- Query Performance: Same as full index
```

---

### 사례 3: JSONB 검색 최적화

**Before (No GIN Index)**:
```sql
SELECT * FROM process_data
WHERE process_specific_data @> '{"temp_sensor": {"result": "FAIL"}}'::jsonb;

-- Execution Plan: Seq Scan
-- Execution Time: 5s (40M rows scan)
```

**After (GIN Index)**:
```sql
CREATE INDEX idx_process_data_jsonb ON process_data
USING GIN (process_specific_data);

-- Execution Plan: Bitmap Index Scan
-- Execution Time: 100ms
-- Performance Improvement: 50x
```

---

## 🔧 인덱스 모니터링

### 1. 인덱스 사용 통계

```sql
-- 인덱스 사용 빈도 확인
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,  -- 인덱스 스캔 횟수
    idx_tup_read,  -- 읽은 튜플 수
    idx_tup_fetch  -- 실제 반환된 튜플 수
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### 2. 사용되지 않는 인덱스 확인

```sql
-- 사용 안 된 인덱스 (삭제 고려)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname = 'public'
AND indexrelid IS NOT NULL;
```

### 3. 인덱스 블로트 (Bloat) 확인

```sql
-- 인덱스 재구축 필요 여부
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan,
    idx_tup_read / NULLIF(idx_scan, 0) as avg_tuples_per_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 📚 관련 문서

- [02-entity-definitions.md](02-entity-definitions.md) - 테이블 정의
- [06-migration-plan.md](06-migration-plan.md) - 인덱스 마이그레이션

---

**마지막 업데이트**: 2025-01-17
