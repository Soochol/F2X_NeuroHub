# Database Documentation

F2X NeuroHub MES PostgreSQL Database documentation.

## Documentation Structure

```
database/.docs/
├── README.md                           # This file
├── DOCUMENTATION_ANALYSIS_REPORT.md    # Analysis and issues
├── guides/                             # Deployment & Operations
│   ├── QUICK_START.md                  # Quick deployment guide
│   ├── DEPLOYMENT_GUIDE.md             # Complete deployment reference
│   ├── DEPLOYMENT_DIAGRAM.md           # Visual deployment diagrams
│   └── VERIFICATION_GUIDE.md           # Post-deployment validation
└── requirements/                       # Database Design
    ├── 01-ERD.md                       # Entity-Relationship Diagram
    ├── 02-entity-definitions.md        # Entity specifications
    ├── 03-relationship-specifications.md # FK constraints
    └── DATABASE-REQUIREMENTS.md        # High-level requirements
```

## Quick Links

### Getting Started

- **[Quick Start](guides/QUICK_START.md)** - One-command deployment
- **[Deployment Guide](guides/DEPLOYMENT_GUIDE.md)** - Complete deployment reference
- **[Verification Guide](guides/VERIFICATION_GUIDE.md)** - Post-deployment validation

### Database Design

- **[ERD](requirements/01-ERD.md)** - Entity-Relationship Diagram
- **[Entity Definitions](requirements/02-entity-definitions.md)** - Table schemas
- **[Relationships](requirements/03-relationship-specifications.md)** - FK constraints
- **[Requirements](requirements/DATABASE-REQUIREMENTS.md)** - High-level specs

## Technology Stack

- **PostgreSQL 14+** - Primary database
- **SQLAlchemy 2.0** - ORM with async support
- **asyncpg** - Async PostgreSQL driver

## Key Features

- 7 core entities + 2 P2 entities (production_lines, equipment)
- 14 database functions (5 common + 9 table-specific)
- 50+ indexes with GIN support for JSONB
- 20+ triggers for business logic
- Partitioned audit_logs for performance
- JSONB for flexible measurement data

## Business Rules

| Rule | Description |
|------|-------------|
| BR-001 | LOT number format: {COUNTRY}{LINE}{MODEL}{YYMM}{SEQ} (14 chars) |
| BR-002 | Serial number format: {LOT_NUMBER}{SEQ} (18 chars) |
| BR-003 | Maximum 100 serials per LOT |
| BR-004 | Maximum 3 rework attempts |
| BR-005 | Process sequence enforcement (1-8) |
| BR-006 | Status transitions validation |
| BR-007 | Label printing requires all prior processes PASS |

## Performance Targets

- Query response: < 500ms
- Connection pool: 50 connections
- Throughput: 20 TPS
- Data volume: up to 40M process_data records/year

## Implementation Status

- **Requirements**: Ready for Implementation (v1.0, 2025-11-17)
- **Deployment**: Documented and tested
- **Verification**: CI/CD examples included

---

**Last Updated**: 2025-11-20
