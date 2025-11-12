---
description: Execute TDD workflow - analyze prompt, run appropriate agents, generate code and tests
argument-hint: <task description>
---

You are executing the **TDD (Test-Driven Development) Workflow Command**.

## Task Description

User's request: $ARGUMENTS

## TDD Workflow Steps

### Step 1: Analyze the Request

Determine which phase and agents are needed based on the user's request:

**If the request is about:**
- Requirements/specifications → Phase 1 agents (requirements-analyzer, api-designer, etc.)
- Design/architecture → Phase 2 agents (component-architect, data-modeler, etc.)
- Implementation/coding → Phase 3 agents (backend/frontend generators)
- Testing → Phase 4 agents (test generators)
- Deployment → Phase 5 agents (build, deploy)

### Step 2: Execute Relevant Agents

Invoke the appropriate agents from `.claude/agents/` folder:

For example:
- If user asks to "implement user authentication API"
  1. Run: api-designer (if API spec not exists)
  2. Run: component-architect (design components)
  3. Run: backend-router-generator (generate code)
  4. Run: unit-test-generator (generate tests)

Use the agents by saying:
"I'm going to use the [agent-name] agent to [what it will do]."

Then execute the agent's instructions.

### Step 3: Generate Code (Implementation)

Based on agent outputs, generate actual code files:
- Backend: Python/FastAPI code
- Frontend: React/TypeScript code
- Tests: pytest/Jest test files

### Step 4: Generate Tests FIRST (TDD Principle)

**Write tests before implementation** (Red-Green-Refactor):

1. **Red**: Write failing tests based on acceptance criteria
2. **Green**: Write minimal code to make tests pass
3. **Refactor**: Improve code while keeping tests green

### Step 5: Run Tests

Execute the tests:
```bash
# Backend tests
pytest tests/unit/test_[module].py -v

# Frontend tests
npm run test
```

### Step 6: Generate TDD Report

Create a comprehensive TDD report in this format:

```markdown
# TDD Workflow Report

## 📋 Task Summary
**Request**: [User's original request]
**Agents Used**: [List of agents executed]
**Duration**: [Estimated time]

---

## 🎯 Phase 1: Requirement Analysis

**Agent**: requirements-analyzer

**Findings**:
- [Key requirements extracted]
- [Business rules identified]
- [User stories]

**Output**: `artifacts/phase1_documentation/functional_requirements.md`

---

## 🏗️ Phase 2: Design

**Agents**: component-architect, data-modeler

**Design Decisions**:
- [Component structure]
- [Data models]
- [Interfaces]

**Outputs**:
- `artifacts/phase2_design/component_architecture.md`
- `artifacts/phase2_design/data_model_design.md`

---

## 🔴 RED: Write Failing Tests

**Agent**: unit-test-generator

**Tests Created**:

\`\`\`python
# tests/unit/test_[module].py

import pytest
from app.services.[module]_service import [Module]Service

class Test[Module]Service:
    def test_create_[entity]_success(self):
        """Test successful [entity] creation"""
        # Arrange
        service = [Module]Service()
        data = {"field1": "value1"}

        # Act
        result = service.create(data)

        # Assert
        assert result.id is not None
        assert result.field1 == "value1"

    def test_create_[entity]_invalid_data(self):
        """Test [entity] creation with invalid data"""
        service = [Module]Service()
        data = {"field1": ""}  # Invalid

        with pytest.raises(ValidationError):
            service.create(data)
\`\`\`

**Test Execution** (Expected: ❌ FAIL):
\`\`\`
$ pytest tests/unit/test_[module].py -v

test_create_[entity]_success FAILED
test_create_[entity]_invalid_data FAILED

FAILED: 2 failed in 0.5s
\`\`\`

---

## 🟢 GREEN: Implement Code to Pass Tests

**Agent**: backend-service-generator

**Implementation**:

\`\`\`python
# app/services/[module]_service.py

from pydantic import ValidationError

class [Module]Service:
    def __init__(self, repo: I[Module]Repository):
        self.repo = repo

    def create(self, data: dict) -> [Module]:
        """Create new [entity]"""
        # Validate
        if not data.get("field1"):
            raise ValidationError("field1 is required")

        # Business logic
        entity = [Module](**data)

        # Save
        return self.repo.save(entity)
\`\`\`

**Test Execution** (Expected: ✅ PASS):
\`\`\`
$ pytest tests/unit/test_[module].py -v

test_create_[entity]_success PASSED
test_create_[entity]_invalid_data PASSED

PASSED: 2 passed in 0.3s
\`\`\`

---

## ♻️ REFACTOR: Improve Code Quality

**Improvements**:
- ✅ Extract validation to separate method
- ✅ Add docstrings
- ✅ Improve error messages
- ✅ Add type hints

**Refactored Code**:

\`\`\`python
# app/services/[module]_service.py

from typing import Optional
from pydantic import ValidationError

class [Module]Service:
    """Service for [entity] business logic"""

    def __init__(self, repo: I[Module]Repository):
        self.repo = repo

    def create(self, data: dict) -> [Module]:
        """
        Create new [entity]

        Args:
            data: [Entity] data

        Returns:
            Created [entity]

        Raises:
            ValidationError: If data is invalid
        """
        self._validate_create_data(data)
        entity = [Module](**data)
        return self.repo.save(entity)

    def _validate_create_data(self, data: dict) -> None:
        """Validate [entity] creation data"""
        if not data.get("field1"):
            raise ValidationError("field1 is required and cannot be empty")
\`\`\`

**Test Execution** (Should still: ✅ PASS):
\`\`\`
$ pytest tests/unit/test_[module].py -v

test_create_[entity]_success PASSED
test_create_[entity]_invalid_data PASSED

PASSED: 2 passed in 0.3s
\`\`\`

---

## 📊 Test Coverage Report

\`\`\`
$ pytest --cov=app/services tests/unit/

---------- coverage: platform win32, python 3.11 -----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app/services/[module]_service.py      15      0   100%
-------------------------------------------------------
TOTAL                                 15      0   100%
\`\`\`

✅ **Coverage: 100%**

---

## 🧪 Integration Tests

**Agent**: integration-test-generator

**API Tests**:

\`\`\`python
# tests/integration/test_[module]_api.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_[entity]_api(client: AsyncClient):
    """Test POST /api/[entities] endpoint"""
    response = await client.post(
        "/api/[entities]",
        json={"field1": "value1"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["field1"] == "value1"
\`\`\`

**Execution**:
\`\`\`
$ pytest tests/integration/ -v

test_create_[entity]_api PASSED

PASSED: 1 passed in 1.2s
\`\`\`

---

## ✅ Acceptance Criteria Validation

**From**: `artifacts/phase1_documentation/acceptance_criteria.md`

**AC-[MODULE]-001: [Requirement Title]**

Given: User is authenticated
When: User creates [entity] with valid data
Then: [Entity] is created and returned

**Status**: ✅ PASSED

| Test Scenario | Status | Notes |
|---------------|--------|-------|
| TS-[MODULE]-001-01: Happy path | ✅ PASS | |
| TS-[MODULE]-001-02: Invalid input | ✅ PASS | |
| TS-[MODULE]-001-03: Unauthorized | ✅ PASS | |

---

## 📁 Files Created

**Source Code**:
- `app/services/[module]_service.py`
- `app/repositories/[module]_repository.py`
- `app/api/v1/[module].py`

**Tests**:
- `tests/unit/test_[module]_service.py`
- `tests/unit/test_[module]_repository.py`
- `tests/integration/test_[module]_api.py`

**Documentation**:
- `artifacts/phase1_documentation/functional_requirements.md` (updated)
- `artifacts/phase2_design/component_architecture.md` (updated)

---

## 🎯 Summary

**TDD Cycle Completed**: ✅

**Red → Green → Refactor**: ✅

**Test Coverage**: 100%

**All Acceptance Criteria**: PASSED

**Next Steps**:
1. Code review
2. Integration with existing codebase
3. Deployment to staging
```

---

## Execution Notes

1. **Identify agents needed**: Based on user's request, determine which agents to invoke
2. **Run agents in correct order**: Follow phase dependencies (Phase 1 → 2 → 3 → 4)
3. **Generate tests FIRST**: Follow TDD principle (Red-Green-Refactor)
4. **Execute tests**: Run tests and show pass/fail results
5. **Report in TDD format**: Use the template above

## Agent Selection Logic

**Request Analysis**:
- Keywords: "API", "endpoint" → api-designer, backend-router-generator
- Keywords: "database", "model" → database-designer, data-modeler
- Keywords: "test" → test generator agents
- Keywords: "deploy" → deployment agents

**Always include**:
- requirements-analyzer (if requirements not clear)
- unit-test-generator (for TDD)
- acceptance-validator (to verify)

## Success Criteria

Your TDD report must include:
- ✅ Clear task summary
- ✅ Agents used and their outputs
- ✅ RED phase: Failing tests shown
- ✅ GREEN phase: Passing tests shown
- ✅ REFACTOR phase: Improved code
- ✅ Test coverage report
- ✅ Acceptance criteria validation
- ✅ Files created list
