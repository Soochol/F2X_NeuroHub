---
name: deploy
description: Generate deployment configurations (Docker, CI/CD, Nginx) for production deployment
---

You are orchestrating **deployment configuration generation** using the deployment-agent.

## Mission

Generate production-ready deployment configurations:
- **Docker**: Multi-stage Dockerfile, docker-compose.yml
- **CI/CD**: GitHub Actions or GitLab CI pipeline
- **Web Server**: Nginx reverse proxy configuration
- **Scripts**: Deployment, rollback, health check scripts
- **Environment**: .env.example templates

## When to Use

Run this command when:
- ✅ Development is complete (`/full` command finished)
- ✅ Multiple features implemented and ready for deployment
- ✅ Need to update deployment configurations
- ✅ Setting up new environment (staging, production)

## Pipeline Execution

### Phase 1: Read Architecture Design

**Steps**:
1. Locate architecture design document
   - `docs/design/architecture/ARCH-APP-*.md`
2. Read deployment options:
   - Docker (local, cloud)
   - Database type (PostgreSQL, MySQL, etc.)
   - Additional services (Redis, message queue, etc.)
3. Read non-functional requirements:
   - `docs/requirements/` - Performance, security requirements

**Expected Input**:
```
docs/design/architecture/ARCH-APP-001.md
→ Deployment option: Docker
→ Database: PostgreSQL
→ Additional services: Redis, Nginx
→ Backend: FastAPI (Python 3.11)
```

---

### Phase 2: Generate Deployment Configurations

**Agent**: deployment-agent
**Input**: Architecture design + NFRs
**Output**: Deployment configuration files

**Generated Files**:

#### 1. Docker Configuration
```
Dockerfile                    # Multi-stage build
docker-compose.yml            # Services orchestration
.dockerignore                 # Build optimization
```

#### 2. CI/CD Pipeline
```
.github/workflows/deploy.yml  # Deployment pipeline
.github/workflows/test.yml    # Testing pipeline
```

#### 3. Web Server Configuration
```
nginx.conf                    # Reverse proxy, SSL, security headers
```

#### 4. Deployment Scripts
```
scripts/
├── deploy.sh                 # Zero-downtime deployment
├── rollback.sh               # Rollback to previous version
└── health_check.sh           # Health verification
```

#### 5. Environment Configuration
```
.env.example                  # Environment variables template
```

**Security Features**:
- ✅ Non-root Docker user
- ✅ Multi-stage builds (smaller images)
- ✅ Health checks configured
- ✅ SSL/TLS with modern ciphers
- ✅ Security headers (HSTS, CSP, etc.)
- ✅ Rate limiting
- ✅ Secrets management (no hardcoded secrets)

**DevOps Best Practices**:
- ✅ 12-Factor App principles
- ✅ Zero-downtime deployment
- ✅ Automated testing in CI/CD
- ✅ Database backup before deployment
- ✅ Rollback capability
- ✅ Health check monitoring

---

### Phase 3: Validation

**Steps**:
1. Verify all files generated
2. Check syntax (Dockerfile, docker-compose.yml, nginx.conf)
3. Ensure secrets are not hardcoded
4. Validate environment variables documented

**Validation Checklist**:
- [ ] Dockerfile uses multi-stage build
- [ ] docker-compose.yml includes all services
- [ ] Health checks configured for all services
- [ ] nginx.conf has SSL and security headers
- [ ] CI/CD pipeline includes tests
- [ ] Deployment script has rollback capability
- [ ] .env.example documents all required variables

---

## Final Report

After deployment configuration complete, generate summary:

```markdown
# Deployment Configuration Complete

**Generated**: {timestamp}
**Architecture**: {architecture_pattern}

## Files Generated

### Docker Configuration (3 files)
- ✅ Dockerfile (multi-stage, non-root user)
- ✅ docker-compose.yml (backend + DB + nginx + redis)
- ✅ .dockerignore (build optimization)

### CI/CD Pipeline (2 files)
- ✅ .github/workflows/deploy.yml (automated deployment)
- ✅ .github/workflows/test.yml (automated testing)

### Web Server (1 file)
- ✅ nginx.conf (reverse proxy, SSL, rate limiting)

### Deployment Scripts (3 files)
- ✅ scripts/deploy.sh (zero-downtime deployment)
- ✅ scripts/rollback.sh (rollback capability)
- ✅ scripts/health_check.sh (health verification)

### Environment Configuration (1 file)
- ✅ .env.example (all variables documented)

**Total**: 10 files generated

## Security Features

✅ Multi-stage Docker builds
✅ Non-root user in containers
✅ SSL/TLS with modern ciphers
✅ Security headers (HSTS, CSP, X-Frame-Options)
✅ Rate limiting (10 req/s with burst)
✅ No secrets in images or config files
✅ Health checks for all services

## Deployment Options

### Option 1: Local Development
\`\`\`bash
docker-compose up --build
\`\`\`

### Option 2: Staging Deployment
\`\`\`bash
./scripts/deploy.sh staging
\`\`\`

### Option 3: Production Deployment
\`\`\`bash
# Via CI/CD (GitHub Actions)
git push origin main

# Or manual
./scripts/deploy.sh production
\`\`\`

### Health Check
\`\`\`bash
./scripts/health_check.sh
\`\`\`

### Rollback (if needed)
\`\`\`bash
./scripts/rollback.sh
\`\`\`

## Environment Variables

Required environment variables (see .env.example):
- DATABASE_URL
- JWT_SECRET
- SECRET_KEY
- DB_USER
- DB_PASSWORD
- REDIS_URL
- (see .env.example for complete list)

## Next Steps

1. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Fill in production values
   - Store secrets in secret manager (AWS Secrets Manager, HashiCorp Vault)

2. **Deploy to Staging**:
   \`\`\`bash
   ./scripts/deploy.sh staging
   \`\`\`

3. **Run Health Checks**:
   \`\`\`bash
   ./scripts/health_check.sh
   \`\`\`

4. **Deploy to Production**:
   - Push to main branch (triggers CI/CD)
   - Or run: `./scripts/deploy.sh production`

---

✅ Deployment configurations ready! Follow Next Steps to deploy.
```

## Error Handling

### If Generation Fails:

**Architecture Document Not Found**:
- Error: `docs/design/architecture/ARCH-APP-*.md` not found
- Action: Run `/full` command first to generate architecture design

**Invalid Deployment Option**:
- Error: Unsupported deployment target
- Action: Update architecture document with valid option (Docker, Kubernetes, etc.)

**Missing Dependencies**:
- Error: Required service not specified (DB, cache, etc.)
- Action: Update architecture design to include all required services

## Workflow Diagram

```
/deploy Command
    ↓
Read Architecture Design
    ↓
[deployment-agent]
    ↓
Generate Docker Configs
    ↓
Generate CI/CD Pipelines
    ↓
Generate Nginx Config
    ↓
Generate Deployment Scripts
    ↓
Generate .env.example
    ↓
Validate All Configurations
    ↓
Final Report → Ready to Deploy
```

## Agent Invocation

```python
# Read architecture
architecture = read_file('docs/design/architecture/ARCH-APP-001.md')

# Generate deployment configs
deployment_result = invoke_agent(
    agent='deployment-agent',
    input={
        'architecture_path': 'docs/design/architecture/ARCH-APP-001.md',
        'deployment_target': 'docker',  # or 'kubernetes', 'cloud'
        'environment': 'production'
    }
)

# Validate
assert all_files_generated(), "All deployment files must be generated"
assert no_secrets_hardcoded(), "No secrets should be in config files"
```

## Success Criteria

Deployment configuration succeeds if:
- ✅ All 10 files generated correctly
- ✅ Dockerfile uses multi-stage builds
- ✅ docker-compose.yml includes all services
- ✅ Health checks configured
- ✅ CI/CD pipeline includes automated tests
- ✅ Nginx configured with SSL and security headers
- ✅ Deployment scripts have zero-downtime strategy
- ✅ No secrets hardcoded anywhere
- ✅ All environment variables documented

---

**Philosophy**: "Deploy early, deploy often, deploy safely" - generate production-ready configs that follow DevOps best practices!
