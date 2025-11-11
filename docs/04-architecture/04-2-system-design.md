# 4.2 시스템 구성 및 설계

[← 목차로 돌아가기](../../README.md)

## 4.2 시스템 구성도

본 섹션에서는 배포 옵션별 시스템 아키텍처 구성도를 제공합니다.

### 4.2.1 Option A: 온프레미스 구성도

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

    PC1 -->|WiFi| Nginx
    PC2 --> PC1
    PC3 --> PC1
    Dashboard -->|WiFi/VPN| Nginx
    Nginx --> Backend1
    Nginx --> Backend2
    Backend1 --> DB
    Backend1 --> Redis
    Backend2 --> DB
    Backend2 --> Redis
```

### 4.2.2 Option B-1: Railway 구성도

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

    PC1 -->|HTTPS| Backend
    PC2 --> PC1
    PC3 --> PC1
    Dashboard -->|HTTPS| Backend
    Backend --> DB
    Backend --> Redis
    Backend --> Volume
```

### 4.2.3 Option B-2: AWS 구성도

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

    PC1 -->|HTTPS| ALB
    PC2 --> PC1
    PC3 --> PC1
    Dashboard -->|HTTPS| ALB
    ALB --> Backend1
    ALB --> Backend2
    Backend1 --> RDS
    Backend1 --> ElastiCache
    Backend1 --> S3
    Backend2 --> RDS
    Backend2 --> ElastiCache
    Backend2 --> S3
```

---

## 4.4 배포 아키텍처

**설계 목표:** 동시 접속자 100명 지원, 향후 200명까지 확장 가능

### 4.4.1 Phase 1: 단일 서버 구성 (현재)

**아키텍처:**

```
                    Internet
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

**서버 스펙 권장:**

- CPU: 8 코어 (Intel Xeon 또는 AMD EPYC)
- RAM: 32GB
- SSD: 500GB (NVMe)
- 네트워크: 1Gbps
- OS: Ubuntu 22.04 LTS

**컴포넌트 배치:**

| 컴포넌트 | 포트 | 프로세스 수 | 메모리 |
|---------|------|------------|--------|
| Nginx | 80, 443 | 1 | 512MB |
| FastAPI (Uvicorn) | 8000 | 8 workers | 4GB (총) |
| PostgreSQL | 5432 | 1 | 8GB |
| Redis | 6379 | 1 | 4GB |
| Prometheus | 9090 | 1 | 2GB |
| Grafana | 3000 | 1 | 512MB |

**연결 흐름:**

1. 클라이언트 → Nginx (443) → SSL 종단
2. Nginx → FastAPI (8000) → 8개 worker에 분산
3. FastAPI → PostgreSQL (5432) → Connection Pool (50 connections)
4. FastAPI → Redis (6379) → 캐시 조회/저장

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

## 4.6 AWS 클라우드 마이그레이션 전략

### 4.6.1 코드 수정 최소화 원칙

본 시스템은 온프레미스 환경에서 개발되지만, 향후 AWS로의 마이그레이션을 고려하여 다음 원칙을 따라 설계합니다:

**핵심 설계 패턴:**

1. **12 Factor App 패턴**
   - 모든 환경별 설정을 환경 변수로 관리
   - 하드코딩된 설정 금지 (IP, 포트, 경로 등)
   - 개발/스테이징/프로덕션/AWS 환경 동일 코드 사용

2. **Storage Adapter 패턴**
   - 파일 저장소 추상화 (로컬 vs S3)
   - 인터페이스 기반 설계로 구현체만 교체
   - 펌웨어, 백업 파일 등에 적용

3. **Docker 컨테이너화**
   - 환경 독립적인 배포 패키지
   - 온프레미스와 AWS에서 동일 이미지 사용
   - 환경 변수만 변경하여 배포

**코드 수정 목표:** 0-10 라인 (환경 변수 파일만 수정)

### 4.6.2 환경별 설정 관리

**config.py 구조:**

```python
# backend/app/core/config.py
import os
from typing import Optional

class Settings:
    """환경 변수 기반 설정 관리"""

    # 데이터베이스
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://neurohub:password@localhost:5432/neurohub"
    )

    # Redis 캐시
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # 스토리지 설정
    USE_S3: bool = os.getenv("USE_S3", "false").lower() == "true"
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET", None)
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-2")

    # 로컬 파일 경로 (온프레미스 전용)
    FIRMWARE_DIR: str = os.getenv("FIRMWARE_DIR", "/app/data/firmware")
    BACKUP_DIR: str = os.getenv("BACKUP_DIR", "/app/data/backups")

    # 애플리케이션
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # 보안
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()
```

**환경별 설정 파일:**

온프레미스 환경 (`.env.onprem`):
```bash
DATABASE_URL=postgresql://neurohub:password@192.168.1.10:5432/neurohub
REDIS_URL=redis://192.168.1.10:6379/0
USE_S3=false
FIRMWARE_DIR=/app/data/firmware
BACKUP_DIR=/app/data/backups
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-production-secret-key
```

AWS 환경 (`.env.aws`):
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

### 4.6.3 Storage Adapter 구현

**스토리지 추상화 인터페이스:**

```python
# backend/app/services/storage.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

class StorageAdapter(ABC):
    """파일 저장소 추상 인터페이스"""

    @abstractmethod
    def upload(self, file_path: str, key: str) -> str:
        """파일 업로드"""
        pass

    @abstractmethod
    def download(self, key: str, file_path: str) -> None:
        """파일 다운로드"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """파일 존재 여부 확인"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """파일 삭제"""
        pass

    @abstractmethod
    def get_url(self, key: str) -> str:
        """파일 URL 반환"""
        pass


class LocalStorage(StorageAdapter):
    """로컬 파일 시스템 저장소 (온프레미스)"""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file_path: str, key: str) -> str:
        import shutil
        dest = self.base_dir / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, dest)
        return str(dest)

    def download(self, key: str, file_path: str) -> None:
        import shutil
        src = self.base_dir / key
        shutil.copy(src, file_path)

    def exists(self, key: str) -> bool:
        return (self.base_dir / key).exists()

    def delete(self, key: str) -> None:
        (self.base_dir / key).unlink(missing_ok=True)

    def get_url(self, key: str) -> str:
        return f"/api/v1/files/{key}"


class S3Storage(StorageAdapter):
    """AWS S3 저장소 (클라우드)"""

    def __init__(self, bucket: str, region: str):
        import boto3
        self.bucket = bucket
        self.region = region
        self.s3 = boto3.client('s3', region_name=region)

    def upload(self, file_path: str, key: str) -> str:
        self.s3.upload_file(file_path, self.bucket, key)
        return f"s3://{self.bucket}/{key}"

    def download(self, key: str, file_path: str) -> None:
        self.s3.download_file(self.bucket, key, file_path)

    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False

    def delete(self, key: str) -> None:
        self.s3.delete_object(Bucket=self.bucket, Key=key)

    def get_url(self, key: str) -> str:
        # Presigned URL (7일 유효)
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=604800  # 7 days
        )


# Factory: 환경에 따라 자동 선택
def get_storage() -> StorageAdapter:
    """환경별 스토리지 어댑터 생성"""
    from app.core.config import settings

    if settings.USE_S3:
        return S3Storage(settings.S3_BUCKET, settings.AWS_REGION)
    else:
        return LocalStorage(settings.FIRMWARE_DIR)
```

**사용 예시 (펌웨어 관리):**

```python
# backend/app/api/v1/endpoints/firmware.py
from app.services.storage import get_storage

@router.post("/upload")
async def upload_firmware(file: UploadFile):
    storage = get_storage()  # 환경에 따라 자동 선택

    # 임시 파일로 저장
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # 스토리지에 업로드 (로컬 or S3)
    key = f"firmware/{file.filename}"
    storage.upload(temp_path, key)

    return {"message": "Uploaded", "key": key}

@router.get("/download/{version}")
async def download_firmware(version: str):
    storage = get_storage()

    # 다운로드 URL 생성 (로컬: /api/v1/files/xxx, S3: presigned URL)
    key = f"firmware/firmware_{version}.bin"
    url = storage.get_url(key)

    return {"download_url": url}
```

### 4.6.4 AWS 마이그레이션 옵션

**Option 1: Lift & Shift (EC2 기반)**

| 항목 | 내용 |
|------|------|
| **난이도** | ⭐⭐ (쉬움) |
| **마이그레이션 시간** | 1-2일 |
| **코드 수정** | 0-10 라인 (환경 변수만) |
| **예상 비용** | 월 220-350만원 |
| **장점** | 빠른 마이그레이션, 최소 변경 |
| **단점** | 운영 부담 높음, HA 수동 구성 |

**AWS 구성:**
- EC2 t3.large (2개: primary + standby)
- PostgreSQL: EC2에 설치
- Redis: EC2에 설치
- 로드밸런서: Nginx (EC2 내부)
- 파일 스토리지: EBS 볼륨

**배포 방법:**
```bash
# 1. Docker Compose로 배포
docker-compose -f docker-compose.aws.yml up -d

# 2. 환경 변수만 변경
export DATABASE_URL=postgresql://...
export REDIS_URL=redis://...
export USE_S3=false
```


**Option 2: Managed Services (권장)**

| 항목 | 내용 |
|------|------|
| **난이도** | ⭐⭐⭐ (보통) |
| **마이그레이션 시간** | 3-4주 |
| **코드 수정** | 0 라인 (환경 변수만) |
| **예상 비용** | 월 220-350만원 |
| **장점** | 자동 백업, 자동 HA, 모니터링 통합 |
| **단점** | 초기 설정 복잡, 비용 높음 |

**AWS 서비스 매핑:**

| 온프레미스 | AWS 서비스 | 설정 |
|-----------|-----------|------|
| PostgreSQL 15 | RDS PostgreSQL 15 | db.t3.large (Multi-AZ) |
| Redis 7.x | ElastiCache Redis | cache.t3.medium (Cluster 모드) |
| Nginx | Application Load Balancer (ALB) | HTTP/HTTPS 리스너 |
| 파일 저장소 | S3 | Standard Storage Class |
| 백업 | S3 + RDS Snapshot | 자동 백업 (7일 보관) |
| 모니터링 | CloudWatch | RDS/EC2 통합 메트릭 |
| 로그 | CloudWatch Logs | 중앙 집중식 로그 |

**인프라 구성 (Terraform):**

```hcl
# infrastructure/aws/main.tf
resource "aws_db_instance" "neurohub" {
  identifier           = "neurohub-postgres"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.large"
  allocated_storage    = 100
  storage_type         = "gp3"

  multi_az             = true  # 고가용성
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
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"

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
      days = 90  # 90일 후 자동 삭제
    }
  }
}
```

### 4.6.5 단계별 마이그레이션 절차

**Phase 1: 준비 단계 (1주)**

1. **AWS 계정 설정**
   - AWS 계정 생성
   - IAM 사용자 및 역할 설정
   - VPC 및 서브넷 구성 (Private/Public)

2. **코드 검증**
   - 환경 변수 기반 설정 확인
   - Storage Adapter 테스트
   - Docker 이미지 빌드 및 테스트

3. **데이터 마이그레이션 계획**
   - PostgreSQL 덤프 생성
   - 데이터 크기 산정
   - 마이그레이션 다운타임 계획

**Phase 2: 인프라 구축 (1-2주)**

1. **AWS 리소스 프로비저닝**
   ```bash
   cd infrastructure/aws
   terraform init
   terraform plan
   terraform apply
   ```

2. **데이터베이스 마이그레이션**
   ```bash
   # 온프레미스에서 덤프 생성
   pg_dump -h 192.168.1.10 -U neurohub neurohub > neurohub_backup.sql

   # AWS RDS로 복원
   psql -h neurohub.abc123.ap-northeast-2.rds.amazonaws.com \
        -U admin -d neurohub < neurohub_backup.sql
   ```

3. **파일 마이그레이션 (펌웨어)**
   ```bash
   # AWS CLI로 S3 동기화
   aws s3 sync /app/data/firmware/ s3://neurohub-firmware-prod/firmware/
   ```

**Phase 3: 배포 및 전환 (3-5일)**

1. **애플리케이션 배포**
   ```bash
   # Docker 이미지 ECR에 푸시
   docker tag neurohub-backend:latest 123456789.dkr.ecr.ap-northeast-2.amazonaws.com/neurohub-backend:latest
   docker push 123456789.dkr.ecr.ap-northeast-2.amazonaws.com/neurohub-backend:latest

   # EC2에서 실행
   docker-compose -f docker-compose.aws.yml up -d
   ```

2. **환경 변수 설정**
   ```bash
   # .env.aws 파일 생성
   DATABASE_URL=postgresql://admin:password@neurohub.abc123.ap-northeast-2.rds.amazonaws.com:5432/neurohub
   REDIS_URL=redis://neurohub.abc123.apn2.cache.amazonaws.com:6379/0
   USE_S3=true
   S3_BUCKET=neurohub-firmware-prod
   AWS_REGION=ap-northeast-2
   ```

3. **DNS 전환**
   - Route 53에 도메인 등록
   - ALB DNS를 A 레코드로 연결
   - 점진적 트래픽 전환 (0% → 10% → 50% → 100%)

**Phase 4: 검증 및 최적화 (1주)**

1. **성능 테스트**
   - API 응답 시간 측정
   - 데이터베이스 쿼리 최적화
   - 캐시 히트율 확인

2. **모니터링 설정**
   - CloudWatch 대시보드 구성
   - 알람 설정 (CPU, 메모리, 디스크, API 에러율)
   - 로그 확인 및 분석

3. **백업 검증**
   - RDS 자동 스냅샷 확인
   - S3 버킷 버전 관리 테스트
   - 복원 절차 문서화

### 4.6.6 비용 산정

**온프레미스 vs AWS 비용 비교 (월간):**

| 구분 | 온프레미스 | AWS (Managed) |
|------|-----------|--------------|
| **서버/인프라** | ~월 113만원 | 월 220-350만원 |

**3년 총 소유 비용 (TCO) 비교:**

온프레미스는 초기 투자 6,790만원 + 36개월 운영비 4,068만원 = 10,858만원
AWS는 초기 투자 1,805만원 + 36개월 운영비 7,920-12,600만원 = 9,725-14,405만원

### 4.6.7 롤백 계획

AWS 마이그레이션 실패 시 온프레미스로 복귀하는 절차:

1. **DNS 복원** (5분)
   - Route 53에서 온프레미스 IP로 A 레코드 변경
   - TTL이 짧으므로 5분 내 전환

2. **데이터 동기화** (1-2시간)
   ```bash
   # AWS RDS에서 최신 데이터 덤프
   pg_dump -h neurohub.abc123.ap-northeast-2.rds.amazonaws.com \
           -U admin neurohub > latest_backup.sql

   # 온프레미스 DB 복원
   psql -h 192.168.1.10 -U neurohub neurohub < latest_backup.sql
   ```

3. **환경 변수 복원**
   ```bash
   # .env.onprem 파일 재적용
   docker-compose -f docker-compose.onprem.yml up -d
   ```

4. **검증**
   - API 헬스체크 확인
   - 주요 기능 테스트 (LOT 생성, 공정 완공 등)

**최대 다운타임:** 2-3시간 (데이터 동기화 시간 포함)

---

**이전 섹션:** [4.1 배포 옵션 비교](04-1-deployment-options.md)
**다음 섹션:** [4.3 기술 스택](04-3-tech-stack.md)
