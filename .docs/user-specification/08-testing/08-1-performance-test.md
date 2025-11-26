# 8.1 성능 테스트 계획

[← 목차로 돌아가기](../README.md)

---

## 목차

- [8.1.1 성능 테스트 개요](#811-성능-테스트-개요)
- [8.1.2 테스트 환경](#812-테스트-환경)
- [8.1.3 성능 목표 및 기준](#813-성능-목표-및-기준)
- [8.1.4 테스트 시나리오](#814-테스트-시나리오)
- [8.1.5 부하 테스트 계획](#815-부하-테스트-계획)
- [8.1.6 스트레스 테스트 계획](#816-스트레스-테스트-계획)
- [8.1.7 내구성 테스트 계획](#817-내구성-테스트-계획)
- [8.1.8 테스트 도구 및 측정 항목](#818-테스트-도구-및-측정-항목)
- [8.1.9 성능 모니터링 및 분석](#819-성능-모니터링-및-분석)

---

## 8.1.1 성능 테스트 개요

### 목적

MES 시스템의 성능 요구사항(NFR-PERF-001 ~ NFR-PERF-009)을 검증하고, 프로덕션 환경에서 안정적으로 운영 가능한지 확인합니다.

### 테스트 유형

| 테스트 유형 | 목적 | 실행 시점 |
|-----------|------|----------|
| **부하 테스트 (Load Test)** | 정상 부하에서 성능 검증 | 매 릴리스 전 |
| **스트레스 테스트 (Stress Test)** | 최대 부하 및 한계점 파악 | 주요 릴리스 전 |
| **내구성 테스트 (Endurance Test)** | 장시간 운영 시 안정성 검증 | 주요 릴리스 전 |
| **스파이크 테스트 (Spike Test)** | 급격한 부하 변화 대응 확인 | 선택적 |

---

## 8.1.2 테스트 환경

### 하드웨어 사양 (온프레미스 기준)

**애플리케이션 서버:**
- CPU: Intel Xeon 8코어 3.0GHz
- RAM: 32GB DDR4
- Disk: SSD 500GB
- Network: 1Gbps

**데이터베이스 서버:**
- CPU: Intel Xeon 8코어 3.0GHz
- RAM: 64GB DDR4
- Disk: SSD 1TB (RAID 10)
- Network: 1Gbps

### 소프트웨어 구성

| 구성 요소 | 버전 | 설정 |
|----------|------|------|
| **FastAPI** | 0.104+ | Workers: 8 (CPU 코어 × 1) |
| **PostgreSQL** | 15+ | max_connections: 100, shared_buffers: 8GB |
| **Redis** | 7+ | maxmemory: 4GB, maxmemory-policy: allkeys-lru |
| **Nginx** | 1.24+ | worker_processes: 8, worker_connections: 4096 |

### 네트워크 토폴로지

```
[부하 생성기] → [Nginx (Reverse Proxy)] → [FastAPI (8 Workers)] → [PostgreSQL]
                                                 ↓
                                              [Redis Cache]
```

---

## 8.1.3 성능 목표 및 기준

### API 응답 시간 (NFR-PERF-001 ~ 004)

| API 엔드포인트 | P50 | P95 | P99 | 최대값 |
|---------------|-----|-----|-----|--------|
| `POST /api/v1/process/start` | < 300ms | < 1s | < 2s | < 3s |
| `POST /api/v1/process/complete` | < 500ms | < 2s | < 3s | < 5s |
| `GET /api/v1/lots/{lot_number}` | < 500ms | < 2s | < 3s | < 5s |
| `GET /api/v1/dashboard/summary` | < 1s | < 3s | < 5s | < 8s |

### 처리량 (NFR-PERF-005 ~ 007)

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **동시 사용자** | 100명 (피크 200명) | 부하 테스트 |
| **일일 트랜잭션** | 50,000건 | 내구성 테스트 |
| **TPS (초당 트랜잭션)** | 최소 20 TPS | 부하 테스트 |

### 데이터베이스 성능 (NFR-PERF-008 ~ 009)

| 항목 | 목표 | 검증 방법 |
|------|------|----------|
| **쿼리 응답 시간** | < 500ms (복잡한 집계 쿼리) | SQL Profiling |
| **Connection Pool** | 50 동시 연결 지원 | 부하 테스트 |

---

## 8.1.4 테스트 시나리오

### 시나리오 1: 정상 운영 시뮬레이션

**목표:** 일반적인 작업 시간대의 부하 패턴 재현

**사용자 행동:**
1. 작업자 70명 (착공/완공 처리)
2. 관리자 30명 (대시보드 조회, LOT 생성)

**트랜잭션 분포:**
- 착공 API: 40%
- 완공 API: 30%
- 조회 API: 25%
- LOT 생성: 5%

**실행 시간:** 1시간

**성공 기준:**
- 평균 응답 시간 < 1초
- 에러율 < 0.1%
- CPU 사용률 < 80%
- 메모리 사용률 < 85%

### 시나리오 2: 피크 시간대 시뮬레이션

**목표:** 교대 시작 시간의 급격한 부하 증가 재현

**사용자 행동:**
1. 5분 동안 동시 사용자 50명 → 200명 증가
2. 30분 동안 200명 유지
3. 10분 동안 200명 → 100명 감소

**트랜잭션 분포:**
- 착공 API: 60% (교대 시작 시 착공 집중)
- 완공 API: 20%
- 조회 API: 20%

**실행 시간:** 45분

**성공 기준:**
- P95 응답 시간 < 2초
- 에러율 < 0.5%
- CPU 사용률 < 90%

### 시나리오 3: 대시보드 집중 조회

**목표:** 관리자들의 동시 대시보드 접속 처리

**사용자 행동:**
1. 50명의 관리자가 동시에 대시보드 접속
2. 10초마다 폴링 요청 (금일 현황 조회)
3. LOT 상세 조회 (분당 10회)

**실행 시간:** 30분

**성공 기준:**
- 대시보드 초기 로딩 < 3초
- 폴링 API 응답 시간 < 1초
- 캐시 히트율 > 80%

### 시나리오 4: File Watcher 대량 처리

**목표:** 완공 데이터 대량 유입 시 처리 능력 검증

**데이터 유입:**
1. 1분당 100개의 JSON 파일 생성
2. 총 1,000개 파일 처리
3. 파일 크기: 평균 5KB

**실행 시간:** 10분

**성공 기준:**
- 파일 감지 시간 < 5초
- 파일 처리 성공률 > 99%
- 처리된 파일이 completed/ 폴더로 정상 이동

---

## 8.1.5 부하 테스트 계획

### 테스트 구성

**도구:** Locust (Python 기반 부하 테스트 도구)

**부하 생성 스크립트 예시:**

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random

class MESUser(HttpUser):
    wait_time = between(1, 5)  # 사용자 간 대기 시간 1~5초

    def on_start(self):
        """테스트 시작 시 로그인"""
        response = self.client.post("/api/v1/auth/login", json={
            "user_id": f"worker{random.randint(1, 100):03d}",
            "password": "test1234"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(4)
    def start_process(self):
        """착공 API (40% 비중)"""
        lot_number = f"WF-KR-251115D-{random.randint(1, 10):03d}"
        self.client.post(
            "/api/v1/process/start",
            headers=self.headers,
            json={
                "lot_number": lot_number,
                "line_id": "KR-001",
                "process_id": f"PROC-{random.randint(1, 8):03d}",
                "worker_id": "W001"
            },
            name="착공 API"
        )

    @task(3)
    def complete_process(self):
        """완공 조회 (30% 비중)"""
        lot_number = f"WF-KR-251115D-{random.randint(1, 10):03d}"
        self.client.get(
            f"/api/v1/lots/{lot_number}",
            headers=self.headers,
            name="LOT 조회 API"
        )

    @task(2)
    def dashboard_summary(self):
        """대시보드 요약 (25% 비중)"""
        self.client.get(
            "/api/v1/dashboard/summary",
            headers=self.headers,
            name="대시보드 요약 API"
        )

    @task(1)
    def create_lot(self):
        """LOT 생성 (5% 비중)"""
        self.client.post(
            "/api/v1/lots",
            headers=self.headers,
            json={
                "product_model_id": 1,
                "target_quantity": 100,
                "shift": "D"
            },
            name="LOT 생성 API"
        )
```

### 실행 명령어

```bash
# 100명 사용자, 초당 10명씩 증가, 60분 실행
locust -f tests/performance/locustfile.py \
       --headless \
       --users 100 \
       --spawn-rate 10 \
       --run-time 60m \
       --host http://localhost:8000
```

### 측정 항목

- **응답 시간:** P50, P95, P99, 최대값
- **처리량:** RPS (Requests Per Second), TPS (Transactions Per Second)
- **에러율:** 4xx, 5xx 응답 비율
- **시스템 리소스:** CPU, 메모리, 디스크 I/O, 네트워크

---

## 8.1.6 스트레스 테스트 계획

### 목표

시스템의 한계점을 파악하고, 장애 시 복구 능력을 검증합니다.

### 테스트 시나리오

**단계 1: 점진적 부하 증가**
- 시작: 50명 사용자
- 증가: 10분마다 50명씩 증가
- 종료: 시스템 응답 시간이 5초를 초과하거나 에러율이 5%를 초과할 때

**단계 2: 한계점 유지**
- 한계점의 80% 부하로 30분 유지
- 안정성 확인

**단계 3: 부하 감소**
- 10분 동안 점진적으로 정상 부하(100명)로 감소
- 복구 능력 확인

### 성공 기준

- 한계점: 최소 200명 동시 사용자 지원
- 복구 시간: 부하 감소 후 5분 이내 정상 응답 시간 회복
- 데이터 무결성: 스트레스 테스트 후 데이터 손실 없음

---

## 8.1.7 내구성 테스트 계획

### 목표

장시간 운영 시 메모리 누수, 리소스 고갈 등의 문제가 없는지 확인합니다.

### 테스트 시나리오

**실행 시간:** 24시간

**부하:**
- 동시 사용자: 100명 (일정)
- 트랜잭션: 일일 50,000건 (시뮬레이션)

**모니터링 항목:**
- 메모리 사용량 추이 (메모리 누수 감지)
- CPU 사용률 추이
- Database Connection Pool 상태
- 로그 파일 크기 증가율

### 성공 기준

- 메모리 사용량 증가율 < 1% per hour
- CPU 사용률 안정적 (평균 ±10% 이내)
- 에러율 < 0.1%
- Database Connection 누수 없음

---

## 8.1.8 테스트 도구 및 측정 항목

### 부하 생성 도구

| 도구 | 용도 | 장점 |
|------|------|------|
| **Locust** | API 부하 테스트 | Python 기반, 확장 용이, 실시간 모니터링 |
| **Apache JMeter** | 종합 성능 테스트 | GUI 제공, 플러그인 풍부 |
| **k6** | 대규모 부하 테스트 | Go 기반, 고성능, Grafana 연동 |

**권장:** Locust (개발 언어와 동일한 Python 사용)

### 모니터링 도구

**시스템 메트릭:**
```bash
# Prometheus + Grafana
# docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**애플리케이션 메트릭:**
```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 요청 카운터
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 응답 시간 히스토그램
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# 활성 연결 게이지
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)
```

### 측정 항목

**응답 시간 메트릭:**
- P50 (중앙값): 50%의 요청이 이 시간 이내 완료
- P95: 95%의 요청이 이 시간 이내 완료
- P99: 99%의 요청이 이 시간 이내 완료
- Max: 최대 응답 시간

**처리량 메트릭:**
- RPS (Requests Per Second): 초당 요청 수
- TPS (Transactions Per Second): 초당 트랜잭션 수

**에러 메트릭:**
- Error Rate: 전체 요청 대비 에러 비율
- 4xx Rate: 클라이언트 에러 비율
- 5xx Rate: 서버 에러 비율

**시스템 메트릭:**
- CPU Utilization: CPU 사용률 (%)
- Memory Usage: 메모리 사용량 (MB)
- Disk I/O: 디스크 읽기/쓰기 (MB/s)
- Network I/O: 네트워크 송수신 (MB/s)

---

## 8.1.9 성능 모니터링 및 분석

### 실시간 모니터링 대시보드

**Grafana 대시보드 구성:**

**패널 1: API 응답 시간**
```promql
# P95 응답 시간
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

**패널 2: 요청 처리량**
```promql
# 초당 요청 수
rate(http_requests_total[1m])
```

**패널 3: 에러율**
```promql
# 에러율 (%)
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100
```

**패널 4: Database Connection Pool**
```promql
# 활성 연결 수
db_connections_active
```

### 성능 분석 체크리스트

**응답 시간 분석:**
- [ ] P95 응답 시간이 목표 이내인가?
- [ ] 응답 시간의 분산이 큰가? (P99 - P50 > 2초)
- [ ] 특정 엔드포인트에서 병목이 발생하는가?

**처리량 분석:**
- [ ] 목표 TPS를 달성했는가?
- [ ] 사용자 증가에 따라 TPS가 선형적으로 증가하는가?

**에러 분석:**
- [ ] 에러율이 목표 이내인가?
- [ ] 특정 유형의 에러가 반복되는가?
- [ ] 에러 로그에서 패턴을 발견했는가?

**시스템 리소스 분석:**
- [ ] CPU 병목이 있는가? (> 90%)
- [ ] 메모리 누수가 있는가? (지속적 증가)
- [ ] Disk I/O 병목이 있는가?
- [ ] Database Connection Pool이 고갈되는가?

### 성능 개선 우선순위

**High Priority (즉시 개선):**
- P95 응답 시간 > 목표치의 150%
- 에러율 > 1%
- CPU 사용률 > 90%
- 메모리 누수 발견

**Medium Priority (다음 릴리스 전):**
- P95 응답 시간 > 목표치의 120%
- 에러율 > 0.5%
- 특정 엔드포인트 병목

**Low Priority (점진적 개선):**
- P50 응답 시간 최적화
- 캐시 히트율 향상
- 코드 리팩토링

### 성능 테스트 보고서 템플릿

```markdown
# 성능 테스트 보고서

**테스트 날짜:** YYYY-MM-DD
**테스트 버전:** v1.0.0
**테스트 환경:** 온프레미스 / Railway / AWS

## 1. 테스트 요약
- 테스트 유형: 부하 테스트
- 실행 시간: 60분
- 동시 사용자: 100명
- 총 요청 수: 120,000건

## 2. 성능 메트릭

| 항목 | 목표 | 실제 결과 | 상태 |
|------|------|----------|------|
| P95 응답 시간 | < 1s | 850ms | ✅ Pass |
| TPS | > 20 | 25.5 | ✅ Pass |
| 에러율 | < 0.1% | 0.05% | ✅ Pass |
| CPU 사용률 | < 80% | 72% | ✅ Pass |

## 3. 발견된 이슈
- 이슈 없음

## 4. 권장 사항
- Redis 캐시 TTL 조정 (60초 → 120초)
- Database Connection Pool 크기 증가 (20 → 30)

## 5. 첨부 자료
- Grafana 대시보드 스크린샷
- Locust 테스트 리포트 (HTML)
```

---

## 관련 문서

- [3.3 비기능 요구사항](../03-requirements/03-1-functional.md#33-비기능-요구사항) - 성능 요구사항
- [4.3 기술 스택](../04-architecture/04-3-tech-stack.md) - 성능 최적화 설정
- [8.2 통합 테스트 가이드](08-2-integration-test.md) - 통합 테스트 전략

---

> **이전 섹션:** [7. 부록](../07-appendix.md)
> **다음 섹션:** [8.2 통합 테스트 가이드](08-2-integration-test.md)

---

[← 목차로 돌아가기](../README.md)
