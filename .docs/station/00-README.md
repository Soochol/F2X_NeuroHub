# Station System Design Documentation

Station Service와 Station UI에 대한 상세 설계 문서입니다.

---

## 개발 진행 현황

> 마지막 업데이트: 2025-12-30

| Phase | 상태 | 진행률 |
|-------|------|--------|
| Phase 1: 기반 구조 | ✅ 완료 | 100% |
| Phase 2: 시퀀스 패키지 | ✅ 완료 | 100% |
| Phase 3: Station Service | ✅ 완료 | 100% |
| Phase 4: Backend 통합 | ✅ 완료 | 100% |
| Phase 5: Station UI | ✅ 완료 | 100% |

**범례**: ⬜ 대기 | 🔄 진행중 | ✅ 완료

---

## 개발 순서 (Implementation Order)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         실제 개발 순서                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Phase 1: 기반 구조 ─────────────────────────────────────────────────────── │
│   │                                                                          │
│   ├─ 1.1 아키텍처 이해 (01) ─────── 전체 구조 파악 (읽기 전용)                │
│   ├─ 1.2 데이터 모델 구현 (02) ──── Python Pydantic 모델                      │
│   └─ 1.3 API 스키마 정의 (03) ───── FastAPI 라우터 스켈레톤                   │
│                                                                              │
│   Phase 2: 시퀀스 패키지 ─────────────────────────────────────────────────── │
│   │                                                                          │
│   ├─ 2.1 패키지 구조 생성 (04) ──── 디렉토리/파일 구조                        │
│   ├─ 2.2 SequenceLoader 구현 (05) ─ 패키지 로딩/검증                          │
│   ├─ 2.3 SequenceExecutor 구현 ──── 시퀀스 실행 엔진                          │
│   └─ 2.4 Driver 인터페이스 정의 ─── 하드웨어 추상화 레이어                    │
│                                                                              │
│   Phase 3: Station Service ───────────────────────────────────────────────── │
│   │                                                                          │
│   ├─ 3.1 프로젝트 구조 생성 (06) ── station_service/ 디렉토리                 │
│   ├─ 3.2 BatchManager 구현 (07) ─── 프로세스 생성/관리                        │
│   ├─ 3.3 IPC 통신 구현 ──────────── ZeroMQ REQ/REP, PUB/SUB                   │
│   ├─ 3.4 FastAPI 서버 구현 ──────── REST API + WebSocket                      │
│   └─ 3.5 LocalDB 구현 ───────────── SQLite 저장소                             │
│                                                                              │
│   Phase 4: Backend 통합 ──────────────────────────────────────────────────── │
│   │                                                                          │
│   ├─ 4.1 BackendClient 구현 (10) ── HTTP 클라이언트                           │
│   ├─ 4.2 착공 API 연동 ──────────── start-process 호출                        │
│   ├─ 4.3 완공 API 연동 ──────────── complete-process 호출                     │
│   ├─ 4.4 시리얼 변환 연동 ───────── convert-to-serial 호출                    │
│   └─ 4.5 SyncEngine 구현 ────────── 오프라인 큐 처리                          │
│                                                                              │
│   Phase 5: Station UI ────────────────────────────────────────────────────── │
│   │                                                                          │
│   ├─ 5.1 프로젝트 설정 (08) ─────── React + Vite + TypeScript                 │
│   ├─ 5.2 API 클라이언트 (09) ────── REST + WebSocket 훅                       │
│   ├─ 5.3 대시보드 페이지 ────────── Batch 모니터링 UI                         │
│   ├─ 5.4 Batch 제어 UI ──────────── 시작/정지/상태 표시                       │
│   └─ 5.5 실시간 업데이트 ────────── WebSocket 이벤트 처리                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 문서 구조

| # | 문서 | 설명 | Phase |
|---|------|------|-------|
| 01 | [architecture-overview](./01-architecture-overview.md) | 전체 아키텍처 개요 | 1 |
| 02 | [data-models](./02-data-models.md) | 데이터 모델 정의 | 1 |
| 03 | [api-specification](./03-api-specification.md) | API 인터페이스 명세 | 1 |
| 04 | [sequence-package-spec](./04-sequence-package-spec.md) | 시퀀스 패키지 요구사항 | 2 |
| 05 | [sequence-package-design](./05-sequence-package-design.md) | 시퀀스 패키지 상세 설계 | 2 |
| 06 | [station-service-spec](./06-station-service-spec.md) | Station Service 요구사항 | 3 |
| 07 | [station-service-design](./07-station-service-design.md) | Station Service 상세 설계 | 3 |
| 08 | [station-ui-spec](./08-station-ui-spec.md) | Station UI 요구사항 | 5 |
| 09 | [station-ui-design](./09-station-ui-design.md) | Station UI 상세 설계 | 5 |
| 10 | [batch-lifecycle-backend-integration](./10-batch-lifecycle-backend-integration.md) | 착공/완공 Backend 통합 | 4 |

## 시스템 개요

Station System은 공정(Station)에 설치되어 하드웨어를 제어하고 테스트 시퀀스를 실행하는 시스템입니다.

### 핵심 구성요소

1. **Station Service**: 시퀀스 실행/관리, Batch 프로세스 관리, Backend 통신
2. **Station UI**: 웹 기반 모니터링 및 제어 인터페이스
3. **Sequence Package**: 드라이버 + 시퀀스가 통합된 배포 단위

### 설계 원칙

- **Thin Station Service**: 실행/관리만 담당, 드라이버 로직 없음
- **Self-contained Package**: 시퀀스와 드라이버가 하나의 패키지로 통합
- **Offline-first**: Backend 연결 없이도 동작 가능
- **Independent Batch**: 각 Batch는 독립 프로세스로 실행

## 기술 스택

| 구성요소 | 기술 |
|----------|------|
| Station Service | Python 3.11+, FastAPI, asyncio, ZeroMQ |
| Station UI | React, TypeScript, Vite |
| 프로세스 통신 | ZeroMQ (REQ/REP, PUB/SUB) |
| 로컬 저장소 | SQLite |
| Backend 통신 | REST API + WebSocket |

## 개발 시작하기

### 1. Phase 시작 시
해당 Phase의 문서를 열고 **구현 체크리스트** 섹션을 확인하세요.

### 2. 작업 완료 시
- 체크리스트 항목을 `[x]`로 변경
- 이 README의 "개발 진행 현황" 테이블 업데이트
  - 진행중: 🔄
  - 완료: ✅
  - 진행률 업데이트

### 3. 예시
```markdown
## 구현 체크리스트

- [x] `station_service/models/__init__.py` 생성  ← 완료
- [ ] `station_service/models/station.py`        ← 미완료
```

---

## 버전 정보

- 문서 버전: 1.2.0
- 최종 수정: 2025-12-30
