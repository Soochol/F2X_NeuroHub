---
name: full
description: Complete TDD automation pipeline - from requirements to verification (development phase only)
---

You are orchestrating a **complete software development pipeline** using specialized Claude agents.

## Mission

Execute full TDD workflow automatically:
1. **Requirements** → Analyze user request, create FR documents
2. **Design** → Create API specs, DB schemas, architecture
3. **TDD Red Phase** → Generate failing tests first
4. **TDD Green Phase** → Implement code to pass tests
5. **Verification** → Validate document-code alignment

**Note**: Deployment configuration is handled separately via `/deploy` command.

## User Request Format

User provides a feature description, for example:
- "재고 조회 기능 만들어줘" (Create inventory inquiry feature)
- "주문 생성 API를 구현해줘" (Implement order creation API)
- "품질 검사 결과 저장 기능" (Quality inspection result storage)

## Pipeline Execution

### Phase 1: Requirements Analysis

**Agent**: requirements-agent
**Input**: User's feature description
**Output**: FR documents + AC test plans

**Steps**:
1. Analyze user request to extract entities, operations, business rules
2. Create functional requirements (FR) documents
3. Generate acceptance criteria (AC) in Given-When-Then format
4. Create acceptance test plans
5. Update manifest.json

**Expected Output**:
```
docs/requirements/modules/{module}/
├── FR-{MOD}-001-{feature}.md
└── AC-{MOD}-001-test-plan.md
```

**Status Check**:
- ✅ FR documents created with unique IDs
- ✅ Acceptance criteria defined (testable)
- ✅ Manifest updated

---

### Phase 2: System Design

**Agent**: design-agent
**Input**: FR documents from Phase 1
**Output**: API specs + DB schemas + Architecture design

**Steps**:
1. Read all FR documents from docs/requirements/
2. Select appropriate architecture pattern (Clean Architecture, Layered, DDD)
3. Design RESTful API endpoints
4. Design database schema (normalized, indexed)
5. Create component architecture
6. Update manifest.json

**Expected Output**:
```
docs/design/
├── api/API-{MOD}-001-{feature}.md
├── database/DB-{MOD}-001-{table}.md
├── component/COMP-{MOD}-001-service.md
└── architecture/ARCH-APP-001.md
```

**Status Check**:
- ✅ API endpoints defined (RESTful)
- ✅ Database schema created (3NF)
- ✅ Architecture pattern selected
- ✅ Manifest updated

---

### Phase 3: TDD Red Phase (Write Failing Tests First)

**Agent**: testing-agent
**Input**: FR + AC + Design specs
**Output**: Actual pytest test files (failing)

**Steps**:
1. Read acceptance criteria (AC) from docs/requirements/
2. Read API specifications from docs/design/api/
3. Generate unit tests (70% coverage target)
4. Generate integration tests (20% coverage)
5. Generate E2E tests (10% coverage)
6. **Run pytest** → All tests should FAIL (RED phase)
7. Update manifest.json

**Expected Output**:
```
tests/
├── unit/test_{module}_service.py
├── integration/test_{module}_api.py
└── e2e/test_{module}_workflow.py
```

**Status Check**:
- ✅ Test files created with FR/AC references in docstrings
- ✅ pytest executed → **All tests FAIL** (RED ✅)
- ❌ If tests PASS unexpectedly → Error (no implementation should exist yet)

**Critical**: Tests MUST fail at this stage. If they pass, stop and alert.

---

### Phase 4: TDD Green Phase (Implement Code to Pass Tests)

**Agent**: implementation-agent
**Input**: FR + Design specs + Failing tests
**Output**: Actual Python code files

**Steps**:
1. Read functional requirements (FR)
2. Read design specifications (API, DB, Component)
3. Read failing tests from Phase 3
4. Generate implementation code:
   - Domain entities (app/domain/entities/)
   - Services (app/application/services/)
   - Repositories (app/infrastructure/repositories/)
   - API controllers (app/presentation/api/)
5. **Run pytest** → All tests should PASS (GREEN phase)
6. Update manifest.json

**Expected Output**:
```
app/
├── domain/entities/{module}.py
├── application/services/{module}_service.py
├── infrastructure/repositories/{module}_repository.py
└── presentation/api/v1/{module}.py
```

**Status Check**:
- ✅ Code files created with FR references in docstrings
- ✅ pytest executed → **All tests PASS** (GREEN ✅)
- ✅ Type hints present
- ✅ Error handling implemented
- ❌ If tests still FAIL → Debug and fix

**Critical**: Tests MUST pass at this stage. If they fail, analyze errors and fix implementation.

---

### Phase 5: Verification & Documentation Alignment

**Agent**: verification-agent
**Input**: FR docs + Code files + Test files
**Output**: Traceability matrix + Verification report + Progress dashboard

**Steps**:
1. Parse all FR documents (extract IDs, ACs, business rules)
2. Analyze code with AST (extract classes, functions, FR references)
3. Analyze tests with AST (extract test functions, AC references)
4. Generate traceability matrix (FR → Code → Test mapping)
5. Identify gaps:
   - Missing implementations (FR with no code)
   - Missing tests (FR with code but no tests)
   - Orphaned code (code with no FR reference)
6. Generate verification report
7. Create progress dashboard
8. Update manifest.json

**Expected Output**:
```
docs/verification/{module}/
├── traceability-matrix.md
└── verification-report-{timestamp}.md

docs/progress/{module}/
└── progress-{date}.md
```

**Status Check**:
- ✅ Traceability matrix complete (FR → Code → Test)
- ✅ No gaps identified (100% coverage)
- ✅ All business rules verified in code
- ⚠️ If gaps exist → Report to user

**Acceptance Criteria**:
- All FRs have corresponding code
- All ACs have corresponding tests
- All code references FRs in docstrings
- Test coverage ≥ 80%

---

## Final Report

After all phases complete, generate summary:

```markdown
# Development Complete: {Feature Name}

**Feature**: {User's original request}
**Module**: {module_name}
**Completion Time**: {timestamp}

## Pipeline Results

| Phase | Status | Output |
|-------|--------|--------|
| Requirements | ✅ Complete | 5 FR documents, 15 acceptance criteria |
| Design | ✅ Complete | 8 API endpoints, 3 tables, Clean Architecture |
| TDD Red | ✅ Complete | 23 failing tests |
| TDD Green | ✅ Complete | All 23 tests passing |
| Verification | ✅ Complete | 100% traceability, 0 gaps |

## Code Metrics

- **Total Files Created**: 18
- **Lines of Code**: 1,247
- **Test Coverage**: 87%
- **Requirements Coverage**: 100% (5/5 FRs implemented)

## Verification Summary

**Traceability**: 100%
- FR-INV-001 → InventoryService.get_stock_level → 3 tests ✅
- FR-INV-002 → InventoryService.add_stock → 2 tests ✅
- FR-INV-003 → InventoryService.remove_stock → 3 tests ✅
- FR-INV-004 → InventoryService.check_low_stock → 2 tests ✅
- FR-INV-005 → InventoryController.get_inventory → 5 tests ✅

**Gaps**: None

## Next Steps

### To Run Tests:
\`\`\`bash
# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=app tests/
\`\`\`

### To Deploy:
Run `/deploy` command to generate deployment configurations (Docker, CI/CD, scripts).

## Documentation

All documentation available in:
- Requirements: docs/requirements/modules/{module}/
- Design: docs/design/
- Verification: docs/verification/{module}/
- Progress: docs/progress/{module}/

---

✅ Development complete! Ready for deployment setup via `/deploy` command.
```

## Error Handling

### If Phase Fails:

**Requirements Phase Fails**:
- Error: User request too vague
- Action: Ask clarifying questions, retry

**Design Phase Fails**:
- Error: Conflicting requirements
- Action: Flag conflicts, ask user to prioritize

**TDD Red Phase Issues**:
- Error: Tests PASS when they should FAIL
- Action: **STOP** - Implementation already exists or tests are wrong

**TDD Green Phase Issues**:
- Error: Tests still FAIL after implementation
- Action: Analyze pytest output, debug, fix code, re-run

**Verification Phase Issues**:
- Error: Gaps detected (missing implementation/tests)
- Action: Report gaps, ask user if acceptable or re-run implementation

## Workflow Diagram

```
User Request
    ↓
[Phase 1: Requirements] → FR docs + AC
    ↓
[Phase 2: Design] → API + DB + Architecture
    ↓
[Phase 3: TDD Red] → Write failing tests
    ↓ (pytest → ALL FAIL ✅)
[Phase 4: TDD Green] → Implement code
    ↓ (pytest → ALL PASS ✅)
[Phase 5: Verification] → Check FR-Code-Test alignment
    ↓ (100% traceability ✅)
Final Report → Development Complete

(Run /deploy separately for deployment setup)
```

## Agent Invocation Example

```python
# Phase 1: Requirements
requirements_result = invoke_agent(
    agent='requirements-agent',
    input={
        'user_request': '재고 조회 기능 만들어줘',
        'module': 'inventory'
    }
)

# Phase 2: Design
design_result = invoke_agent(
    agent='design-agent',
    input={
        'requirements_path': 'docs/requirements/modules/inventory/'
    }
)

# Phase 3: TDD Red
testing_result = invoke_agent(
    agent='testing-agent',
    input={
        'requirements_path': 'docs/requirements/modules/inventory/',
        'design_path': 'docs/design/'
    }
)

# Verify tests FAIL
assert pytest_status == 'FAILED', "Tests must fail in RED phase!"

# Phase 4: TDD Green
implementation_result = invoke_agent(
    agent='implementation-agent',
    input={
        'requirements_path': 'docs/requirements/modules/inventory/',
        'design_path': 'docs/design/',
        'tests_path': 'tests/'
    }
)

# Verify tests PASS
assert pytest_status == 'PASSED', "Tests must pass in GREEN phase!"

# Phase 5: Verification
verification_result = invoke_agent(
    agent='verification-agent',
    input={
        'module': 'inventory'
    }
)

# Check for gaps
assert verification_result['gaps'] == 0, "All requirements must be traced!"

# Development complete!
# Run /deploy separately if deployment configuration is needed
```

## Success Criteria

Pipeline succeeds if:
- ✅ All 5 phases complete without errors
- ✅ TDD Red phase: tests FAIL
- ✅ TDD Green phase: tests PASS
- ✅ Verification phase: 0 gaps
- ✅ Final test coverage ≥ 80%
- ✅ All FR references present in code

---

**Philosophy**: Automate the development lifecycle (requirements → code → tests → verification) while maintaining quality through TDD!
