# 4.2 시스템 구성 및 설계

[← 목차로 돌아가기](../../README.md)

## 4.2 시스템 구성도

본 섹션에서는 배포 옵션별 시스템 아키텍처 구성도를 제공합니다.

> ⚠️ **네트워크 요구사항**:
> - **온프레미스**: 내부 LAN만 필요 (인터넷 불필요)
> - **클라우드(Railway/AWS)**: 인터넷 연결 필수

### 4.2.1 Option A: 온프레미스 구성도 (인터넷 불필요)

```mermaid
graph TB
    subgraph Factory["생산 현장 (공장 내부)"]
        PC1[작업 PC 1-7<br/>PyQt5 App]
        PC2[바코드 스캐너]
        PC3[라벨 프린터<br/>Zebra ZT]
    end

    subgraph OnPremServer["온프레미스 서버실"]
        subgraph BackendServers["백엔드 서버 (2대)"]
            Backend1[FastAPI Server 1]
            Backend2[FastAPI Server 2]
        end
        subgraph DBServer["DB 서버 (1대)"]
            DB[(PostgreSQL 15+)]
            Redis[(Redis 7.0+)]
        end
        Nginx[Nginx<br/>Load Balancer]
    end

    subgraph Office["관리자 (사무실)"]
        Dashboard[React Dashboard<br/>웹 브라우저]
    end

    PC1 -->|내부 LAN| Nginx
    PC2 --> PC1
    PC3 --> PC1
    Dashboard -->|내부 LAN| Nginx
    Nginx --> Backend1
    Nginx --> Backend2
    Backend1 --> DB
    Backend1 --> Redis
    Backend2 --> DB
    Backend2 --> Redis
```

**특징:**
- ✅ 인터넷 불필요 - 내부 LAN만 사용
- ✅ 외부 네트워크 차단 가능
- ✅ ISP 장애와 무관

---

### 4.2.2 Option B-1: Railway 구성도 (인터넷 필수)

```mermaid
graph TB
    subgraph Factory["생산 현장"]
        PC1[작업 PC 1-7<br/>PyQt5 App]
        PC2[바코드 스캐너]
        PC3[라벨 프린터<br/>Zebra ZT]
    end

    subgraph RailwayCloud["Railway Cloud Platform"]
        Backend[FastAPI Service<br/>Auto-scaled]
        DB[(Railway PostgreSQL)]
        Redis[(Railway Redis)]
        Volume[Railway Volume<br/>File Storage]
    end

    subgraph Office["관리자"]
        Dashboard[React Dashboard<br/>웹 브라우저]
    end

    PC1 -->|인터넷<br/>HTTPS| Backend
    PC2 --> PC1
    PC3 --> PC1
    Dashboard -->|인터넷<br/>HTTPS| Backend
    Backend --> DB
    Backend --> Redis
    Backend --> Volume
```

**특징:**
- ⚠️ **인터넷 연결 필수** - 작업 PC가 Railway 서버에 접근
- ⚠️ ISP 장애 시 작업 중단
- ✅ 인프라 관리 불필요

---

### 4.2.3 Option B-2: AWS 구성도 (인터넷 필수)

```mermaid
graph TB
    subgraph Factory["생산 현장"]
        PC1[작업 PC 1-7<br/>PyQt5 App]
        PC2[바코드 스캐너]
        PC3[라벨 프린터<br/>Zebra ZT]
    end

    subgraph AWS["AWS Cloud"]
        subgraph VPC["VPC (Virtual Private Cloud)"]
            ALB[Application Load Balancer]
            subgraph EC2["EC2 Instances"]
                Backend1[FastAPI Server 1<br/>t3.medium]
                Backend2[FastAPI Server 2<br/>t3.medium]
            end
            RDS[(RDS PostgreSQL<br/>db.t3.medium)]
            ElastiCache[(ElastiCache Redis<br/>t3.micro)]
            S3[S3 Bucket<br/>File Storage]
        end
    end

    subgraph Office["관리자"]
        Dashboard[React Dashboard<br/>웹 브라우저]
    end

    PC1 -->|인터넷<br/>HTTPS| ALB
    PC2 --> PC1
    PC3 --> PC1
    Dashboard -->|인터넷<br/>HTTPS| ALB
    ALB --> Backend1
    ALB --> Backend2
    Backend1 --> RDS
    Backend1 --> ElastiCache
    Backend1 --> S3
    Backend2 --> RDS
    Backend2 --> ElastiCache
    Backend2 --> S3
```

**특징:**
- ⚠️ **인터넷 연결 필수** - 작업 PC가 AWS 서버에 접근
- ⚠️ ISP 장애 시 작업 중단
- ✅ VPN 터널로 보안 강화 가능
- ✅ 엔터프라이즈급 안정성

---

## 4.4 배포 아키텍처

**설계 목표:** 동시 접속자 100명 지원, 향후 200명까지 확장 가능

본 섹션에서는 선택한 배포 옵션에 따른 상세 아키텍처를 제공합니다.

---

### 4.4.1 Option A: 온프레미스 배포 아키텍처

#### 서버 구성

**아키텍처:**

```text
                    Internal LAN
                        |
                   [WiFi Router]
                        |
        +---------------+----------------+
        |               |                |
   [작업 PC 1-7]   [관리자 PC]    [Primary Server]
                                         |
                         +---------------+--------------+
                         |               |              |
                    [Nginx]       [PostgreSQL]      [Redis]
                         |
                +--------+--------+
                |                 |
          [FastAPI         [FastAPI
           Worker 1]        Worker 2-8]
```

#### 서버 스펙 권장

- **CPU:** 8 코어 (Intel Xeon 또는 AMD EPYC)
- **RAM:** 32GB
- **Storage:** 500GB SSD (NVMe)
- **네트워크:** 1Gbps
- **OS:** Ubuntu 22.04 LTS

#### 컴포넌트 배치

| 컴포넌트 | 포트 | 프로세스 수 | 메모리 할당 |
|---------|------|------------|-----------|
| Nginx | 80, 443 | 1 | 512MB |
| FastAPI (Uvicorn) | 8000 | 8 workers | 4GB (총) |
| PostgreSQL 15 | 5432 | 1 | 8GB |
| Redis 7.0 | 6379 | 1 | 4GB |
| Prometheus | 9090 | 1 | 2GB |
| Grafana | 3000 | 1 | 512MB |
| **총합** | - | - | **약 20GB** |

#### 연결 흐름

1. 클라이언트 → Nginx (443) → SSL 종단
2. Nginx → FastAPI (8000) → 8개 worker에 로드 밸런싱
3. FastAPI → PostgreSQL (5432) → Connection Pool (50 connections)
4. FastAPI → Redis (6379) → 캐시 조회/저장

#### 성능 지표

- **동시 접속자:** 100명 (최대 200명)
- **API 응답 시간:** 평균 100ms
- **데이터베이스 TPS:** 약 500 TPS
- **네트워크 대역폭:** 피크 시 10Mbps

---

### 4.4.2 Option B-1: Railway 배포 아키텍처

#### 서비스 구성

Railway는 PaaS(Platform as a Service)로 인프라 관리가 자동화됩니다.

**Railway 서비스:**

| 서비스 | 타입 | 설정 |
|--------|------|------|
| **Backend** | Web Service | FastAPI (Python 3.11) |
| **Database** | PostgreSQL | 15.x (Managed) |
| **Cache** | Redis | 7.x (Managed) |
| **Volume** | Persistent Storage | 10GB (펌웨어, 로그) |

#### 자동 스케일링 설정

```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[scaling]
minReplicas = 1
maxReplicas = 3
targetCPU = 70
targetMemory = 80
```

#### 환경 변수 관리

Railway Dashboard에서 다음 환경 변수 설정:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Railway 자동 주입
REDIS_URL=${{Redis.REDIS_URL}}          # Railway 자동 주입
USE_S3=false
FIRMWARE_DIR=/app/data/firmware
API_HOST=0.0.0.0
API_PORT=${{PORT}}                      # Railway 자동 할당
SECRET_KEY=your-production-secret-key
```

#### 모니터링 및 로그

- **메트릭:** CPU, 메모리, 디스크, 네트워크 자동 수집
- **로그:** Railway Dashboard에서 실시간 조회
- **알림:** Slack/Discord/Email 연동 가능
- **백업:** PostgreSQL 자동 백업 (7일 보관)

#### 비용 최적화

- **Free Tier:** 월 $5 크레딧 (개발/테스트용)
- **Production 권장:** ~$20-30/월 (약 26만원)
  - Backend: $10
  - PostgreSQL: $5
  - Redis: $5
  - Volume: $2

---

### 4.4.3 Option B-2: AWS 배포 아키텍처

#### AWS 리소스 구성

**권장 인스턴스:**

| 리소스 | 인스턴스 타입 | 스펙 | 용도 |
|--------|-------------|------|------|
| **EC2** | t3.medium × 2 | 2 vCPU, 4GB RAM | FastAPI Backend |
| **RDS** | db.t3.medium | 2 vCPU, 4GB RAM | PostgreSQL 15 (Multi-AZ) |
| **ElastiCache** | cache.t3.micro | 2 vCPU, 512MB | Redis 7.x |
| **ALB** | Application Load Balancer | - | 로드 밸런싱 |
| **S3** | Standard | - | 펌웨어 저장소 |

#### VPC 및 네트워크 구성

```text
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24)
│   └── ALB (Internet-facing)
├── Private Subnet (10.0.10.0/24)
│   ├── EC2 Instance 1 (FastAPI)
│   └── EC2 Instance 2 (FastAPI)
└── Private Subnet (10.0.20.0/24)
    ├── RDS PostgreSQL (Multi-AZ)
    └── ElastiCache Redis
```

#### 보안 그룹 설정

**ALB Security Group:**
- Inbound: 0.0.0.0/0 → 443 (HTTPS)
- Outbound: Private Subnet → 8000 (FastAPI)

**EC2 Security Group:**
- Inbound: ALB → 8000
- Outbound: RDS → 5432, ElastiCache → 6379, S3 → 443

**RDS Security Group:**
- Inbound: EC2 → 5432
- Outbound: None

**ElastiCache Security Group:**
- Inbound: EC2 → 6379
- Outbound: None

#### 고가용성(HA) 구성

- **RDS Multi-AZ:** 자동 장애 복구 (Failover 1-2분)
- **EC2 Auto Scaling:** CPU 70% 이상 시 자동 스케일 아웃
- **ALB Health Check:** 30초마다 `/health` 엔드포인트 체크
- **S3 버전 관리:** 파일 삭제/수정 시 복구 가능

#### 백업 전략

| 항목 | 방식 | 보관 기간 |
|------|------|---------|
| **RDS Snapshot** | 자동 (매일 새벽 2시) | 7일 |
| **S3 버킷** | Versioning 활성화 | 90일 |
| **Application 로그** | CloudWatch Logs | 30일 |

#### 모니터링 및 알림

**CloudWatch 메트릭:**
- EC2: CPU, 메모리, 디스크, 네트워크
- RDS: Connection Count, Read/Write IOPS, Storage
- ALB: Target Response Time, HTTP 4xx/5xx 에러율
- ElastiCache: Cache Hit Rate, Memory Usage

**CloudWatch Alarms (예시):**
```bash
# RDS CPU 사용률 80% 이상
aws cloudwatch put-metric-alarm \
  --alarm-name neurohub-rds-cpu-high \
  --metric-name CPUUtilization \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# ALB 5xx 에러율 5% 이상
aws cloudwatch put-metric-alarm \
  --alarm-name neurohub-alb-5xx-high \
  --metric-name HTTPCode_Target_5XX_Count \
  --threshold 50
```

#### 배포 방법

**Terraform으로 인프라 프로비저닝:**

```hcl
# infrastructure/aws/main.tf
resource "aws_db_instance" "neurohub" {
  identifier           = "neurohub-postgres"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.medium"
  allocated_storage    = 100
  storage_type         = "gp3"
  multi_az             = true
  backup_retention_period = 7

  db_name              = "neurohub"
  username             = "admin"
  password             = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
}

resource "aws_elasticache_cluster" "neurohub" {
  cluster_id           = "neurohub-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1

  subnet_group_name    = aws_elasticache_subnet_group.neurohub.name
  security_group_ids   = [aws_security_group.cache.id]
}

resource "aws_s3_bucket" "firmware" {
  bucket = "neurohub-firmware-prod"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true
    expiration {
      days = 90
    }
  }
}
```

**환경 변수 설정 (.env.aws):**

```bash
DATABASE_URL=postgresql://admin:password@neurohub.abc123.ap-northeast-2.rds.amazonaws.com:5432/neurohub
REDIS_URL=redis://neurohub.abc123.apn2.cache.amazonaws.com:6379/0
USE_S3=true
S3_BUCKET=neurohub-firmware-prod
AWS_REGION=ap-northeast-2
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-aws-production-secret-key
```

#### 비용 산정 (월간)

| 항목 | 비용 (USD) | 비용 (KRW) |
|------|-----------|-----------|
| EC2 t3.medium × 2 | $60 | 78,000원 |
| RDS db.t3.medium (Multi-AZ) | $120 | 156,000원 |
| ElastiCache cache.t3.micro | $15 | 19,500원 |
| ALB | $20 | 26,000원 |
| S3 (10GB) | $3 | 3,900원 |
| 데이터 전송 | $10 | 13,000원 |
| **총합** | **$228** | **약 296,000원** |

> **참고:** 비용은 사용량에 따라 변동될 수 있습니다. 실제 월 운영비는 220-350만원 예상

---

## 4.5 네트워크 구성

| 구분 | IP 주소 | 용도 | 포트 |
|------|---------|------|------|
| WiFi 공유기 | 192.168.1.1 | Gateway | - |
| MES 서버 | 192.168.1.10 | MES 서버 | 80, 443, 5432, 6379 |
| 작업 PC 1-7 | 192.168.1.101-107 | 공정별 | - |
| 관리자 PC | 192.168.1.201-230 | 대시보드 접속 | - |
| 프린터 | 192.168.1.50-57 | 라벨 프린터 | 9100 (TCP) |

**네트워크 대역폭 산정:**

```
동시 접속자: 100명
평균 API 요청 크기: 5KB (Request) + 20KB (Response) = 25KB
요청 빈도: 10초당 1회 (0.1 req/s per user)

총 대역폭 = 100명 × 0.1 req/s × 25KB = 250KB/s = 2Mbps

피크 시간대 (×5 배수): 10Mbps
권장 네트워크: 1Gbps (여유율 100배)
```

---

**이전 섹션:** [4.1 배포 옵션 비교](04-1-deployment-options.md)
**다음 섹션:** [4.3 기술 스택](04-3-tech-stack.md)
