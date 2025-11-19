# Frontend 요구사항

> user-specification 문서 기반 Frontend 관련 요구사항 정리

---

## 1. 프론트엔드 기술 스택

### 1.1 작업자 PC 애플리케이션
- **GUI Framework**: PyQt5 / PySide6
- **Python**: 3.11+
- **바코드 스캐너**: USB HID 인터페이스
- **라벨 프린터**: Zebra ZPL 프로토콜

### 1.2 관리자 대시보드
- **Framework**: React 18 + TypeScript
- **상태관리**: Zustand / React Query
- **차트**: Recharts / Apache ECharts
- **테이블**: TanStack Table (React Table)
- **UI 라이브러리**: shadcn/ui 또는 Ant Design

### 1.3 브라우저 호환성
- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+ (선택사항)

---

## 2. PyQt5 작업자 PC 애플리케이션

### 2.1 주요 기능

#### LOT 관리 (FR-LOT)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-LOT-001 | LOT 생성 | 제품 모델, 목표 수량 입력하여 LOT 생성 |
| FR-LOT-002 | LOT 조회 | 날짜/상태 필터링으로 LOT 목록 조회 |
| FR-LOT-003 | LOT 상세 보기 | LOT의 시리얼 목록 및 진행 상태 확인 |
| FR-LOT-004 | LOT 마감 | 완료된 LOT 마감 처리 |

#### 시리얼 관리 (FR-SN)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-SN-001 | 시리얼 생성 | LOT에 시리얼 번호 자동 생성 (100개 단위) |
| FR-SN-002 | 시리얼 조회 | LOT별 시리얼 목록 및 공정 진행 상태 조회 |
| FR-SN-003 | 재작업 승인 | 불량 시리얼에 대한 재작업 승인 처리 |

#### 공정 관리 (FR-PROC)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-PROC-001 | 착공 등록 | 바코드 스캔으로 공정 착공 |
| FR-PROC-002 | 완공 등록 | 공정 결과(PASS/FAIL) 및 데이터 등록 |
| FR-PROC-003 | 공정 이력 조회 | 시리얼별 공정 이력 타임라인 표시 |

### 2.2 화면 구성

#### 메인 화면
```
┌─────────────────────────────────────────────┐
│  Header: 로고, 사용자 정보, 로그아웃        │
├─────────────┬───────────────────────────────┤
│  Sidebar    │  Main Content Area            │
│  - LOT 관리 │                               │
│  - 공정 작업│  선택된 메뉴에 따른 콘텐츠    │
│  - 이력 조회│                               │
│  - 설정     │                               │
├─────────────┴───────────────────────────────┤
│  Footer: 연결 상태, 프린터 상태, 버전       │
└─────────────────────────────────────────────┘
```

#### 공정 작업 화면
```
┌─────────────────────────────────────────────┐
│  공정명: [공정 선택 드롭다운]               │
├─────────────────────────────────────────────┤
│  바코드 입력: [________________] [스캔]     │
├─────────────────────────────────────────────┤
│  시리얼 정보                                │
│  - 시리얼 번호: PSA10-KR-251110D-001-0001  │
│  - LOT 번호: PSA10-KR-251110D-001          │
│  - 현재 상태: IN_PROGRESS                   │
├─────────────────────────────────────────────┤
│  공정별 데이터 입력 폼                      │
│  (공정에 따라 동적으로 변경)                │
├─────────────────────────────────────────────┤
│  [착공]  [완공-PASS]  [완공-FAIL]           │
└─────────────────────────────────────────────┘
```

### 2.3 공정별 입력 폼

#### 공정 2: LMA 조립
- SMA Spring LOT 번호 (텍스트)
- Busbar LOT 번호 (텍스트)
- 조립 시간 (숫자, 초)
- 육안 검사 결과 (PASS/FAIL)

#### 공정 3: 센서 검사
- 온도 센서 측정값 (숫자, °C)
- ToF 센서 I2C 통신 (PASS/FAIL)

#### 공정 4: 펌웨어 업로드
- 펌웨어 버전 (텍스트, 자동)
- 업로드 상태 (자동 업데이트)

#### 공정 6: 성능검사
- 테스트 포인트 목록 (표)
  - 온도, 변위, 측정 힘
- 전체 결과 (자동 계산)

#### 공정 7: 라벨 프린팅
- 라벨 프린터 선택
- 프린트 미리보기
- 프린트 버튼

### 2.4 바코드 스캐너 연동

#### 연동 방식
- USB HID 모드 (키보드 에뮬레이션)
- 입력 필드에 포커스 후 스캔

#### 스캔 포맷
- 시리얼 번호: `PSA10-KR-YYMMDD{D/N}-NNN-NNNN`
- LOT 번호: `PSA10-KR-YYMMDD{D/N}-NNN`

#### 처리 로직
```python
def on_barcode_scanned(barcode: str):
    if is_serial_number(barcode):
        # 시리얼 조회 및 공정 착공 처리
        serial = api.get_serial(barcode)
        show_serial_info(serial)
    elif is_lot_number(barcode):
        # LOT 조회 및 상세 정보 표시
        lot = api.get_lot(barcode)
        show_lot_info(lot)
```

### 2.5 라벨 프린터 연동

#### Zebra 프린터 설정
- 프로토콜: ZPL (Zebra Programming Language)
- 연결 방식: TCP/IP 또는 USB
- 기본 포트: 9100

#### 라벨 템플릿 (ZPL)
```zpl
^XA
^FO50,50^A0N,30,30^FD{serial_number}^FS
^FO50,100^BY2^BCN,100,Y,N,N^FD{serial_number}^FS
^FO50,220^A0N,25,25^FD{lot_number}^FS
^FO50,260^A0N,20,20^FD{date}^FS
^XZ
```

#### Circuit Breaker 패턴
```python
# 프린터 상태 확인
printer_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=PrinterException
)

@printer_circuit_breaker
def print_label(serial_number: str):
    # 라벨 출력 로직
    pass
```

### 2.6 File Watcher 클라이언트

#### 용도
- 외부 공정 앱 (성능검사 등)과의 JSON 파일 기반 데이터 연동

#### 처리 흐름
```
외부 앱 → JSON 파일 생성 → File Watcher 감지 → API 호출 → DB 저장
```

#### JSON 파일 포맷
```json
{
  "serial_number": "PSA10-KR-251110D-001-0001",
  "process_id": "PROC-006",
  "worker_id": "W001",
  "result": "PASS",
  "data": {
    "test_results": [...],
    "overall_result": "PASS"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 2.7 오프라인 지원

#### 로컬 캐시
- SQLite 로컬 DB에 최근 작업 데이터 캐시
- 네트워크 복구 시 자동 동기화

#### 동기화 로직
```python
def sync_offline_data():
    pending_records = local_db.get_pending()
    for record in pending_records:
        try:
            api.submit(record)
            local_db.mark_synced(record.id)
        except NetworkError:
            break
```

---

## 3. React 관리자 대시보드

### 3.1 주요 기능

#### 대시보드 (FR-DASH)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-DASH-001 | 실시간 현황 | 오늘의 생산 현황 요약 (목표/실적/달성률) |
| FR-DASH-002 | 공정별 현황 | 공정별 착공/완공/불량 현황 |
| FR-DASH-003 | 시간대별 추이 | 시간대별 생산량 추이 차트 |
| FR-DASH-004 | 불량 현황 | 공정별/유형별 불량 현황 |

#### 모니터링 (FR-MON)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-MON-001 | LOT 진행 모니터링 | 활성 LOT의 실시간 진행 상태 |
| FR-MON-002 | 공정 흐름도 | 시각적 공정 흐름 및 병목 표시 |
| FR-MON-003 | 알림 | 이상 상황 알림 (지연, 불량률 초과 등) |

#### 보고서 (FR-RPT)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-RPT-001 | 생산 보고서 | 일별/주별/월별 생산 통계 |
| FR-RPT-002 | 품질 보고서 | 불량률 분석 및 추이 |
| FR-RPT-003 | 추적성 보고서 | 시리얼별 전체 공정 이력 |

#### 마스터 데이터 관리 (FR-MASTER)
| 기능 ID | 기능명 | 설명 |
|---------|--------|------|
| FR-MASTER-001 | 제품 모델 관리 | 제품 모델 CRUD |
| FR-MASTER-002 | 공정 관리 | 공정 정보 관리 |
| FR-MASTER-003 | 설비 관리 | 설비/장비 정보 관리 |
| FR-MASTER-004 | 사용자 관리 | 사용자 계정 및 권한 관리 |

### 3.2 화면 구성

#### 대시보드 레이아웃
```
┌─────────────────────────────────────────────────────┐
│  Header: 로고, 검색, 알림, 사용자 메뉴              │
├─────────┬───────────────────────────────────────────┤
│ Sidebar │  Dashboard                                │
│         │  ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│ - 대시보드│  │  생산   │ │  불량   │ │  달성률  │     │
│ - LOT   │  │  현황   │ │  현황   │ │         │     │
│ - 공정   │  └─────────┘ └─────────┘ └─────────┘     │
│ - 보고서 │  ┌───────────────────────────────────┐   │
│ - 마스터 │  │    시간대별 생산량 추이 차트      │   │
│ - 설정   │  │                                   │   │
│         │  └───────────────────────────────────┘   │
│         │  ┌─────────────────┐ ┌─────────────────┐ │
│         │  │ 공정별 현황     │ │ 최근 알림       │ │
│         │  └─────────────────┘ └─────────────────┘ │
└─────────┴───────────────────────────────────────────┘
```

### 3.3 차트 및 시각화

#### 생산량 추이 차트
- **타입**: Line Chart
- **X축**: 시간 (hourly/daily)
- **Y축**: 생산량
- **필터**: 기간, 제품 모델, 라인

#### 공정별 현황 차트
- **타입**: Stacked Bar Chart
- **데이터**: 공정별 PASS/FAIL 수량
- **색상**: PASS(green), FAIL(red)

#### 불량 유형별 Pareto 차트
- **타입**: Combo (Bar + Line)
- **Bar**: 불량 유형별 수량
- **Line**: 누적 비율

#### 실시간 공정 흐름도
- **타입**: Flow Diagram
- **노드**: 8개 공정
- **색상**: 정상(green), 지연(yellow), 이상(red)
- **데이터**: 현재 WIP, 사이클 타임

### 3.4 테이블 컴포넌트

#### LOT 목록 테이블
```tsx
interface LotTableProps {
  columns: [
    { key: 'lot_number', header: 'LOT 번호', sortable: true },
    { key: 'product_model', header: '제품 모델' },
    { key: 'target_quantity', header: '목표 수량' },
    { key: 'completed_quantity', header: '완료 수량' },
    { key: 'status', header: '상태', filterable: true },
    { key: 'created_at', header: '생성일', sortable: true },
    { key: 'actions', header: '액션' }
  ];
  pagination: true;
  pageSize: [10, 20, 50];
}
```

#### 시리얼 목록 테이블
```tsx
interface SerialTableProps {
  columns: [
    { key: 'serial_number', header: '시리얼 번호' },
    { key: 'sequence', header: '순번' },
    { key: 'status', header: '상태' },
    { key: 'current_process', header: '현재 공정' },
    { key: 'progress', header: '진행률', type: 'progress-bar' },
    { key: 'rework_count', header: '재작업' },
    { key: 'updated_at', header: '최종 업데이트' }
  ];
  expandable: true;  // 공정 이력 표시
}
```

### 3.5 실시간 업데이트

#### WebSocket 연결
```typescript
// 대시보드 실시간 데이터
const socket = new WebSocket('wss://api.example.com/ws/dashboard');

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'production_update':
      updateProductionStats(data.payload);
      break;
    case 'defect_alert':
      showDefectAlert(data.payload);
      break;
    case 'lot_status_change':
      updateLotStatus(data.payload);
      break;
  }
};
```

#### 폴링 방식 (대안)
```typescript
// 5초 간격 폴링
const { data } = useQuery({
  queryKey: ['dashboard'],
  queryFn: fetchDashboardData,
  refetchInterval: 5000,
});
```

### 3.6 알림 시스템

#### 알림 유형
| 유형 | 조건 | 심각도 |
|------|------|--------|
| 불량률 초과 | 공정별 불량률 > 5% | Warning |
| 생산 지연 | LOT 완료 예상 시간 초과 | Warning |
| 설비 이상 | 설비 상태 변경 | Critical |
| 재작업 요청 | 재작업 승인 대기 | Info |

#### 알림 UI
```tsx
interface NotificationProps {
  type: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  timestamp: Date;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

---

## 4. 공통 UI/UX 요구사항

### 4.1 디자인 원칙
- **일관성**: 동일한 컴포넌트, 색상, 타이포그래피 사용
- **접근성**: WCAG 2.1 AA 준수
- **반응성**: 다양한 화면 크기 지원

### 4.2 색상 체계
| 용도 | 색상 코드 | 설명 |
|------|----------|------|
| Primary | #1976D2 | 주요 액션, 버튼 |
| Success | #4CAF50 | PASS, 성공 |
| Error | #F44336 | FAIL, 오류 |
| Warning | #FF9800 | 경고, 주의 |
| Info | #2196F3 | 정보 |

### 4.3 타이포그래피
- **한글**: Pretendard, Noto Sans KR
- **영문/숫자**: Inter, Roboto Mono (고정폭)
- **크기 체계**: 12px, 14px, 16px, 18px, 24px, 32px

### 4.4 반응형 브레이크포인트
| 크기 | 너비 | 대상 |
|------|------|------|
| sm | < 768px | 태블릿 세로 |
| md | 768px - 1024px | 태블릿 가로 |
| lg | 1024px - 1440px | 데스크톱 |
| xl | > 1440px | 대형 모니터 |

### 4.5 로딩 상태
- **Skeleton**: 콘텐츠 영역 로딩
- **Spinner**: 버튼, 소형 컴포넌트
- **Progress Bar**: 파일 업로드, 긴 작업

### 4.6 에러 처리
- **토스트 알림**: 일시적 오류, 성공 메시지
- **인라인 오류**: 폼 유효성 검사
- **전체 화면 오류**: 네트워크 오류, 서버 오류

---

## 5. 인증/인가 UI

### 5.1 로그인 화면
```
┌─────────────────────────┐
│         로고            │
├─────────────────────────┤
│  사용자 ID: [________]  │
│  비밀번호:  [________]  │
│                         │
│  [       로그인       ] │
│                         │
│  비밀번호 찾기          │
└─────────────────────────┘
```

### 5.2 JWT 토큰 관리
```typescript
// React Query + Axios Interceptor
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refreshToken');
      const { data } = await refreshAccessToken(refreshToken);
      localStorage.setItem('accessToken', data.access_token);
      return api(error.config);
    }
    return Promise.reject(error);
  }
);
```

### 5.3 역할별 접근 제어
| 역할 | 접근 가능 화면 |
|------|---------------|
| WORKER | 공정 작업, 이력 조회 (본인) |
| MANAGER | 대시보드, 보고서, LOT 관리 |
| ADMIN | 전체 기능, 마스터 데이터 관리, 사용자 관리 |

```typescript
// 역할 기반 라우트 보호
const ProtectedRoute = ({ roles, children }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};
```

---

## 6. 비기능 요구사항

### 6.1 성능 (NFR-PERF)
| ID | 요구사항 | 목표 |
|----|----------|------|
| NFR-PERF-001 | 페이지 로드 시간 | < 2초 |
| NFR-PERF-002 | 대시보드 새로고침 | < 3초 |
| NFR-PERF-003 | 테이블 렌더링 (1000행) | < 1초 |
| NFR-PERF-004 | 번들 크기 | < 500KB (gzip) |

### 6.2 가용성 (NFR-AVAIL)
| ID | 요구사항 | 목표 |
|----|----------|------|
| NFR-AVAIL-001 | 서비스 가용성 | 99.5% |
| NFR-AVAIL-002 | 오프라인 지원 | PyQt5 앱 기본 기능 |

### 6.3 사용성 (NFR-USE)
| ID | 요구사항 | 설명 |
|----|----------|------|
| NFR-USE-001 | 키보드 네비게이션 | 주요 기능 키보드 접근 |
| NFR-USE-002 | 단축키 지원 | 자주 사용하는 기능 단축키 |
| NFR-USE-003 | 툴팁 | 모든 아이콘에 툴팁 제공 |

---

## 7. 테스트 요구사항

### 7.1 단위 테스트
- **커버리지 목표**: 80%
- **도구**: pytest (PyQt5), Jest/Vitest (React)
- **범위**: 컴포넌트, 유틸리티 함수, 커스텀 훅

### 7.2 통합 테스트
- **도구**: Cypress, Playwright
- **범위**: 사용자 시나리오, API 연동

### 7.3 E2E 테스트 시나리오
1. 로그인 → 대시보드 접근
2. LOT 생성 → 시리얼 생성 → 공정 착공/완공
3. 바코드 스캔 → 자동 공정 처리
4. 라벨 프린팅 → 출력 확인
5. 대시보드 차트 → 데이터 정확성

---

## 8. 국제화 (i18n)

### 8.1 지원 언어
- 한국어 (기본)
- 영어 (선택사항)

### 8.2 구현 방식
```typescript
// React: react-i18next
import { useTranslation } from 'react-i18next';

const Dashboard = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.production_count', { count: 100 })}</p>
    </div>
  );
};
```

### 8.3 번역 키 구조
```json
{
  "common": {
    "save": "저장",
    "cancel": "취소",
    "delete": "삭제"
  },
  "lot": {
    "create": "LOT 생성",
    "status": {
      "CREATED": "생성됨",
      "IN_PROGRESS": "진행중",
      "COMPLETED": "완료",
      "CLOSED": "마감"
    }
  }
}
```

---

## 관련 문서

- [03-1-functional.md](../user-specification/03-requirements/03-1-functional.md) - 기능 요구사항
- [03-2-api-specs.md](../user-specification/03-requirements/03-2-api-specs.md) - API 명세
- [04-3-tech-stack.md](../user-specification/04-architecture/04-3-tech-stack.md) - 기술 스택