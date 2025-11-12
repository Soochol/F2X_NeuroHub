---
description: Implement code using TDD (Test-Driven Development) methodology
argument-hint: [--module <module_name>] [--id <doc_id>]
---

You are executing the **/implement:tdd Command** - TDD Implementation Pipeline

## User's Request

$ARGUMENTS

## Command Overview

This command implements code using strict TDD methodology:
1. **RED**: Generate failing tests FIRST
2. **GREEN**: Implement minimal code to pass tests
3. **REFACTOR**: Improve code quality while keeping tests green

## Prerequisites Check

Before starting, verify:

```bash
# Check if design documents exist
ls docs/design/*.md
ls docs/requirements/*.md
```

If no design documents found, suggest:
```
⚠️ No design documents found!

Please run these commands first:
1. /spec <requirements>  - Generate requirements
2. /design               - Generate design specs

Or provide design documents manually in docs/design/
```

## Workflow

### Phase 1: RED - Generate Failing Tests

#### Step 1.1: Run unit-test-generator Agent

Execute the `unit-test-generator` agent to create test specifications.

**Input**: `docs/requirements/`, `docs/design/`
**Output**: `docs/testing/unit/{DOC_ID}-*-test.md` (YAML specs)

The agent will:
- Read acceptance criteria
- Read design specifications
- Generate structured YAML test specs
- Return metadata (doc_id, uuid, file path)

#### Step 1.2: Collect Agent Results

Parse agent output to extract:
```json
{
  "documents": [
    {
      "doc_id": "TEST-INV-001",
      "uuid": "c3d4e5f6...",
      "file": "docs/testing/unit/TEST-INV-001-inventory-service-test.md",
      "title": "Inventory Service Tests",
      "module": "inventory",
      "test_count": 12
    }
  ]
}
```

#### Step 1.3: Run code-writer Agent (Test Mode)

Execute `code-writer` agent to generate actual pytest code from test specs.

**Input**: Test specification documents from Step 1.2
**Output**: `tests/unit/test_*.py`

Example:
```bash
# code-writer will read:
docs/testing/unit/TEST-INV-001-inventory-service-test.md

# And generate:
tests/unit/test_inventory_service.py
```

#### Step 1.4: Run Tests (Expect FAIL)

```bash
pytest tests/unit/ -v --tb=short
```

**Expected Result**: ❌ ALL TESTS FAIL

Report:
```
🔴 RED Phase Complete

Tests Generated: 12
Tests Run: 12
Tests FAILED: 12 ✅ (Expected)
Tests PASSED: 0

Example failures:
- test_get_stock_level_success: ModuleNotFoundError: No module named 'app.services.inventory_service'
- test_add_stock_success: ModuleNotFoundError...

✅ This is correct! Tests should fail before implementation.

Proceeding to GREEN phase...
```

### Phase 2: GREEN - Implement Code to Pass Tests

#### Step 2.1: Run Implementation Agents

Execute these agents in parallel:

1. **backend-model-generator**
   - Input: `docs/design/database/*.md`
   - Output: `docs/implementation/backend/models/{DOC_ID}-*.md`

2. **backend-service-generator**
   - Input: `docs/design/component_design.md`
   - Output: `docs/implementation/backend/services/{DOC_ID}-*.md`

3. **backend-router-generator**
   - Input: `docs/design/api/*.md`
   - Output: `docs/implementation/backend/routers/{DOC_ID}-*.md`

Each agent returns metadata similar to unit-test-generator.

#### Step 2.2: Collect Implementation Specs

Parse all agent outputs:
```json
{
  "documents": [
    {
      "doc_id": "MDL-INV-001",
      "uuid": "d4e5f6a7...",
      "file": "docs/implementation/backend/models/MDL-INV-001-inventory.md",
      "module": "inventory"
    },
    {
      "doc_id": "SVC-INV-001",
      "uuid": "a1b2c3d4...",
      "file": "docs/implementation/backend/services/SVC-INV-001-inventory-service.md",
      "module": "inventory"
    }
  ]
}
```

#### Step 2.3: Update Manifest

Use Python utility to update manifest:

```python
import sys
sys.path.append('docs/_utils')
from manifest_manager import ManifestManager

# Update implementation manifest
manager = ManifestManager("implementation")

for doc in collected_documents:
    manager.add_document(
        doc_id=doc["doc_id"],
        uuid=doc["uuid"],
        file_path=doc["file"],
        title=doc["title"],
        module=doc["module"],
        doc_type=doc["type"],
        dependencies=doc.get("dependencies", []),
        outputs=doc.get("outputs", []),
        version=1
    )

print("✅ Manifest updated: docs/implementation/_manifest.json")
```

#### Step 2.4: Run code-writer Agent (Implementation Mode)

Execute `code-writer` to generate actual code from implementation specs.

**Input**: All implementation spec documents from Step 2.2
**Output**: `app/models/*.py`, `app/services/*.py`, `app/api/*.py`

Example:
```bash
# code-writer will read:
docs/implementation/backend/models/MDL-INV-001-inventory.md
docs/implementation/backend/services/SVC-INV-001-inventory-service.md

# And generate:
app/models/inventory.py
app/services/inventory_service.py
```

#### Step 2.5: Run Tests Again (Expect PASS)

```bash
pytest tests/unit/ -v --cov=app --cov-report=term-missing
```

**Expected Result**: ✅ ALL TESTS PASS

Report:
```
🟢 GREEN Phase Complete

Tests Run: 12
Tests PASSED: 12 ✅
Tests FAILED: 0 ✅

Coverage:
- app/models/inventory.py: 100%
- app/services/inventory_service.py: 95%
- Overall: 97%

✅ All tests passing! Code is working.

Proceeding to REFACTOR phase...
```

If tests still fail, report errors and stop:
```
❌ GREEN Phase Failed

Tests PASSED: 8
Tests FAILED: 4

Failed Tests:
- test_remove_stock_insufficient: AssertionError: ValueError not raised
- test_add_stock_negative_quantity: Expected error not thrown
- ...

Please review implementation specs or generated code.
```

### Phase 3: REFACTOR - Improve Code Quality

#### Step 3.1: Code Review (Manual or Agent)

For now, provide manual checklist:
```
🔍 Refactoring Checklist

Please review:
- ✅ Type hints complete?
- ✅ Docstrings present?
- ✅ Variable names clear?
- ✅ No code duplication?
- ✅ Error messages helpful?
- ✅ Constants extracted?
- ✅ Functions < 20 lines?

Suggested improvements:
- Extract validation to separate method
- Add logging for debugging
- Improve error messages
```

#### Step 3.2: Apply Refactoring

Make improvements to generated code while ensuring tests still pass.

#### Step 3.3: Final Test Run

```bash
pytest tests/unit/ -v --cov=app --cov-report=term-missing
```

**Expected**: ✅ Tests STILL PASS after refactoring

Report:
```
♻️ REFACTOR Phase Complete

Tests Run: 12
Tests PASSED: 12 ✅
Coverage: 98% ✅

Refactoring applied:
- Extracted _validate_quantity() method
- Added docstrings to all methods
- Improved error messages

✅ Refactoring complete while maintaining test coverage!
```

## Final Report

After all phases complete, generate comprehensive report:

```markdown
# TDD Implementation Report

## Summary

**Module**: inventory
**Duration**: ~15 minutes
**Status**: ✅ SUCCESS

---

## 🔴 RED Phase

**Test Specifications Created**:
- TEST-INV-001: Inventory Service Tests
  - File: docs/testing/unit/TEST-INV-001-inventory-service-test.md
  - UUID: c3d4e5f6-a7b8-9012-cdef-3456789abcde
  - Test Cases: 12

**Test Code Generated**:
- tests/unit/test_inventory_service.py (180 lines)

**Test Execution**:
- Run: 12 tests
- Failed: 12 ✅ (Expected before implementation)

---

## 🟢 GREEN Phase

**Implementation Specs Created**:
- MDL-INV-001: Inventory Model
- SVC-INV-001: Inventory Service
- RTR-INV-001: Inventory Router

**Code Generated**:
- app/models/inventory.py (45 lines)
- app/services/inventory_service.py (78 lines)
- app/api/v1/inventory.py (62 lines)

**Total**: 3 files, 185 lines

**Test Execution**:
- Run: 12 tests
- Passed: 12 ✅
- Coverage: 97%

---

## ♻️ REFACTOR Phase

**Improvements Applied**:
- Extracted validation methods
- Added comprehensive docstrings
- Improved error messages
- Added type hints

**Final Test Results**:
- Run: 12 tests
- Passed: 12 ✅
- Coverage: 98%

---

## 📊 Traceability

| Test Case | Implementation | Requirement |
|-----------|----------------|-------------|
| test_get_stock_level_success | SVC-INV-001.get_stock_level | FR-INV-001 |
| test_add_stock_success | SVC-INV-001.add_stock | FR-INV-002 |
| test_remove_stock_success | SVC-INV-001.remove_stock | FR-INV-003 |

---

## 📁 Files Created

**Documentation**:
- docs/testing/unit/TEST-INV-001-inventory-service-test.md
- docs/implementation/backend/models/MDL-INV-001-inventory.md
- docs/implementation/backend/services/SVC-INV-001-inventory-service.md

**Code**:
- app/models/inventory.py
- app/services/inventory_service.py
- tests/unit/test_inventory_service.py

**Manifests Updated**:
- docs/testing/_manifest.json
- docs/implementation/_manifest.json

---

## ✅ Success Criteria Met

- ✅ TDD Cycle Completed (RED → GREEN → REFACTOR)
- ✅ All Tests Passing
- ✅ Code Coverage > 90%
- ✅ All Requirements Traced
- ✅ Documentation Generated
- ✅ Manifests Updated

---

## 🎯 Next Steps

1. **Code Review**: Review generated code for business logic correctness
2. **Integration Tests**: Run `/implement:integration` for API testing
3. **Manual Testing**: Test via API endpoints
4. **Deployment**: Run `/deploy` when ready

```

## Optional Arguments

### `--module <module_name>`

Implement only specific module:

```bash
/implement:tdd --module inventory
```

This will:
- Filter specs to inventory module only
- Generate code only for inventory
- Run only inventory tests

### `--id <doc_id>`

Regenerate code for specific document:

```bash
/implement:tdd --id SVC-INV-001
```

This will:
- Find SVC-INV-001 in manifest
- Regenerate code from that spec only
- Run related tests

## Error Handling

### No Design Documents

```
❌ Error: No design documents found

Please run:
1. /design

Or manually create design documents in docs/design/
```

### Tests Fail in GREEN Phase

```
❌ GREEN Phase Failed

This means implementation doesn't match test specs.

Possible causes:
1. Implementation spec incomplete
2. Code-writer generated incorrect code
3. Test spec has errors

Please review:
- docs/implementation/backend/services/SVC-INV-001-inventory-service.md
- app/services/inventory_service.py
- tests/unit/test_inventory_service.py

Fix the issue and re-run: /implement:tdd
```

### Tests Fail After Refactoring

```
❌ REFACTOR Phase Failed

Tests were passing but now failing after refactoring!

Please revert changes and try again.
```

## Implementation Notes

This command orchestrates multiple agents:
1. **unit-test-generator**: YAML test specs
2. **code-writer**: pytest code (RED phase)
3. **backend-*-generator**: YAML implementation specs
4. **code-writer**: actual code (GREEN phase)
5. **pytest**: Test execution
6. **manifest-manager**: Tracking

All agents are autonomous and communicate via:
- Input: docs/ folder
- Output: docs/ folder + code files
- Metadata: Returned to command for manifest updates

## Success Criteria

Command succeeds when:
- ✅ All 3 phases complete (RED → GREEN → REFACTOR)
- ✅ All tests passing
- ✅ Code coverage > 90%
- ✅ Manifests updated
- ✅ Traceability maintained
