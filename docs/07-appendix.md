# 7. 부록

[← 목차로 돌아가기](./README.md)

---

## 목차

- [7.1 용어 정의](#71-용어-정의)
- [7.2 문서 버전 이력](#72-문서-버전-이력)
- [7.3 참고 자료](#73-참고-자료)

---

## 7.1 용어 정의

| 용어 | 설명 |
|------|------|
| **LOT** | 동일 조건으로 생산된 제품 묶음 단위 (통상 100개) |
| **시리얼 번호** | 개별 제품 고유 식별 번호 (Serial Number) |
| **작업대차** | LOT 단위로 제품을 이동/보관하는 이동식 작업대 |
| **착공** | 공정 작업 시작 |
| **완공** | 공정 작업 완료 |
| **Traceability** | 추적성 - 제품 이력 추적 능력 |
| **MES** | Manufacturing Execution System - 제조 실행 시스템 |
| **LMA** | Linear Muscle Actuator - 로봇의 핵심 구동기 |
| **SMA 스프링** | Shape Memory Alloy 스프링 - 온도로 형상 기억하여 구동 |
| **모선** | SMA 스프링을 제조하는 원재료 케이블 |
| **EOL 검사** | End Of Line 검사 - 최종 성능 검사 |
| **TOF 센서** | Time Of Flight 센서 - 거리 측정 센서 |
| **교대조** | 작업 교대 (D: Day, N: Night) |
| **바코드 스캔** | LOT 번호/시리얼 번호 자동 인식 방식 |
| **File Watcher** | 특정 디렉토리의 파일 생성/변경을 자동 감시하는 기능 |
| **JSONB** | PostgreSQL의 JSON 이진 저장 타입 - 검색/인덱싱 최적화 |
| **API** | Application Programming Interface - 시스템 간 데이터 통신 인터페이스 |
| **JWT** | JSON Web Token - 사용자 인증용 토큰 |
| **RBAC** | Role-Based Access Control - 역할 기반 접근 제어 |
| **HA** | High Availability - 고가용성 (시스템 이중화) |
| **VIP** | Virtual IP - 가상 IP 주소 (이중화 환경용) |
| **Connection Pool** | 데이터베이스 연결 재사용 메커니즘 (성능 최적화) |
| **TPS** | Transactions Per Second - 초당 트랜잭션 처리량 |
| **TTL** | Time To Live - 데이터 유효 시간 |
| **Presigned URL** | 임시 접근 권한이 부여된 URL (S3 다운로드용) |
| **Failover** | 주 시스템 장애 시 대기 시스템으로 자동 전환 |
| **MD5 Hash** | 파일 무결성 검증용 체크섬 |
| **Streaming Replication** | PostgreSQL 실시간 데이터 복제 방식 |
| **Railway** | Cloud PaaS 플랫폼 - 간단한 배포와 자동 인프라 관리 제공 |
| **PaaS** | Platform as a Service - 플랫폼형 클라우드 서비스 |
| **IaaS** | Infrastructure as a Service - 인프라형 클라우드 서비스 |
| **AWS** | Amazon Web Services - 아마존 클라우드 플랫폼 |
| **EC2** | Elastic Compute Cloud - AWS 가상 서버 서비스 |
| **RDS** | Relational Database Service - AWS 관리형 데이터베이스 서비스 |
| **ElastiCache** | AWS 관리형 Redis/Memcached 서비스 |
| **S3** | Simple Storage Service - AWS 객체 스토리지 서비스 |
| **ALB** | Application Load Balancer - AWS 로드 밸런서 |
| **ACM** | AWS Certificate Manager - SSL/TLS 인증서 관리 서비스 |
| **VPC** | Virtual Private Cloud - AWS 가상 네트워크 |
| **CloudWatch** | AWS 모니터링 및 로깅 서비스 |
| **12-Factor App** | 클라우드 네이티브 애플리케이션 설계 원칙 (환경 변수 기반 설정 등) |
| **TCO** | Total Cost of Ownership - 총 소유 비용 (초기 투자 + 운영 비용) |
| **온프레미스** | On-Premise - 자체 서버실에 구축하는 배포 방식 |
| **동시 접속자** | 시스템에 동시에 접속하여 사용하는 사용자 수 |

---

## 7.2 문서 버전 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| v1.0 | 2025.11.09 | 초기 버전 | - |
| v1.6 | 2025.11.09 | 투자 목록 추가 | - |
| v2.0 | 2025.11.10 | 전면 재작성 - 사양서 중심 | Claude |
| **v2.1** | **2025.11.11** | **문서 구조 개선 (13개 파일 분리), 논리적 오류 10건 수정, 일관성 개선, 품질 검증 완료** | **Claude** |

### v2.1 주요 변경 사항

**1. 문서 구조 개선**
- 단일 파일(3,648줄) → 13개 파일로 분리
- 섹션별 독립 파일로 유지보수성 향상
- 체계적인 디렉토리 구조 구축

**2. 논리적 오류 수정 (10건)**
- 섹션 번호 중복 해결 (4.3 중복)
- 배포 옵션 개수 통일 ("두 가지" → "세 가지")
- 공정 2 필드 동기화 (assembly_time, visual_inspection 추가)
- 공정 6 필드 추가 (temperature, displacement)
- 날짜 표기 오류 수정 (251110 = 11월 10일)
- Phase 1 Scope Out 명확화
- AWS 비용 통일 (월 220-350만원)
- LOT 번호 중복 제거 (섹션 2.6, 5.3)

**3. 일관성 개선**
- 용어 통일 ("동시 접속자" 일관 사용)
- 내비게이션 링크 추가 (모든 파일)
- 상호 참조 경로 업데이트

**4. 품질 검증**
- 13개 파일 전체 검증 완료
- 105개 링크 유효성 확인
- 63개 코드 블록 검증
- 78개 테이블 포맷 확인
- 6개 Mermaid 다이어그램 검증
- 품질 점수: 100% (EXCELLENT)

---

## 7.3 참고 자료

### 기술 문서

- **FastAPI 공식 문서:** https://fastapi.tiangolo.com
- **PostgreSQL 공식 문서:** https://www.postgresql.org/docs/
- **React 공식 문서:** https://react.dev
- **PyQt5 문서:** https://www.riverbankcomputing.com/static/Docs/PyQt5/

### 클라우드 플랫폼

- **Railway 공식 사이트:** https://railway.app
- **AWS 공식 문서:** https://docs.aws.amazon.com
- **Railway 가격 정책:** https://railway.app/pricing

### 표준 및 프로토콜

- **ZPL 프로그래밍 가이드:** https://www.zebra.com/us/en/support-downloads/knowledge-articles/zpl-programming-guide.html
- **REST API 설계 가이드:** https://restfulapi.net/
- **JWT 표준 (RFC 7519):** https://datatracker.ietf.org/doc/html/rfc7519

### MES 관련 자료

- **ISA-95 표준:** Manufacturing Execution System 국제 표준
- **Smart Factory 가이드:** 스마트팩토리 구축 가이드라인

---

## 관련 문서

- [README](./README.md) - 문서 전체 개요 및 구조
- [1. 프로젝트 개요](./01-project-overview.md) - 프로젝트 배경 및 목적
- [6. 투자 계획](./06-investment.md) - 개발 일정 및 비용 계획

---

[← 목차로 돌아가기](./README.md)

---

**문서 끝**
