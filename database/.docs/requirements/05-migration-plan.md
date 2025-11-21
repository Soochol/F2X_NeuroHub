# 마이그레이션 계획 (Migration Plan)

> F2X NeuroHub MES 데이터베이스 Alembic 마이그레이션 단계별 실행 계획

## 🎯 마이그레이션 전략

- **도구**: Alembic (SQLAlchemy ORM)
- **버전 관리**: Git으로 마이그레이션 파일 추적
- **롤백 계획**: 모든 마이그레이션에 `downgrade()` 구현
- **테스트**: 로컬 → 스테이징 → 운영 순차 적용
- **백업**: 마이그레이션 전 필수 백업

---

## 📋 마이그레이션 버전 계획

| 버전 | 파일명 | 설명 | 예상 시간 | 위험도 | 롤백 |
|------|--------|------|----------|--------|------|
| 001 | initial_schema.py | 핵심 6개 테이블 생성 | 5분 | 낮음 | ✅ |
| 002 | add_triggers.py | Trigger/Function 8개 추가 | 10분 | 중간 | ✅ |
| 003 | add_audit_logs.py | 감사 로그 테이블 | 5분 | 낮음 | ✅ |
| 004 | add_indexes.py | 성능 인덱스 30+개 추가 | 30분 | 중간 | ✅ |
| 005 | add_firmware_table.py | 펌웨어 관리 테이블 | 2분 | 낮음 | ✅ |
| 006 | add_wip_tables.py | WIP 추적 테이블 2개 추가 ⭐ **NEW** | 5분 | 낮음 | ✅ |

**총 예상 시간**: 57분

---

## 001: Initial Schema

### 목적
핵심 6개 테이블 생성 및 Seed Data 삽입

### 포함 내용
1. `product_models` 테이블
2. `lots` 테이블
3. `serials` 테이블
4. `processes` 테이블
5. `process_data` 테이블
6. `users` 테이블
7. 기본 인덱스 (PK, UNIQUE, FK)
8. Seed Data:
   - processes (8개 공정)
   - product_models (WF 모델)
   - users (admin 계정)

### DDL 예시
```python
"""Initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create product_models
    op.create_table(
        'product_models',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('model_code', sa.String(50), nullable=False),
        sa.Column('model_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_code')
    )

    # Create lots
    op.create_table(
        'lots',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_number', sa.String(50), nullable=False),
        sa.Column('product_model_id', sa.BigInteger(), nullable=False),
        sa.Column('target_quantity', sa.Integer(), server_default='100', nullable=False),
        sa.Column('shift', sa.CHAR(1), nullable=False),
        sa.Column('status', sa.String(20), server_default='CREATED', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('closed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_model_id'], ['product_models.id'], ondelete='RESTRICT'),
        sa.UniqueConstraint('lot_number'),
        sa.CheckConstraint("shift IN ('D', 'N')", name='chk_lot_shift'),
        sa.CheckConstraint("status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED')", name='chk_lot_status')
    )

    # ... (serials, processes, process_data, users 테이블 생성)

    # Seed Data
    op.execute("""
        INSERT INTO product_models (model_code, model_name, description) VALUES
        ('WF', 'Withforce Wearable Robot', '산업용/농업용 허리 보조 로봇');
    """)

    op.execute("""
        INSERT INTO processes (process_id, process_name, sequence_order, estimated_duration_seconds) VALUES
        ('PROC-001', '레이저 마킹', 1, 60),
        ('PROC-002', 'LMA 조립', 2, 3600),
        ('PROC-003', '센서 검사', 3, 60),
        ('PROC-004', '펌웨어 업로드', 4, 60),
        ('PROC-005', '로봇 조립', 5, 3600),
        ('PROC-006', '성능검사', 6, 600),
        ('PROC-007', '라벨 프린팅', 7, 40),
        ('PROC-008', '포장+외관검사', 8, 120);
    """)

    op.execute("""
        INSERT INTO users (user_id, username, email, password_hash, role) VALUES
        ('admin', '시스템 관리자', 'admin@withforce.com', '$2b$12$...', 'ADMIN');
    """)

def downgrade() -> None:
    op.drop_table('process_data')
    op.drop_table('serials')
    op.drop_table('processes')
    op.drop_table('lots')
    op.drop_table('product_models')
    op.drop_table('users')
```

### 실행 명령
```bash
alembic upgrade 001_initial_schema
```

### 검증
```sql
-- 테이블 생성 확인
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Seed Data 확인
SELECT COUNT(*) FROM processes;  -- 8
SELECT COUNT(*) FROM product_models;  -- 1
SELECT COUNT(*) FROM users;  -- 1
```

---

## 002: Add Triggers

### 목적
비즈니스 규칙 Trigger 및 Function 8개 추가

### 포함 내용
1. BR-001: LOT 상태 전이 검증
2. BR-002: 공정 순서 제어
3. BR-003: 시리얼 상태 자동 업데이트
4. BR-004: 시리얼 생성 제한
5. BR-005: 재작업 횟수 제한
6. BR-007: LOT 자동 IN_PROGRESS
7. BR-008: updated_at 자동 갱신

### 실행 명령
```bash
alembic upgrade 002_add_triggers
```

### 검증
```sql
-- Trigger 목록 확인
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public';

-- Trigger 동작 테스트
INSERT INTO lots (lot_number, product_model_id, shift) VALUES ('TEST-001', 1, 'D');
INSERT INTO serials (serial_number, lot_id, sequence) VALUES ('TEST-001-0001', 1, 1);

-- LOT 상태가 IN_PROGRESS로 자동 전환되었는지 확인
SELECT status FROM lots WHERE lot_number = 'TEST-001';  -- IN_PROGRESS
```

---

## 003: Add Audit Logs

### 목적
감사 로그 테이블 및 Trigger 추가

### 포함 내용
1. `audit_logs` 테이블 생성
2. BR-006: 감사 로그 자동 생성 Trigger
3. 주요 테이블에 Trigger 적용 (lots, serials, process_data, users)

### 실행 명령
```bash
alembic upgrade 003_add_audit_logs
```

### 검증
```sql
-- audit_logs 테이블 확인
SELECT COUNT(*) FROM audit_logs;

-- Trigger 동작 테스트
UPDATE lots SET status = 'COMPLETED' WHERE lot_number = 'TEST-001';

-- 감사 로그 확인
SELECT * FROM audit_logs
WHERE table_name = 'lots' AND action = 'UPDATE'
ORDER BY created_at DESC LIMIT 1;
```

---

## 004: Add Indexes

### 목적
성능 최적화 인덱스 30+개 추가

### 포함 내용
1. lots: 6개 인덱스
2. serials: 7개 인덱스
3. process_data: 13개 인덱스
4. 기타 테이블: 4+개 인덱스

### 인덱스 생성 순서 (중요도 순)
```python
def upgrade() -> None:
    # 1. UNIQUE 인덱스 (데이터 무결성)
    op.create_index('idx_lot_number', 'lots', ['lot_number'], unique=True)
    op.create_index('idx_serial_number', 'serials', ['serial_number'], unique=True)

    # 2. FK 인덱스 (JOIN 성능)
    op.create_index('idx_serial_lot', 'serials', ['lot_id'])
    op.create_index('idx_process_data_lot', 'process_data', ['lot_id'])
    op.create_index('idx_process_data_serial', 'process_data', ['serial_id'])

    # 3. 복합 인덱스 (복합 조건 쿼리)
    op.create_index('idx_lot_status_created', 'lots', ['status', sa.text('created_at DESC')])
    op.create_index('idx_process_data_serial_process', 'process_data', ['serial_id', 'process_id'])

    # 4. 부분 인덱스 (특정 조건)
    op.execute("""
        CREATE INDEX idx_serial_failed ON serials(lot_id, status)
        WHERE status = 'FAILED';
    """)

    op.execute("""
        CREATE INDEX idx_process_data_incomplete ON process_data(serial_id, process_id)
        WHERE complete_time IS NULL;
    """)

    # 5. GIN 인덱스 (JSONB)
    op.execute("""
        CREATE INDEX idx_process_data_jsonb ON process_data
        USING GIN (process_specific_data);
    """)
```

### 실행 명령
```bash
alembic upgrade 004_add_indexes
```

### 검증
```sql
-- 인덱스 목록 확인
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- 총 인덱스 수 확인
SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';
-- Expected: 30+
```

### 예상 시간
- 빈 테이블: 5분
- 데이터 100만 rows: 15분
- 데이터 1000만 rows: 30분

---

## 005: Add Firmware Table

### 목적
펌웨어 버전 관리 테이블 추가

### 포함 내용
1. `firmware_versions` 테이블
2. 인덱스 4개

### 실행 명령
```bash
alembic upgrade 005_add_firmware_table
```

---

## 006: Add WIP Tables ⭐ **NEW**

### 목적
WIP (Work-In-Progress) 추적 시스템을 위한 2개 테이블 및 인덱스 추가

### 포함 내용
1. `wip_items` 테이블 - 공정 1-6 동안 제품 추적
2. `wip_process_history` 테이블 - 각 공정 단계별 이력
3. 인덱스 10개 (성능 최적화)

### DDL 예시
```python
"""Add WIP tracking tables

Revision ID: 006_add_wip_tables
Revises: 005_add_firmware_table
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa

revision = '006_add_wip_tables'
down_revision = '005_add_firmware_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create wip_items table
    op.create_table(
        'wip_items',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wip_id', sa.String(19), nullable=False),  # WIP-{LOT}-{SEQ}
        sa.Column('lot_id', sa.BigInteger(), nullable=False),
        sa.Column('serial_id', sa.BigInteger(), nullable=True),
        sa.Column('sequence_in_lot', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), server_default='CREATED', nullable=False),
        sa.Column('current_process_id', sa.BigInteger(), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('converted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['serial_id'], ['serials.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['current_process_id'], ['processes.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('wip_id'),
        sa.CheckConstraint(
            "status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CONVERTED')",
            name='chk_wip_status'
        )
    )

    # Create wip_process_history table
    op.create_table(
        'wip_process_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wip_item_id', sa.BigInteger(), nullable=False),
        sa.Column('process_id', sa.BigInteger(), nullable=False),
        sa.Column('operator_id', sa.BigInteger(), nullable=False),
        sa.Column('equipment_id', sa.BigInteger(), nullable=True),
        sa.Column('result', sa.String(20), nullable=False),  # PASS, FAIL, REWORK
        sa.Column('measurements', sa.JSON(), server_default='{}', nullable=False),
        sa.Column('defects', sa.JSON(), server_default='[]', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['wip_item_id'], ['wip_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='SET NULL', name='fk_equipment'),
        sa.CheckConstraint(
            "result IN ('PASS', 'FAIL', 'REWORK')",
            name='chk_process_result'
        )
    )

    # Create indexes for wip_items (6 indexes)
    op.create_index('idx_wip_items_lot', 'wip_items', ['lot_id'])
    op.create_index('idx_wip_items_serial', 'wip_items', ['serial_id'])
    op.create_index('idx_wip_items_status', 'wip_items', ['status'])
    op.create_index('idx_wip_items_current_process', 'wip_items', ['current_process_id'])

    # Composite index for active WIP
    op.create_index(
        'idx_wip_items_active',
        'wip_items',
        ['lot_id', 'status']
    )

    # Partial index for completed WIP
    op.execute("""
        CREATE INDEX idx_wip_items_completed_at ON wip_items(completed_at)
        WHERE completed_at IS NOT NULL;
    """)

    # Create indexes for wip_process_history (4 indexes)
    op.create_index('idx_wip_process_history_wip_item', 'wip_process_history', ['wip_item_id'])
    op.create_index('idx_wip_process_history_process', 'wip_process_history', ['process_id'])
    op.create_index('idx_wip_process_history_operator', 'wip_process_history', ['operator_id'])

    # Composite index for WIP process history lookup
    op.create_index(
        'idx_wip_process_history_composite',
        'wip_process_history',
        ['wip_item_id', 'process_id', sa.text('created_at DESC')]
    )

def downgrade() -> None:
    op.drop_index('idx_wip_process_history_composite')
    op.drop_index('idx_wip_process_history_operator')
    op.drop_index('idx_wip_process_history_process')
    op.drop_index('idx_wip_process_history_wip_item')
    op.drop_index('idx_wip_items_completed_at')
    op.drop_index('idx_wip_items_active')
    op.drop_index('idx_wip_items_current_process')
    op.drop_index('idx_wip_items_status')
    op.drop_index('idx_wip_items_serial')
    op.drop_index('idx_wip_items_lot')
    op.drop_table('wip_process_history')
    op.drop_table('wip_items')
```

### 실행 명령
```bash
alembic upgrade 006_add_wip_tables
```

### 검증
```sql
-- WIP 테이블 생성 확인
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name IN ('wip_items', 'wip_process_history');

-- WIP 인덱스 확인
SELECT indexname FROM pg_indexes
WHERE schemaname = 'public' AND tablename IN ('wip_items', 'wip_process_history')
ORDER BY indexname;
-- Expected: 10 indexes

-- 테이블 구조 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'wip_items'
ORDER BY ordinal_position;
```

### WIP 테이블 통계
```sql
-- WIP 상태 분포
SELECT
    status,
    COUNT(*) as count
FROM wip_items
GROUP BY status;

-- 공정별 완료 통계
SELECT
    p.process_name,
    COUNT(CASE WHEN wph.result = 'PASS' THEN 1 END) as pass_count,
    COUNT(CASE WHEN wph.result = 'FAIL' THEN 1 END) as fail_count,
    COUNT(CASE WHEN wph.result = 'REWORK' THEN 1 END) as rework_count
FROM wip_process_history wph
JOIN processes p ON wph.process_id = p.id
GROUP BY p.process_name
ORDER BY p.sequence_order;
```

### 예상 시간
- 테이블 생성: 1분
- 인덱스 생성: 2분
- 검증: 2분
- **총**: 5분

---

## 🔄 마이그레이션 실행 절차

### 개발 환경

```bash
# 1. 가상 환경 활성화
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 2. Alembic 설정 확인
cat alembic.ini  # DB URL 확인

# 3. 현재 버전 확인
alembic current

# 4. 마이그레이션 파일 생성 (자동)
alembic revision --autogenerate -m "Add new feature"

# 5. 마이그레이션 적용
alembic upgrade head

# 6. 롤백 (최신 버전)
alembic downgrade -1

# 7. 특정 버전으로 이동
alembic upgrade 006_add_wip_tables
```

### 운영 환경

```bash
# 1. 백업 생성 (필수!)
pg_dump -U postgres neurohub_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 마이그레이션 검증 (Dry-run)
alembic upgrade head --sql > migration.sql
cat migration.sql  # SQL 검토

# 3. 마이그레이션 적용
alembic upgrade head

# 4. 검증
psql -U postgres -d neurohub_db -c "SELECT * FROM alembic_version;"

# 5. 롤백 계획 준비 (사전 작성)
alembic downgrade -1 --sql > rollback.sql
```

---

## ⚠️ 주의사항

### 1. 마이그레이션 전 체크리스트

- [ ] 데이터베이스 백업 완료
- [ ] 롤백 SQL 작성 완료
- [ ] 스테이징 환경 테스트 완료
- [ ] 마이그레이션 예상 시간 확인
- [ ] 서비스 중단 계획 수립 (필요 시)
- [ ] 팀원 통지 완료

### 2. 큰 테이블 인덱스 생성 시

```sql
-- CONCURRENTLY 옵션 사용 (락 최소화)
CREATE INDEX CONCURRENTLY idx_process_data_lot ON process_data(lot_id);

-- 장점: 테이블 락 없음, 서비스 중단 없음
-- 단점: 생성 시간 2배 증가
```

### 3. 마이그레이션 실패 시

```bash
# 1. 현재 상태 확인
alembic current

# 2. 마이그레이션 히스토리 확인
alembic history

# 3. 롤백
alembic downgrade -1

# 4. 백업 복원 (최악의 경우)
psql -U postgres -d neurohub_db < backup_20250117_100000.sql
```

---

## 📊 마이그레이션 모니터링

### 진행 상황 확인

```sql
-- 현재 버전 확인
SELECT version_num FROM alembic_version;

-- 테이블 수 확인
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public';

-- 인덱스 수 확인
SELECT COUNT(*) FROM pg_indexes
WHERE schemaname = 'public';

-- Trigger 수 확인
SELECT COUNT(*) FROM information_schema.triggers
WHERE trigger_schema = 'public';
```

---

## 📚 관련 문서

- [README.md](./README.md) - 문서 가이드
- [DATABASE-REQUIREMENTS.md](./DATABASE-REQUIREMENTS.md) - 통합 데이터베이스 요구사항
- [02-entity-definitions.md](./02-entity-definitions.md) - 테이블 DDL
- [04-index-strategy.md](./04-index-strategy.md) - 인덱스 최적화 전략
- [06-data-dictionary.md](./06-data-dictionary.md) - 데이터 사전

---

**마지막 업데이트**: 2025-11-21
