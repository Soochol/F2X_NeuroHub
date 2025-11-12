# Multi-Agent TDD Development System - 사용 가이드

AI 기반 자동화된 TDD (Test-Driven Development) 파이프라인

## 🎯 시스템 개요

이 시스템은 Claude AI 에이전트들을 활용하여 요구사항부터 배포까지 전체 개발 프로세스를 자동화합니다.

### 핵심 원리

```
Agent = Senior Developer (직접 코딩)
```

- **각 Agent**: 베스트 프랙티스 가이드 + 실제 코드 작성
- **No YAML**: 중간 사양 없이 바로 코드 생성 (38% 토큰 절감)
- **6개 Agent**: requirements → design → implementation → testing → deployment → verification

## 🚀 빠른 시작

### 완전 자동화된 개발 파이프라인

```bash
/full
```

입력 예시:
```
"재고 조회 기능: 작업자가 SKU 코드로 재고 수량을 조회할 수 있어야 함"
```

이 명령은 자동으로:
1. ✅ **Requirements** - FR 문서 생성 (Given-When-Then AC)
2. ✅ **Design** - API 사양, DB 스키마, 아키텍처 설계
3. ✅ **TDD Red** - 실패하는 테스트 먼저 작성 (pytest → FAIL)
4. ✅ **TDD Green** - 테스트 통과하는 코드 구현 (pytest → PASS)
5. ✅ **Verification** - 문서-코드 정합성 검증 (AST 파싱)
6. ✅ **Deployment** - Docker 설정, CI/CD 파이프라인 생성

## 📂 폴더 구조

```
docs/                                   # 모든 설계 문서
├── requirements/modules/{module}/      # 요구사항
│   ├── FR-{MOD}-{SEQ}-{name}.md       # Functional Requirements
│   └── AC-{MOD}-{SEQ}-test-plan.md    # Acceptance Criteria
├── design/                             # 설계
│   ├── api/API-{MOD}-{SEQ}.md         # API 사양 (RESTful)
│   ├── database/DB-{MOD}-{SEQ}.md     # DB 스키마
│   ├── component/COMP-{MOD}-{SEQ}.md  # 컴포넌트 설계
│   └── architecture/ARCH-APP-{SEQ}.md # 아키텍처 패턴
├── verification/{module}/              # 검증 결과
│   ├── traceability-matrix.md         # FR → Code → Test 매핑
│   └── verification-report-{date}.md  # 검증 보고서
├── progress/{module}/                  # 진행 현황
│   └── progress-{date}.md             # 진행률 대시보드
└── _utils/                             # 유틸리티
    ├── id_generator.py
    └── manifest_manager.py

app/                                    # 실제 코드 (Agent가 직접 생성)
├── domain/entities/                    # 엔티티
├── application/services/               # 비즈니스 로직
├── infrastructure/repositories/        # DB 접근
└── presentation/api/                   # API 컨트롤러

tests/                                  # 실제 테스트 (Agent가 직접 생성)
├── unit/                               # 단위 테스트 (70%)
├── integration/                        # 통합 테스트 (20%)
└── e2e/                                # E2E 테스트 (10%)

deployment/                             # 배포 설정 (Agent가 직접 생성)
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── scripts/
```

## 🎼 TDD 워크플로우 (완전 자동화)

### Phase 1: Requirements (requirements-agent)

```
입력: "재고 조회 기능"

출력:
→ docs/requirements/modules/inventory/FR-INV-001-stock-inquiry.md
→ docs/requirements/modules/inventory/AC-INV-001-test-plan.md

내용:
- User Story (As a... I want... So that...)
- Acceptance Criteria (Given-When-Then 형식)
- Business Rules
- Dependencies
```

### Phase 2: Design (design-agent)

```
입력: FR 문서들

출력:
→ docs/design/api/API-INV-001.md (RESTful API 사양)
→ docs/design/database/DB-INV-001.md (정규화된 스키마)
→ docs/design/architecture/ARCH-APP-001.md (Clean Architecture)

결정사항:
- Architecture Pattern: Clean Architecture (복잡한 비즈니스 로직)
- API Style: RESTful (GET /api/v1/inventory/{sku})
- Database: PostgreSQL (3NF 정규화, 인덱스 최적화)
```

### Phase 3: TDD Red Phase (testing-agent)

```
입력: FR + Design 문서들

실행:
1. AC 읽기 (Given-When-Then)
2. pytest 코드 직접 생성
   → tests/unit/test_inventory_service.py (23 tests)
   → tests/integration/test_inventory_api.py (8 tests)
3. pytest 실행

결과:
→ 31 tests FAILED ✅ (예상된 실패 - 구현 전)

예시 테스트:
def test_get_stock_level_valid_sku_returns_quantity(self, service, mock_repo):
    """
    Given: Repository has SKU-001 with quantity=100
    When: get_stock_level('SKU-001') called
    Then: Returns 100

    Related: FR-INV-001, AC-INV-001-01
    """
    # Arrange
    mock_inventory = Inventory(sku="SKU-001", quantity=100)
    mock_repo.find_by_sku.return_value = mock_inventory

    # Act
    result = service.get_stock_level("SKU-001")

    # Assert
    assert result == 100
```

### Phase 4: TDD Green Phase (implementation-agent)

```
입력: FR + Design + Failing Tests

실행:
1. 설계 문서 읽기
2. 실제 Python 코드 직접 생성
   → app/domain/entities/inventory.py
   → app/application/services/inventory_service.py
   → app/infrastructure/repositories/inventory_repository.py
   → app/presentation/api/v1/inventory.py
3. pytest 실행

결과:
→ 31 tests PASSED ✅ (구현 완료)

예시 코드:
class InventoryService:
    """
    Inventory management business logic.

    Generated by: implementation-agent
    Source: docs/design/api/API-INV-001.md
    Requirements: FR-INV-001, FR-INV-002
    Generated: 2025-11-12T10:00:00Z
    """

    def __init__(self, repo: IInventoryRepository):
        self.repo = repo

    def get_stock_level(self, sku: str) -> int:
        """
        Retrieve current stock quantity.

        Args:
            sku: Product SKU code

        Returns:
            Current stock quantity

        Raises:
            ValueError: If SKU not found

        Related: FR-INV-001
        """
        inventory = self.repo.find_by_sku(sku)
        if not inventory:
            raise ValueError(f"SKU not found: {sku}")
        return inventory.quantity
```

### Phase 5: Verification (verification-agent)

```
입력: FR 문서 + 코드 파일들 + 테스트 파일들

실행:
1. 문서 파싱 (Regex)
   - FR ID, AC, Business Rules 추출
2. 코드 분석 (AST)
   - 클래스, 함수, FR 참조 추출
3. 테스트 분석 (AST)
   - AC 참조 추출
4. 추적성 매트릭스 생성 (FR → Code → Test)
5. 갭 분석
   - Missing Implementation: FR 있는데 코드 없음
   - Missing Tests: 코드 있는데 테스트 없음
   - Orphaned Code: 코드 있는데 FR 없음

출력:
→ docs/verification/inventory/traceability-matrix.md
→ docs/verification/inventory/verification-report-20251112.md
→ docs/progress/inventory/progress-2025-11-12.md

결과:
- Traceability: 100% (FR → Code → Test 모두 연결)
- Test Coverage: 87%
- Gaps: 0
- Status: ✅ Complete
```

### Phase 6: Deployment (deployment-agent)

```
입력: Architecture 설계

실행:
1. Dockerfile 생성 (multi-stage build)
2. docker-compose.yml 생성 (app + DB + Redis)
3. nginx.conf 생성 (reverse proxy, SSL)
4. CI/CD pipeline 생성 (.github/workflows/)
5. 배포 스크립트 생성 (deploy.sh)

출력:
→ deployment/Dockerfile
→ deployment/docker-compose.yml
→ deployment/nginx.conf
→ deployment/.env.example
→ deployment/scripts/deploy.sh

사용법:
docker-compose up --build
./deployment/scripts/deploy.sh production
```

## 🔍 추적성 (Traceability)

### FR → Code → Test 매핑

```
FR-INV-001 (Stock Inquiry)
    ↓
app/services/inventory_service.py::get_stock_level
    ↓
tests/unit/test_inventory_service.py::test_get_stock_level_valid_sku
tests/unit/test_inventory_service.py::test_get_stock_level_invalid_sku
tests/integration/test_inventory_api.py::test_get_stock_endpoint
```

### 문서 ID 체계

```
{TYPE}-{MODULE}-{SEQ}

예:
- FR-INV-001: Functional Requirement (재고 모듈 요구사항 #1)
- AC-INV-001: Acceptance Criteria (재고 모듈 AC #1)
- API-INV-001: API Specification (재고 모듈 API #1)
- DB-INV-001: Database Schema (재고 모듈 DB #1)
- COMP-INV-001: Component Design (재고 모듈 컴포넌트 #1)
```

### AST 기반 자동 검증

```python
# verification-agent가 자동으로 수행

# 1. 문서에서 FR 추출
FR-INV-001: "Stock Level Inquiry"
  - AC-INV-001-01: Valid SKU returns quantity
  - AC-INV-001-02: Invalid SKU raises error

# 2. 코드에서 FR 참조 추출 (AST)
app/services/inventory_service.py:
  - Class: InventoryService
  - Method: get_stock_level
  - Docstring references: FR-INV-001

# 3. 테스트에서 AC 참조 추출 (AST)
tests/unit/test_inventory_service.py:
  - test_get_stock_level_valid_sku → AC-INV-001-01
  - test_get_stock_level_invalid_sku → AC-INV-001-02

# 4. 매핑 검증
✅ FR-INV-001 → InventoryService.get_stock_level → 2 tests
```

## 💡 핵심 개념

### 1. Agent = Senior Developer

| 역할 | OLD (YAML 방식) | NEW (직접 코딩) |
|------|-----------------|-----------------|
| 출력 | YAML 사양 → code-writer → 코드 | 실제 코드 직접 생성 |
| 토큰 | ~300 (YAML) + ~800 (code) = 1100 | ~680 (코드만) |
| 절감 | - | **38% 절감** |

### 2. 베스트 프랙티스 내장

각 Agent는:
- ✅ **SOLID 원칙** 적용
- ✅ **Clean Architecture** 패턴 사용
- ✅ **Design Patterns** (Repository, Service Layer, Factory)
- ✅ **Type Hints** + **Docstrings** 필수
- ✅ **Error Handling** 명시적

### 3. 완전 자동화

```
User: "재고 조회 기능 만들어줘"
    ↓
/full 실행
    ↓
6 Phases 자동 진행
    ↓
결과: Production-ready 코드 + 테스트 + 문서 + 배포 설정
```

## 🛠️ 주요 Agent

### 6개 통합 Agent

| Agent | 역할 | 입력 | 출력 |
|-------|------|------|------|
| **requirements-agent** | 요구사항 분석 | 사용자 요청 | FR, AC 문서 (markdown) |
| **design-agent** | 시스템 설계 | FR 문서 | API, DB, Architecture 문서 |
| **testing-agent** | 테스트 작성 | FR + Design | 실제 pytest 코드 |
| **implementation-agent** | 코드 구현 | FR + Design + Tests | 실제 Python 코드 |
| **verification-agent** | 정합성 검증 | 문서 + 코드 + 테스트 | Traceability 보고서 |
| **deployment-agent** | 배포 설정 | Architecture | Docker, CI/CD 설정 |

### OLD: 29개 Agent (비효율적)

```
❌ unit-test-generator → YAML
❌ backend-service-generator → YAML
❌ code-writer → YAML을 읽어 코드 생성
... 총 29개
```

### NEW: 6개 Agent (79% 감소)

```
✅ testing-agent → 실제 pytest 코드 직접 생성
✅ implementation-agent → 실제 Python 코드 직접 생성
... 총 6개
```

## 📊 성공 기준

### TDD 사이클 완료 시:

- ✅ **RED Phase**: 모든 테스트 FAIL (구현 전)
- ✅ **GREEN Phase**: 모든 테스트 PASS (구현 후)
- ✅ **Verification**: FR → Code → Test 100% 추적 가능
- ✅ **Coverage**: 80%+
- ✅ **Quality**: Type hints + Docstrings + Error handling 완비

### Verification Report 예시:

```markdown
# Verification Report: Inventory

**Status**: ✅ Complete

## Summary
- Total Requirements: 5
- Fully Implemented: 5 (100%)
- Test Coverage: 87%
- Gaps: 0

## Traceability Matrix

| FR ID | Code | Tests | Status |
|-------|------|-------|--------|
| FR-INV-001 | InventoryService.get_stock_level | 3 tests | ✅ Complete |
| FR-INV-002 | InventoryService.add_stock | 2 tests | ✅ Complete |
| FR-INV-003 | InventoryService.remove_stock | 3 tests | ✅ Complete |
```

## 🎯 실전 예제

### 재고 관리 모듈 구현

```bash
# 완전 자동화 실행
/full

# 사용자 입력
"재고 조회, 입고, 출고, 재고 부족 알림 기능을 구현해줘"

# 결과 (자동 생성):
✅ docs/requirements/modules/inventory/
   - FR-INV-001-stock-inquiry.md
   - FR-INV-002-stock-receipt.md
   - FR-INV-003-stock-issue.md
   - FR-INV-004-low-stock-alert.md
   - AC-INV-001-test-plan.md

✅ docs/design/
   - api/API-INV-001.md (8 endpoints)
   - database/DB-INV-001.md (3 tables)
   - architecture/ARCH-APP-001.md (Clean Architecture)

✅ tests/ (pytest → 31 FAIL → 31 PASS)
   - unit/test_inventory_service.py (23 tests)
   - integration/test_inventory_api.py (8 tests)

✅ app/ (Clean Architecture)
   - domain/entities/inventory.py
   - application/services/inventory_service.py
   - infrastructure/repositories/inventory_repository.py
   - presentation/api/v1/inventory.py

✅ docs/verification/inventory/
   - traceability-matrix.md (100% coverage)
   - verification-report.md (0 gaps)

✅ deployment/
   - Dockerfile
   - docker-compose.yml
   - nginx.conf

최종 결과:
- Coverage: 87%
- Traceability: 100%
- Ready for Production: ✅
```

## 🔧 Agent 작동 원리

### Example: implementation-agent

```markdown
# Agent Prompt (implementation-agent.md)

## Role
Write production-ready code directly (not YAML)

## Input
Read from:
- docs/requirements/ (FR documents)
- docs/design/ (API, DB, Architecture)

## Output
Generate actual Python code:
- app/services/inventory_service.py
- app/models/inventory.py
- app/api/v1/inventory.py

## Guidelines
- SOLID principles
- Type hints required
- Docstrings with FR references
- Error handling explicit
- Clean Architecture pattern
```

### Example: verification-agent

```python
# Agent가 실행하는 로직

# 1. 문서 파싱 (Regex)
fr_data = parse_functional_requirement('FR-INV-001.md')
# → {'id': 'FR-INV-001', 'acceptance_criteria': [...]}

# 2. 코드 분석 (AST)
import ast
tree = ast.parse(code_file)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        docstring = ast.get_docstring(node)
        fr_refs = re.findall(r'FR-[A-Z]+-\d+', docstring)
        # → ['FR-INV-001']

# 3. 매핑 생성
traceability_matrix = {
    'FR-INV-001': {
        'implemented_in': ['InventoryService.get_stock_level'],
        'tested_by': ['test_get_stock_level_valid_sku'],
        'status': 'Complete'
    }
}

# 4. 보고서 생성
generate_report(traceability_matrix)
```

## 📖 다음 단계

1. **첫 기능 개발**: `/full` 실행 후 기능 설명
2. **추가 모듈**: 주문, 생산, 품질 등 다른 모듈 개발
3. **배포**: `docker-compose up` 또는 `./deploy.sh production`

## 🎓 학습 자료

- [Agent 상세 가이드](.claude/agents/)
  - [requirements-agent.md](.claude/agents/requirements-agent.md)
  - [design-agent.md](.claude/agents/design-agent.md)
  - [implementation-agent.md](.claude/agents/implementation-agent.md)
  - [testing-agent.md](.claude/agents/testing-agent.md)
  - [verification-agent.md](.claude/agents/verification-agent.md)
  - [deployment-agent.md](.claude/agents/deployment-agent.md)
- [Command 가이드](.claude/commands/)
  - [full.md](.claude/commands/full.md) - 완전 자동화 파이프라인
- [기존 MES 프로젝트 문서](./README.md)

## 🚨 주의사항

### TDD Red Phase에서 테스트가 통과하면 안 됨

```bash
# Phase 3 (testing-agent 실행 후)
pytest tests/
→ 31 tests FAILED ✅ (정상)

# 만약 PASSED가 나오면:
→ ❌ ERROR: 구현이 이미 존재하거나 테스트가 잘못됨
```

### Verification에서 갭 발견 시

```markdown
## Gaps Analysis

- Missing Implementation: FR-INV-005 (미구현)
- Missing Tests: FR-INV-003 (테스트 없음)

→ ⚠️ implementation-agent, testing-agent 재실행 필요
```

---

**시작하기**: `/full`을 실행하고 구현할 기능을 설명하세요!

**예시**:
```
/full

"작업자가 SKU 코드로 현재 재고 수량을 조회하고,
입고/출고를 기록하며, 재고가 최소 수량 이하로 떨어지면
알림을 받을 수 있는 재고 관리 시스템을 만들어줘"
```

→ 자동으로 요구사항 분석부터 배포까지 완료됩니다!
