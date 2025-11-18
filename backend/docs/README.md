# Backend Documentation

Welcome to the F2X NeuroHub Backend documentation!

## 📚 Documentation Structure

```
docs/
├── README.md                  # This file - Documentation index
│
├── api/                       # API Documentation
│   └── API_ENDPOINTS.md      # Complete API reference
│
├── guides/                    # Development & Deployment Guides
│   ├── DEVELOPMENT.md        # Development workflow
│   └── DEPLOYMENT.md         # Production deployment
│
├── testing/                   # Testing Documentation
│   ├── TEST_PLAN.md          # Test strategy
│   └── BACKEND_TEST_COMPLETION_REPORT.md  # Test results
│
└── database/                  # Database-specific docs
    └── (legacy database docs)
```

## 🚀 Quick Links

### For Developers
- **[Development Guide](guides/DEVELOPMENT.md)** - Start here for local development setup
- **[API Endpoints](api/API_ENDPOINTS.md)** - Complete API reference with examples
- **[Test Plan](testing/TEST_PLAN.md)** - Testing strategy and how to run tests

### For DevOps
- **[Deployment Guide](guides/DEPLOYMENT.md)** - Production deployment instructions
- **[Backend README](../README.md)** - Project overview and quick start

### Interactive Documentation
When the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📖 Document Descriptions

### API Documentation

#### [API_ENDPOINTS.md](api/API_ENDPOINTS.md)
Complete API reference covering:
- Authentication endpoints
- User management
- Product models
- Processes
- Lot & serial tracking
- Process data collection
- Analytics
- Audit logs
- Error responses

### Guides

#### [DEVELOPMENT.md](guides/DEVELOPMENT.md)
Development workflow including:
- Local setup instructions
- Project structure explanation
- Creating new features (models, endpoints, etc.)
- Code style guidelines
- Testing strategies
- Debugging tips
- Common tasks

#### [DEPLOYMENT.md](guides/DEPLOYMENT.md)
Production deployment covering:
- Environment setup
- Docker deployment
- Traditional server deployment
- Nginx configuration
- Process management (systemd)
- Performance tuning
- Monitoring and logging
- Backup strategies
- Security checklist
- Rollback procedures

### Testing

#### [TEST_PLAN.md](testing/TEST_PLAN.md)
Testing strategy including:
- Test categories (unit, integration)
- Coverage goals
- Test structure
- Running tests

#### [BACKEND_TEST_COMPLETION_REPORT.md](testing/BACKEND_TEST_COMPLETION_REPORT.md)
Latest test execution results:
- Test pass/fail statistics
- Coverage metrics
- Known issues
- Fixed bugs

## 🔍 How to Use This Documentation

### I want to...

**Set up local development environment**
→ Read [Development Guide - Getting Started](guides/DEVELOPMENT.md#getting-started)

**Understand the API endpoints**
→ Check [API Endpoints Reference](api/API_ENDPOINTS.md)

**Add a new feature**
→ Follow [Development Guide - Creating a New Feature](guides/DEVELOPMENT.md#creating-a-new-feature)

**Deploy to production**
→ Follow [Deployment Guide](guides/DEPLOYMENT.md)

**Run tests**
→ See [Test Plan](testing/TEST_PLAN.md) or [Development Guide - Testing](guides/DEVELOPMENT.md#testing-strategy)

**Debug an issue**
→ Check [Development Guide - Debugging](guides/DEVELOPMENT.md#debugging)

**Add database tables**
→ See [Development Guide - Adding a New Model](guides/DEVELOPMENT.md#adding-a-new-model)

## 📊 Project Status

- **Backend API**: ✅ Complete (80+ endpoints)
- **Authentication**: ✅ JWT with RBAC
- **Database**: ✅ PostgreSQL schema deployed
- **Tests**: 🔄 In Progress (100/148 passing)
- **Documentation**: ✅ Comprehensive
- **Deployment**: ✅ Docker & Traditional methods

## 🤝 Contributing

When adding new features:
1. Update relevant documentation
2. Add API endpoint documentation to `API_ENDPOINTS.md`
3. Write tests (see Test Plan)
4. Update README.md if needed

## 📝 Documentation Maintenance

Please keep documentation up-to-date:
- Update API docs when adding/modifying endpoints
- Update guides when workflow changes
- Update test reports after major test runs
- Keep version numbers current

## 🔗 Related Documentation

- **[Project Root README](../../README.md)** - Overall project documentation
- **[Database Documentation](../../database/README.md)** - PostgreSQL schema
- **[Backend README](../README.md)** - Backend overview

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
