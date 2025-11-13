# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**F2X NeuroHub MES** is a Manufacturing Execution System (MES) for Withforce, a Korean manufacturer of wearable robots. This repository is currently in the **pre-development phase** - it contains comprehensive user specifications and an AI-driven TDD automation framework, but no application code has been generated yet.

**Key Characteristics**:
- Documentation-first approach with approved, production-ready specifications
- AI-driven development using specialized Claude agents
- Test-Driven Development (TDD) methodology with RED → GREEN → Verification phases
- Clean Architecture pattern with clear layer separation
- All documentation in Korean

## Repository Structure

```
F2X_NeuroHub/
├── .claude/
│   ├── agents/              # 7 specialized development agents
│   │   ├── requirements-agent.md    # Interactive requirements gathering
│   │   ├── design-agent.md          # System architecture & design
│   │   ├── implementation-agent.md  # Code generation (GREEN phase)
│   │   ├── testing-agent.md         # Test generation (RED phase)
│   │   ├── verification-agent.md    # Document-code traceability
│   │   └── deployment-agent.md      # Docker, CI/CD, deployment configs
│   └── commands/            # 4 automation commands
│       ├── full.md          # Complete TDD pipeline (design → code → tests → verification)
│       ├── tdd.md           # TDD workflow execution
│       ├── deploy.md        # Deployment configuration generation
│       └── implement-tdd.md # Module-specific TDD implementation
│
├── user-specification/      # Complete project specifications (APPROVED)
│   ├── 1.0 프로젝트 개요.md
│   ├── 2.0 요구사항 분석.md
│   ├── 3.0 아키텍처 설계.md
│   ├── 4.0 데이터베이스 설계.md
│   └── ...
│
├── docs/
│   ├── _utils/              # Python utilities for ID generation and manifest management
│   ├── requirements/        # Will contain FR and AC documents (not created yet)
│   ├── design/              # Will contain architecture, API, DB, class designs
│   ├── verification/        # Will contain traceability matrices and verification reports
│   └── progress/            # Session tracking documents from all agents
│
├── app/                     # Application code (EMPTY - to be generated)
│   ├── domain/              # Business entities, value objects, domain services
│   ├── application/         # Use cases, DTOs, application interfaces
│   ├── infrastructure/      # Database, external APIs, infrastructure services
│   └── presentation/        # REST API controllers, UI
│
└── tests/                   # Test code (EMPTY - to be generated)
    ├── unit/
    ├── integration/
    └── e2e/
```

## Technology Stack

**Backend**:
- Python 3.11+
- FastAPI (REST API framework)
- SQLAlchemy (ORM)
- PostgreSQL (primary database)
- pytest (testing framework)

**Frontend**:
- React (web UI)
- PyQt5 (desktop client - optional)

**Infrastructure**:
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Deployment options: On-premise, Railway, AWS

## Development Workflow

### Phase 1: Interactive Requirements Gathering

**CRITICAL**: All features start with interactive requirements gathering.

```bash
# DO NOT use /full command first!
# Start by invoking the requirements-agent directly
```

The `requirements-agent` conducts a 6-stage dialogue with you:
1. **Initial Understanding**: Purpose, users, value proposition
2. **Entity & Data Exploration**: Data structures, relationships
3. **Operations & Workflows**: User actions, scenarios
4. **Business Rules & Constraints**: Validation, authorization, performance
5. **Edge Cases & Errors**: Error scenarios, boundary conditions
6. **Confirmation & Documentation**: Review and confirm requirements

**Output**:
- `docs/requirements/modules/{module}/FR-{MOD}-{SEQ}-{feature}.md` (Functional Requirements)
- `docs/requirements/modules/{module}/AC-{MOD}-{SEQ}-test-plan.md` (Acceptance Criteria)
- `docs/progress/requirements/{module}/session-{timestamp}.md` (Progress log)

### Phase 2: Automated Development Pipeline

**After requirements exist**, run the `/full` command:

```bash
/full --module {module_name}
```

This executes 4 automated phases:

**Phase 1 - Design** (`design-agent`):
- Selects architecture pattern (Clean Architecture, Layered, DDD)
- Designs project folder structure
- Creates class diagrams with inheritance relationships (text-based UML)
- Defines RESTful API endpoints
- Designs normalized database schema (3NF)
- Creates component architecture
- Output: `docs/design/` + progress tracking

**Phase 2 - TDD Red** (`testing-agent`):
- Generates unit tests (70% coverage)
- Generates integration tests (20%)
- Generates E2E tests (10%)
- Runs pytest → **ALL TESTS MUST FAIL** (RED phase ✅)
- Output: `tests/` + progress tracking

**Phase 3 - TDD Green** (`implementation-agent`):
- Implements domain entities
- Implements application services
- Implements infrastructure repositories
- Implements API controllers
- Runs pytest → **ALL TESTS MUST PASS** (GREEN phase ✅)
- Output: `app/` + progress tracking

**Phase 4 - Verification** (`verification-agent`):
- Parses FR documents with AST
- Analyzes code with AST
- Analyzes tests with AST
- Generates traceability matrix (FR → Code → Test)
- Identifies gaps (missing implementation, missing tests, orphaned code)
- Output: `docs/verification/{module}/` + progress tracking

### Phase 3: Deployment Configuration (Separate)

```bash
/deploy
```

Generates deployment configurations:
- Dockerfile (backend, frontend)
- docker-compose.yml
- CI/CD pipelines (GitHub Actions)
- Nginx configuration
- Environment variable templates
- Deployment scripts

## Available Commands

### `/full` - Complete TDD Automation Pipeline

Executes Design → TDD Red → TDD Green → Verification phases.

**Prerequisites**: Requirements documents must exist in `docs/requirements/modules/{module}/`

**Usage**:
```bash
/full --module inventory
```

**Output**: Complete module implementation with design docs, tests, code, and verification reports.

### `/tdd` - TDD Workflow Execution

Analyzes your prompt and runs appropriate agents to implement features using TDD methodology.

**Usage**:
```bash
/tdd 주문 생성 기능 구현
```

### `/implement-tdd` - Module-Specific TDD Implementation

Implements code using TDD for a specific module or document ID.

**Usage**:
```bash
/implement-tdd --module inventory
/implement-tdd --id FR-INV-001
```

### `/deploy` - Deployment Configuration Generation

Generates all deployment configurations (Docker, CI/CD, Nginx).

**Usage**:
```bash
/deploy
```

## Progress Tracking System

**Every agent** creates progress tracking documents in `docs/progress/{agent-name}/{module}/session-{timestamp}.md`.

Progress documents include:
- Session metadata (date, module, status)
- Stage-by-stage progress with emoji indicators (✅ Done, 🔄 In Progress, ⏳ Pending)
- Detailed logs of actions taken
- Checklists of deliverables
- Next steps

**Example locations**:
- `docs/progress/requirements/inventory/session-2025-01-15-10-30.md`
- `docs/progress/design/inventory/design-session-2025-01-15-11-00.md`
- `docs/progress/testing/inventory/testing-session-2025-01-15-12-00.md`
- `docs/progress/implementation/inventory/implementation-session-2025-01-15-13-00.md`
- `docs/progress/verification/inventory/verification-session-2025-01-15-14-00.md`

## Architecture Pattern

**Clean Architecture** (preferred for this project):

```
┌─────────────────────────────────────────────────────┐
│                 Presentation Layer                  │
│              (FastAPI Controllers, UI)              │
├─────────────────────────────────────────────────────┤
│                Application Layer                    │
│           (Use Cases, DTOs, Interfaces)             │
├─────────────────────────────────────────────────────┤
│                  Domain Layer                       │
│      (Entities, Value Objects, Domain Services)     │
├─────────────────────────────────────────────────────┤
│              Infrastructure Layer                   │
│    (Database, External APIs, Infrastructure Services)│
└─────────────────────────────────────────────────────┘
```

**Dependency Rule**: Dependencies point inward. Domain layer has no dependencies on outer layers.

## Document ID System

All documents use standardized IDs:

- **FR-{MOD}-{SEQ}**: Functional Requirements (e.g., FR-INV-001)
- **AC-{MOD}-{SEQ}**: Acceptance Criteria (e.g., AC-INV-001)
- **API-{MOD}-{SEQ}**: API Specifications (e.g., API-INV-001)
- **DB-{MOD}-{SEQ}**: Database Schemas (e.g., DB-INV-001)
- **CLASS-{MOD}-{SEQ}**: Class Diagrams (e.g., CLASS-INV-001)
- **STRUCT-{APP}-{SEQ}**: Project Structure (e.g., STRUCT-APP-001)

**Module Codes** (3 letters):
- INV: Inventory
- ORD: Order
- PRD: Production
- QLT: Quality
- USR: User Management

## Key Principles

1. **Documentation-First**: All features start with requirements documentation through interactive dialogue
2. **TDD Methodology**: RED (failing tests) → GREEN (passing implementation) → Refactor
3. **Traceability**: Every piece of code must reference an FR document ID in docstrings
4. **Progress Tracking**: Every agent creates session tracking documents
5. **Clean Architecture**: Clear separation of concerns with dependency inversion
6. **Testability**: Target 80%+ test coverage with unit, integration, and E2E tests

## Common Workflows

### Scenario 1: Implementing a New Feature

```bash
# Step 1: Gather requirements interactively
# (Invoke requirements-agent directly, answer questions)

# Step 2: Run full automation pipeline
/full --module {module_name}

# Step 3: (Optional) Generate deployment configs
/deploy
```

### Scenario 2: Quick TDD Implementation

```bash
# For smaller features where requirements are already clear
/tdd 재고 조회 기능 구현
```

### Scenario 3: Implementing from Existing Requirements

```bash
# If FR documents already exist
/implement-tdd --module inventory
```

## Important Notes

- **No Application Code Yet**: This repository is in pre-development phase. The `app/` and `tests/` directories are empty.
- **Requirements First**: Never run `/full` without creating requirements documents first through interactive dialogue with `requirements-agent`.
- **Korean Language**: All user specifications and documentation are in Korean.
- **Progress History**: Always check `docs/progress/` directories to understand what has been done previously.
- **Verification**: After implementation, always check `docs/verification/` for traceability reports and gaps.

## Getting Started

If this is your first time working on a feature:

1. **Understand the project**: Read `user-specification/1.0 프로젝트 개요.md`
2. **Invoke requirements-agent**: Start interactive dialogue to define your feature
3. **Run `/full`**: Execute automated development pipeline
4. **Review progress**: Check `docs/progress/` to see what was generated
5. **Run tests**: `pytest tests/ -v --cov=app`
6. **Review verification**: Check `docs/verification/` for traceability and gaps

## Utilities

- **ID Generator**: `docs/_utils/id_generator.py` - Generates document IDs and filenames
- **Manifest Manager**: `docs/_utils/manifest_manager.py` - Updates manifest.json with document metadata

## Contact & Support

For questions about this AI-driven development system, refer to the agent documentation in `.claude/agents/`.
