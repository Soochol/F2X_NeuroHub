# Database 요구사항 문서 (Database Requirements)

> F2X NeuroHub MES 데이터베이스 설계 및 구현을 위한 완벽한 참고 자료

---

## 📚 문서 목차

### 1. [DATABASE-REQUIREMENTS.md](./DATABASE-REQUIREMENTS.md) - 통합 요구사항 문서

**종류**: 메인 기술 명세서
**범위**: 데이터베이스 전체 설계, 스키마, 비즈니스 규칙

**내용**:
- **Section 1**: 기술 스택 및 성능 요구사항
- **Section 2**: 테이블 구조 및 예상 데이터량
- **Section 3**: 상세 스키마 (11개 테이블 DDL)
- **Section 4**: Foreign Key 관계 명세
- **Section 5**: 인덱스 전략 및 최적화
- **Section 6**: 비즈니스 규칙 (BR-001 ~ BR-010)
- **Section 7**: JSONB 데이터 구조
- **Section 8**: 마이그레이션 및 초기화
- **Section 9**: 데이터 보관 및 백업
- **Section 10**: 비기능 요구사항

**활용처**:
- 초기 데이터베이스 설계 및 구현
- 전체 시스템 이해를 위한 핵심 문서
- 개발자 온보딩 가이드

---

### 2. [01-ERD.md](./01-ERD.md) - Entity Relationship Diagram

**종류**: 시각적 설계 문서
**범위**: 테이블 간 관계도, 카디널리티

**내용**:
- ERD 다이어그램 (Mermaid)
- 테이블 간 관계 및 FK
- 카디널리티 명시

**활용처**:
- 데이터모델 전체 구조 이해
- 데이터베이스 정규화 검증
- 개발 팀 소통 및 설계 리뷰

---

### 3. [02-entity-definitions.md](./02-entity-definitions.md) - 엔티티 상세 정의

**종류**: 테이블 명세 문서
**범위**: 개별 테이블의 컬럼, 제약조건, 인덱스

**내용**:
- 11개 테이블 상세 정의
- 각 테이블별 컬럼 설명
- PRIMARY KEY, FOREIGN KEY, CHECK 제약조건
- 기본값(Default) 및 NULL 정책
- 관련 트리거 및 함수

**테이블 커버리지**:
- product_models (제품 모델)
- lots (생산 LOT)
- serials (시리얼 번호)
- processes (공정)
- process_data (공정 데이터)
- wip_items (WIP 항목) ⭐ NEW
- wip_process_history (WIP 공정 이력) ⭐ NEW
- users (사용자)
- audit_logs (감사 로그)
- production_lines (생산 라인)
- equipment (설비)

**활용처**:
- 개별 테이블 구조 이해
- ORM 모델 정의 참고
- 쿼리 작성 및 데이터 삽입 가이드

---

### 4. [03-relationship-specifications.md](./03-relationship-specifications.md) - 관계 명세

**종류**: 관계형 설계 문서
**범위**: Foreign Key 관계, 카디널리티, Cascade 정책

**내용**:
- 모든 Foreign Key 관계 목록
- 삭제 전략 (CASCADE, RESTRICT, SET NULL)
- JOIN 경로 및 최적화
- 순환 참조 여부 확인

**활용처**:
- 데이터 삭제 정책 이해
- 복잡한 조인 쿼리 설계
- 데이터 무결성 검증

---

### 5. [04-index-strategy.md](./04-index-strategy.md) - 인덱스 최적화 전략

**종류**: 성능 최적화 문서
**범위**: 40+개 인덱스 설계, 성능 기준

**내용**:
- B-Tree, Unique, Composite, Partial, GIN 인덱스
- 각 테이블별 인덱스 목록
- 성능 개선 효과 (Before/After)
- 인덱스 생성 SQL
- 인덱스 모니터링 쿼리

**핵심 인덱스**:
- lots: 6개 (상태, 생성일시, 활성 LOT)
- serials: 7개 (시리얼, LOT, 불량)
- process_data: 13개 (공정, JSONB, 미완료)
- wip_items: 6개 (LOT, 상태, 활성 WIP) ⭐ NEW
- wip_process_history: 4개 (WIP, 공정, 이력) ⭐ NEW
- 기타 테이블: 4+개 (사용자, 감사, 펌웨어)

**활용처**:
- 쿼리 성능 최적화
- 인덱스 선택 기준 이해
- 데이터베이스 튜닝

---

### 6. [05-migration-plan.md](./05-migration-plan.md) - Alembic 마이그레이션 계획

**종류**: 배포 자동화 문서
**범위**: 6개 마이그레이션 버전, 실행 절차

**내용**:
- 마이그레이션 전략 (Alembic)
- 6개 버전별 상세 계획
  - 001: Initial Schema (6개 테이블)
  - 002: Add Triggers (8개 Function)
  - 003: Add Audit Logs
  - 004: Add Indexes (30+개)
  - 005: Add Firmware Table
  - 006: Add WIP Tables ⭐ NEW
- 실행 명령어 (개발/운영)
- 주의사항 및 롤백 전략
- 마이그레이션 모니터링

**활용처**:
- 개발/스테이징/운영 환경 배포
- 데이터베이스 버전 관리
- 마이그레이션 실패 시 대응

---

### 7. [06-data-dictionary.md](./06-data-dictionary.md) - 데이터 사전

**종류**: 컬럼 참조 문서
**범위**: 107개 컬럼 상세 정의

**내용**:
- 알파벳 순 컬럼 사전
- 데이터 타입, NULL 정책
- 제약조건 및 기본값
- 인덱스 할당 여부
- 비즈니스 규칙 참조

**컬럼 커버리지**:
- 기존: 83개 컬럼
- WIP 추가: +24개 컬럼
- 총: 107개 컬럼

**활용처**:
- 특정 컬럼 속성 빠른 검색
- SQL 쿼리 작성 시 참고
- 데이터 타입 및 제약 확인
- API 응답 스키마 설계

---

## 🎯 사용 시나리오별 가이드

### 시나리오 1: 데이터베이스 처음 구축

1. **DATABASE-REQUIREMENTS.md** 전체 읽기
2. **01-ERD.md**로 구조 시각화
3. **02-entity-definitions.md**로 각 테이블 상세 이해
4. **05-migration-plan.md** 실행

```bash
# 마이그레이션 실행
alembic upgrade head
```

---

### 시나리오 2: 새로운 쿼리 작성

1. **04-index-strategy.md**에서 관련 인덱스 확인
2. **06-data-dictionary.md**에서 컬럼 속성 조회
3. **03-relationship-specifications.md**에서 JOIN 경로 확인
4. 최적 쿼리 작성

---

### 시나리오 3: 성능 문제 진단

1. **04-index-strategy.md**에서 인덱스 전략 검토
2. **DATABASE-REQUIREMENTS.md** Section 5 참고
3. 부족한 인덱스 생성
4. 쿼리 재작성

---

### 시나리오 4: 비즈니스 규칙 구현

1. **DATABASE-REQUIREMENTS.md** Section 6에서 해당 BR 찾기
2. Trigger/Function SQL 코드 참고
3. 또는 **05-migration-plan.md**에서 마이그레이션 버전 확인
4. API/애플리케이션 로직 구현

---

### 시나리오 5: 개발자 온보딩

**권장 읽기 순서**:

1. DATABASE-REQUIREMENTS.md (30분)
2. 01-ERD.md (10분)
3. 02-entity-definitions.md (1시간)
4. 04-index-strategy.md (30분)
5. 06-data-dictionary.md (필요할 때마다 참조)

**예상 학습 시간**: 2-3시간

---

## 📊 문서 통계

| 문서 | 라인 수 | 테이블 | 섹션 | 코드블록 |
|------|--------|--------|------|---------|
| DATABASE-REQUIREMENTS.md | 700+ | 20+ | 10 | 15+ |
| 01-ERD.md | 100+ | - | 2 | 1 (Mermaid) |
| 02-entity-definitions.md | 600+ | 11 | 11 | 50+ |
| 03-relationship-specifications.md | 200+ | 5 | 4 | 10+ |
| 04-index-strategy.md | 400+ | 10+ | 8 | 30+ |
| 05-migration-plan.md | 480+ | 5+ | 9 | 20+ |
| 06-data-dictionary.md | 433+ | 10+ | 15 | 5+ |
| **총합** | **3,400+** | **61+** | **58** | **131+** |

---

## 🔄 관계 다이어그램

```
┌─────────────────────────────────────────┐
│   DATABASE-REQUIREMENTS.md              │
│   (통합 기술 명세서)                     │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ↓         ↓         ↓
┌────────┐ ┌────────┐ ┌──────────┐
│ 01-ERD │ │ 02-    │ │ 03-      │
│        │ │ Entity │ │ Relations│
└────────┘ └────────┘ └──────────┘
    │         │         │
    └─────────┼─────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ↓         ↓         ↓
┌────────┐ ┌────────┐ ┌──────────┐
│ 04-    │ │ 05-    │ │ 06-      │
│ Index  │ │Migrtn  │ │Dictionary│
└────────┘ └────────┘ └──────────┘
```

---

## 🔐 WIP 시스템 통합

모든 문서는 WIP (Work-In-Progress) 추적 시스템을 반영하고 있습니다:

### 신규 테이블 (v006 마이그레이션)
- **wip_items**: 공정 1-6 중 제품 추적 (최대 100개/LOT)
- **wip_process_history**: WIP 공정 단계별 이력 기록

### 신규 인덱스 (10개)
- wip_items: 6개 (LOT, 상태, 활성, 완료)
- wip_process_history: 4개 (WIP, 공정, 이력)

### 신규 컬럼 (24개)
- wip_id, status, completed_at, converted_at, sequence_in_lot 등
- 상세: [06-data-dictionary.md](./06-data-dictionary.md) 참조

---

## 📝 버전 관리

| 버전 | 변경 내용 | 날짜 |
|------|---------|------|
| v1.0 | 초기 데이터베이스 설계 | 2025-01-17 |
| v2.0 | WIP 시스템 추가 | 2025-11-21 |
| v2.1 | 문서 통합 및 정리 | 2025-11-21 |

---

## 🤝 기여 가이드

문서를 업데이트할 때:

1. **DATABASE-REQUIREMENTS.md** 먼저 업데이트
2. 변경 사항을 다른 문서에 동기화:
   - 스키마 변경 → 02-entity-definitions.md
   - 관계 변경 → 03-relationship-specifications.md
   - 인덱스 변경 → 04-index-strategy.md
   - 컬럼 변경 → 06-data-dictionary.md
   - 마이그레이션 버전 → 05-migration-plan.md
3. ERD 다이어그램 업데이트 → 01-ERD.md

---

## ✅ 문서 체크리스트

배포 전 확인 사항:

- [ ] 모든 테이블이 문서에 포함되었는가?
- [ ] 모든 Foreign Key가 명시되었는가?
- [ ] 마이그레이션 버전이 최신인가?
- [ ] 인덱스 목록이 최신인가?
- [ ] 컬럼 사전이 최신인가?
- [ ] 내부 링크가 모두 유효한가?
- [ ] ERD 다이어그램이 정확한가?

---

**마지막 업데이트**: 2025-11-21
**관리자**: F2X NeuroHub 개발팀
**문의**: database-team@withforce.com
