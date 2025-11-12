# F2X NeuroHub MES System

**F2X Wearable Robot 생산라인 MES(Manufacturing Execution System) 시스템 개발 사양서 및 구현 가이드**

## 📋 프로젝트 개요

F2X NeuroHub MES는 F2X Wearable Robot 생산라인을 위한 제조 실행 시스템입니다. LOT 기반 생산 추적, 7개 공정 통합 관리, 실시간 모니터링 대시보드를 제공하여 생산 효율성과 품질 관리를 향상시킵니다.

### 주요 특징

- ✅ **LOT 기반 생산 추적**: 전 공정에 걸친 시리얼 번호 추적
- ✅ **7개 공정 통합 관리**: 스프링 투입 → LMA 조립 → 레이저 마킹 → EOL 검사 → 로봇 성능검사 → 프린팅 → 포장
- ✅ **실시간 모니터링**: React 기반 대시보드
- ✅ **오프라인 모드 지원**: 네트워크 단절 시 로컬 큐 활용
- ✅ **외부 공정 앱 통합**: JSON 파일 기반 통신으로 7개 외부 업체 앱 연동

## 📚 문서 구성

### 1. [개선안 v2.0](./F2X_NeuroHub_MES_개선안_v2.0.md)
시스템 개발 사양서 (개선안)
- **생산 워크플로우**: LOT 생성 → 시리얼 발행 → 바코드 라벨 출력 → 착공 → 완공 전체 프로세스
- 시스템 아키텍처 (Mermaid 다이어그램)
- JSON 파일 통신 규격
- LOT/시리얼 번호 체계
- 데이터베이스 설계
- API 명세
- 보안 및 인증 (JWT + RBAC)
- 백업 및 재해복구 계획

### 2. [검토보고서](./F2X_NeuroHub_MES_검토보고서.md)
v1.6 사양서 검토 및 개선점 분석
- Critical/High/Medium/Low 우선순위별 이슈 분류
- 각 이슈별 상세 분석 및 해결 방안
- 추가 투자 비용 산정

### 3. [구현가이드](./F2X_NeuroHub_MES_구현가이드.md)
개발자를 위한 상세 구현 가이드
- Backend 구현 (FastAPI + PostgreSQL)
- Frontend 구현 (PyQt5 작업 PC 앱)
- JSON 파일 모니터링 서비스 (watchdog)
- 외부 공정 앱 개발 가이드
- React Dashboard 구현

## 🏗️ 시스템 아키텍처

```
생산 현장 (작업 PC)
  ↓ WiFi / REST API
로컬 서버 (On-Premise)
  - Primary Server: FastAPI + PostgreSQL + Redis
  - Standby Server: PostgreSQL (Hot Standby) - Phase 2
  ↓ HTTPS / WebSocket
관리자 모니터링 (React Dashboard)
```

## 🛠️ 기술 스택

### Backend
- **언어**: Python 3.11+
- **프레임워크**: FastAPI 0.109+
- **데이터베이스**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **인증**: JWT (python-jose)
- **캐시**: Redis 7+

### Frontend - 작업 PC
- **언어**: Python 3.11+
- **GUI**: PyQt5 5.15+
- **파일 모니터링**: watchdog
- **로컬 DB**: SQLite 3 (오프라인 큐)

### Frontend - Dashboard
- **언어**: TypeScript 5+
- **프레임워크**: React 18+
- **UI**: Ant Design 5+
- **차트**: Recharts 2+

## 🚀 핵심 개선 사항 (v1.6 → v2.0)

| 구분 | v1.6 (기존) | v2.0 (개선안) |
|------|-------------|---------------|
| **개발 기간** | 1개월 | 2-3개월 (현실적) |
| **통신 방식** | JSON 파일 (단일 폴더) | 폴더 구조화 + watchdog 모니터링 |
| **LOT 번호** | FN-YYMMDD-Axxx | FN-KR01-YYYYMMDD-D-000001 (확장성) |
| **DB 구조** | 공정별 분리 (9개 테이블) | 통합 테이블 + JSONB |
| **인증/인가** | 없음 | JWT + RBAC |
| **에러 처리** | 없음 | 에러 프레임워크 + 로깅 |
| **백업** | 없음 | 자동 백업 (6시간) |
| **장애 대응** | SPOF 존재 | 서버 이중화 (Phase 2) |

## 📦 JSON 파일 통신 구조

외부 공정 앱(7개, 각 업체별 개발)과의 통신은 JSON 파일 기반으로 이루어집니다.

```
C:\F2X\
├── input\
│   ├── start\       # 공정 앱이 착공 JSON 생성
│   └── complete\    # 공정 앱이 완공 JSON 생성
├── processed\       # 처리 완료 (30일 보관)
├── error\           # 에러 발생 (수동 처리)
└── queue\           # 오프라인 큐 (SQLite)
```

**제약사항**:
- ⚠️ 공정 앱은 외부 업체 개발 (소스코드 접근 불가)
- ⚠️ JSON 파일 방식이 유일한 통신 수단
- ✅ Frontend App이 watchdog로 실시간 모니터링

## 💰 투자 계획

**Phase 1 (MVP)**: 4,080만원 (2개월)
- Backend 개발: 1,200만원
- Frontend 개발: 1,400만원
- 인프라 구축: 800만원
- 테스트 및 배포: 680만원

**Phase 2 (안정화)**: 1,000만원 (1개월)
- 서버 이중화 (HA): 600만원
- 고급 리포트: 200만원
- 성능 최적화: 200만원

**총 투자 금액**: 5,080만원

## 📄 라이선스

이 문서는 F2X NeuroHub MES 시스템 개발을 위한 내부 사양서입니다.

---

**작성일**: 2025.11.10
**버전**: 2.0 (개선안)
**기반 버전**: v1.6 검토 후 개선
