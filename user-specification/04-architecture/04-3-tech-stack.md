# 4.3 기술 스택
[← 목차로 돌아가기](../../README.md)


본 시스템의 기술 스택은 **배포 옵션과 무관하게 동일**합니다. 12-Factor App 원칙에 따라 환경 변수만 변경하면 온프레미스, Railway, AWS 어디서나 동일하게 동작합니다.

**설계 기준:** 동시 접속자 100명 규모

#### 4.3.1 Backend (공통)

**언어 및 프레임워크:**
- 언어: Python 3.11+
- 프레임워크: FastAPI
- ASGI 서버: Uvicorn (multi-worker)
- 프로세스 관리: Gunicorn + Uvicorn workers
- ORM: SQLAlchemy 2.0 (async)
- 마이그레이션: Alembic

**성능 최적화:**
- Worker 프로세스: CPU 코어 수 × 2 (예: 4코어 → 8 workers)
- Connection Pool:
  - 최소 연결: 10
  - 최대 연결: 50
  - Overflow: 20
- 비동기 I/O: asyncio, httpx

#### 4.3.2 Database (배포 옵션별)

**공통 사양:**
- DBMS: PostgreSQL 15+
- Connection Pool: asyncpg
  - pool_size: 20-50 (동시 접속자에 따라 조정)
  - max_overflow: 10
- 인덱싱 전략:
  - lot_number, process_id, worker_id에 인덱스
  - 복합 인덱스: (lot_number, process_id, created_at)
  - 파티셔닝: 3개월 단위 날짜 파티셔닝 (선택사항)

**배포 옵션별 구성:**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **PostgreSQL** | 자체 설치 (서버) | Railway PostgreSQL | RDS PostgreSQL |
| **버전** | 15+ | Railway 관리 | 15+ |
| **스토리지** | 로컬 디스크 500GB | Railway Disk | RDS gp3 500GB |
| **백업** | pg_dump (cron) | 자동 (Railway) | 자동 (RDS snapshot) |
| **접속 URL** | `postgresql://192.168.1.100:5432/mes_db` | `$DATABASE_URL` (Railway 자동) | `postgresql://mes-db.rds.amazonaws.com:5432/mes_db` |

**Caching:**
- L1 Cache: 애플리케이션 인메모리 (LRU, max 1000 items)
- L2 Cache: Redis 7.0+
  - 용도: 세션, 임시 데이터, API 캐시
  - TTL: 5분~1시간 (데이터 특성별)
  - 메모리: 4GB 권장 (온프레미스), Railway 자동, ElastiCache t3.micro (AWS)
  - Persistence: AOF (Append Only File)

**Redis 배포 옵션별:**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **Redis** | 자체 설치 (서버) | Railway Redis | ElastiCache Redis |
| **메모리** | 4GB | Railway 자동 | t3.micro (512MB) |
| **접속 URL** | `redis://192.168.1.101:6379` | `$REDIS_URL` (Railway 자동) | `redis://mes-cache.elasticache.amazonaws.com:6379` |

#### 4.3.3 Load Balancing & Reverse Proxy (배포 옵션별)

**공통 기능:**
- HTTP/2 지원
- SSL/TLS 종단 처리
- Static file 서빙 (React build)
- Gzip 압축
- Rate Limiting: 100 req/min per IP
- Health Check: /health 엔드포인트 확인
- Timeout: 30초

**배포 옵션별 구성:**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **로드 밸런서** | Nginx 1.24+ | Railway 내장 | AWS ALB |
| **알고리즘** | Least Connections | 자동 | Round Robin/Least Outstanding |
| **SSL 인증서** | Let's Encrypt | Railway 자동 (*.up.railway.app) | AWS ACM |
| **Health Check 주기** | 10초 | Railway 자동 | 30초 |
| **설정 방법** | nginx.conf 수동 편집 | railway.json | AWS Console/Terraform |

#### 4.3.4 Frontend - 작업 PC (공통)

**프레임워크:**
- PyQt5 (Python 3.11+)
- 통신: httpx (async HTTP client)
- 파일 감시: watchdog
- 프린터 통신: pyserial
- 바코드 스캐너: USB HID

**로컬 저장소:**
- SQLite (오프라인 작업 지원)
- 디렉토리: C:\neurohub_work\

**환경 변수 설정 (배포 옵션별):**

```python
# 온프레미스
API_BASE_URL=http://192.168.1.100:8000

# Railway
API_BASE_URL=https://mes-backend.up.railway.app

# AWS
API_BASE_URL=https://mes-api.yourdomain.com
```

#### 4.3.5 Dashboard - 관리자 (공통)

**접속 방식 (배포 옵션별):**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **망내 접속** | `http://192.168.1.100:3000` | `https://mes-dashboard.up.railway.app` | `https://dashboard.yourdomain.com` |
| **망외 접속** | VPN 필요 | 인터넷 접속 가능 | 인터넷 접속 가능 |
| **SSL/TLS** | Let's Encrypt 설정 | Railway 자동 제공 | AWS ACM 설정 |

**지원 브라우저:** Chrome, Edge, Firefox (최신 버전)

**사용자:**
- 생산 관리자: 생산 현황, LOT 생성/관리
- 품질 관리자: 불량 통계, 품질 분석
- 경영진: 주요 KPI 대시보드

**Frontend:**
- 프레임워크: React 18+
- 상태 관리: Zustand 또는 Redux Toolkit
- UI 라이브러리: Material-UI (MUI) 또는 Ant Design
- 차트: Chart.js 또는 Recharts
- 테이블: TanStack Table (React Table)
- HTTP Client: Axios
- 빌드 도구: Vite

**데이터 갱신 방식:**
- REST API 폴링 기반
- 대시보드 조회: `GET /api/v1/dashboard/summary` (10초 주기)
- 알림 조회: `GET /api/v1/alerts` (30초 주기)
- 자동 재시도: 실패 시 exponential backoff (2초, 4초, 8초)

#### 4.3.6 Infrastructure (배포 옵션별)

**운영 체제 및 컨테이너:**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **OS** | Ubuntu 22.04 LTS | Railway 관리 (Linux) | Ubuntu 22.04 LTS (EC2) |
| **컨테이너** | Docker + Docker Compose | Railway 내장 (Dockerfile 지원) | Docker + ECS (선택) |
| **프로세스 관리** | systemd 또는 Docker | Railway 자동 | systemd 또는 ECS |

**백업 전략:**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **DB 백업** | pg_dump (cron, 새벽 2시) | Railway 자동 (매일) | RDS 자동 스냅샷 (매일) |
| **증분 백업** | WAL archiving (선택) | Railway 관리 | RDS PITR (Point-in-Time Recovery) |
| **보관 주기** | 30일 (수동 관리) | Railway 자동 | 35일 (설정 가능) |
| **파일 백업** | NAS 또는 외부 스토리지 | Railway Volume 스냅샷 | S3 Versioning + Lifecycle |
| **복원 시간** | 수동 복원 (1-2시간) | Railway CLI (10분) | RDS 복원 (10-30분) |

**파일 저장소:**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **완공 JSON** | 로컬 디스크 (90일 보관) | Railway Volume | S3 (Lifecycle: 90일) |
| **펌웨어** | 로컬 디스크 (영구) | Railway Volume | S3 (영구, Glacier 아카이브) |
| **위치** | /var/mes/files/ | /app/files/ (Volume) | s3://mes-bucket/ |

#### 4.3.7 모니터링 & 로깅 (배포 옵션별)

**로깅 (공통):**
- 구조화 로깅: structlog (JSON 포맷)
- 로그 레벨: INFO (production), DEBUG (development)

**로그 저장 (배포 옵션별):**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **로그 파일** | /var/log/neurohub/ (30일 rotation) | Railway Logs (7일) | CloudWatch Logs (30일) |
| **중앙 집중** | Loki (선택사항) | Railway 대시보드 | CloudWatch Logs Insights |
| **검색** | grep 또는 Loki Query | Railway CLI | CloudWatch Query |
| **보관 비용** | 디스크 비용 포함 | 무료 (7일) | $0.50/GB/월 |

**모니터링 (배포 옵션별):**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **메트릭 수집** | Prometheus (자체 구축) | Railway Metrics (내장) | CloudWatch |
| **시각화** | Grafana (자체 구축) | Railway Dashboard | CloudWatch Dashboard |
| **알림** | Alertmanager → Slack/Email | Railway Alerts | CloudWatch Alarms → SNS |
| **수집 간격** | 15초 | Railway 자동 | 1분 (기본), 5초 (상세) |
| **보관 주기** | 90일 | Railway 자동 | 15개월 (CloudWatch) |

**공통 알림 기준:**
- CPU > 80% (5분 이상)
- 메모리 > 85%
- API 응답 시간 > 500ms (P95)
- 에러율 > 1%

**APM (선택사항):**
- OpenTelemetry (분산 추적)
- Jaeger (온프레미스), Railway APM (Railway), AWS X-Ray (AWS)

#### 4.3.8 보안 (배포 옵션별)

**인증 & 인가 (공통):**
- JWT (Access Token + Refresh Token)
  - Access Token TTL: 15분
  - Refresh Token TTL: 7일
- RBAC (Role-Based Access Control)
  - 역할: 관리자, 생산관리자, 작업자, 뷰어

**네트워크 보안 (배포 옵션별):**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **HTTPS/SSL** | Nginx + Let's Encrypt | Railway 자동 (*.up.railway.app) | ALB + ACM |
| **방화벽** | UFW (Ubuntu Firewall) | Railway 내장 | Security Groups |
| **허용 포트** | 22, 80, 443 | Railway 자동 관리 | 80, 443 (ALB) |
| **내부망 포트** | PostgreSQL (5432), Redis (6379) | Railway Private Network | VPC 내부 (보안 그룹) |
| **Rate Limiting** | slowapi (FastAPI middleware) | Railway 내장 + slowapi | ALB + slowapi |
| **DDoS 방어** | Fail2ban (선택사항) | Railway 자동 | AWS Shield Standard |

**데이터 보안 (공통):**
- 암호화: bcrypt (비밀번호 해싱)
- 감사 로그: 모든 CUD 작업 기록
- SQL Injection 방지: ORM (SQLAlchemy parameterized queries)

#### 4.3.9 테스트 (공통)

**Backend:**
- 단위 테스트: pytest
- API 테스트: pytest + httpx
- 부하 테스트: Locust (목표: 20 TPS, 100 동시 사용자)

**Frontend:**
- React: Jest + React Testing Library
- E2E: Playwright (선택사항)

**CI/CD (배포 옵션별):**

| 항목 | 온프레미스 | Railway | AWS |
|------|-----------|---------|-----|
| **CI** | GitHub Actions | Railway 내장 CI | GitHub Actions + CodeBuild |
| **CD** | 수동 배포 (SSH) | GitHub Push → 자동 배포 | CodeDeploy 또는 수동 |
| **테스트 자동화** | GitHub Actions | Railway Build 시 pytest 실행 | GitHub Actions |

#### 4.3.10 개발 도구 (공통)

**버전 관리:**
- Git + GitHub/GitLab
- 브랜치 전략: Git Flow

**API 문서:**
- FastAPI 자동 생성 (Swagger UI, ReDoc)
- 엔드포인트: /docs, /redoc

**환경 변수 관리:**
- 온프레미스: .env 파일 (python-dotenv)
- Railway: Railway Dashboard 또는 CLI
- AWS: Systems Manager Parameter Store 또는 .env

---

#### 4.3.11 기술 스택 요약표

| 계층 | 기술 | 목적 | 우선순위 |
|------|------|------|----------|
| **Load Balancer** | Nginx | 부하 분산, SSL 종단 | High |
| **Backend** | FastAPI + Uvicorn | REST API 서버 | High |
| **Database** | PostgreSQL 15+ | 관계형 데이터 저장 | High |
| **Cache** | Redis | 세션, API 캐시 | High |
| **ORM** | SQLAlchemy 2.0 | 데이터베이스 추상화 | High |
| **Frontend (작업 PC)** | PyQt5 | 데스크톱 앱 | High |
| **Dashboard** | React 18 | 관리자 웹 | High |
| **모니터링** | Prometheus + Grafana | 시스템 모니터링 | High |
| **로깅** | structlog | 구조화 로그 | Medium |
| **백업** | pg_dump + Cron | 데이터 백업 | High |
| **컨테이너** | Docker | 배포 환경 관리 | Medium |
| **APM** | OpenTelemetry | 분산 추적 (선택) | Low |


---\n\n**이전 섹션:** [4.2 시스템 구성 및 설계](04-2-system-design.md)\n**다음 섹션:** [5.1 ERD 및 데이터베이스 스키마](../05-data-design/05-1-erd.md)
