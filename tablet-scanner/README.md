# F2X NeuroHub - Tablet QR Scanner

태블릿 브라우저 기반 QR 코드 스캐너로 착공/완공을 처리하는 WebUI 앱입니다.

## 기능

### 핵심 기능
- **QR 코드 스캔**: 브라우저 카메라로 WIP QR 코드 스캔
- **착공 등록**: 스캔 후 공정 착공 처리
- **완공 등록**: PASS/FAIL 결과 선택하여 완공 처리
- **자동 공정 감지**: WIP 상태 기반 다음 공정 자동 추천
- **수동 공정 변경**: 작업자가 필요시 공정 임의 선택 가능
- **실시간 통계**: 오늘의 착공/완공/합격/불량 카운트

### PWA (Progressive Web App)
- **홈 화면 추가**: 태블릿 홈 화면에 앱 아이콘 추가 가능
- **오프라인 지원**: Service Worker로 정적 자원 캐싱
- **전체화면 모드**: standalone 모드로 브라우저 UI 없이 실행

### 오프라인 모드
- **오프라인 큐**: 네트워크 끊김 시 IndexedDB에 작업 저장
- **자동 동기화**: 네트워크 복구 시 대기 중인 작업 자동 전송
- **상태 표시**: 온라인/오프라인 상태 실시간 표시
- **대기 건수 표시**: 동기화 대기 중인 작업 수 표시

### 소리/진동 피드백
- **스캔 감지음**: QR 코드 인식 시 비프음
- **성공음**: 착공/완공 성공 시 화음
- **에러음**: 실패 시 경고음
- **진동 피드백**: 모든 이벤트에 진동 피드백
- **소리 ON/OFF**: 설정으로 소리 끄기 가능

### 측정값 입력
- **공정별 폼**: 각 공정에 맞는 측정 항목 자동 표시
- **데이터 검증**: 필수 항목 및 범위 검증
- **단위 표시**: 측정값 단위 표시

## 기술 스택

- React 19 + TypeScript
- Vite (빌드 도구)
- vite-plugin-pwa (PWA 지원)
- html5-qrcode (QR 스캔)
- Zustand (상태 관리)
- idb-keyval (IndexedDB 오프라인 저장)
- Web Audio API (소리 피드백)
- Axios (HTTP 클라이언트)

## 개발 환경 실행

### Docker Compose (권장)

```bash
# 프로젝트 루트에서
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up -d

# tablet-scanner만 실행
docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up -d tablet-scanner
```

접속: http://localhost:5174

### 로컬 개발

```bash
cd tablet-scanner
npm install
npm run dev
```

접속: http://localhost:5174

## 빌드

```bash
npm run build
```

빌드 결과물: `dist/` 폴더

## Docker 프로덕션 빌드

```bash
docker build -t f2x-tablet-scanner .
docker run -p 80:80 f2x-tablet-scanner
```

## 사용 방법

1. 로그인 (기존 NeuroHub 계정 사용)
2. QR 코드 스캔 영역에 WIP 바코드/QR 위치
3. 스캔 시 자동으로 다음 공정 추천
4. 필요시 공정 수동 선택
5. 착공 또는 완공 버튼 클릭
6. 완공 시 PASS/FAIL 결과 선택 후 측정값 입력
7. 오프라인에서도 작업 가능 (네트워크 복구 시 자동 동기화)

## 홈 화면 추가 (PWA)

### Android (Chrome)
1. 앱 접속 후 브라우저 메뉴 (⋮) 클릭
2. "홈 화면에 추가" 선택
3. 앱 이름 확인 후 "추가"

### iPad (Safari)
1. 앱 접속 후 공유 버튼 클릭
2. "홈 화면에 추가" 선택
3. 앱 이름 확인 후 "추가"

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| VITE_API_URL | 백엔드 API URL | http://localhost:8000 |

## 프로젝트 구조

```
tablet-scanner/
├── src/
│   ├── api/              # API 클라이언트
│   │   └── client.ts
│   ├── components/       # React 컴포넌트
│   │   ├── QrScanner.tsx       # QR 스캐너
│   │   ├── ProcessSelector.tsx # 공정 선택기
│   │   ├── StatsCard.tsx       # 통계 카드
│   │   ├── ActionButtons.tsx   # 착공/완공 버튼
│   │   └── MeasurementForm.tsx # 측정값 입력 폼
│   ├── hooks/            # 커스텀 훅
│   │   └── useProcessDetection.ts
│   ├── pages/            # 페이지 컴포넌트
│   │   ├── LoginPage.tsx
│   │   └── WorkPage.tsx
│   ├── services/         # 비즈니스 로직 서비스
│   │   ├── offlineQueue.ts   # 오프라인 큐
│   │   └── soundService.ts   # 소리 피드백
│   ├── store/            # Zustand 스토어
│   ├── types/            # TypeScript 타입
│   ├── App.tsx
│   └── main.tsx
├── public/               # 정적 자원
│   ├── pwa-192x192.png
│   └── apple-touch-icon.png
├── Dockerfile
├── nginx.conf
├── vite.config.ts        # PWA 설정 포함
└── package.json
```

## 측정값 입력 필드

각 공정별로 다른 측정 필드가 표시됩니다:

| 공정 | 측정 항목 |
|------|----------|
| 1. 레이저 마킹 | 마킹 품질, 레이저 출력(W) |
| 2. LMA 조립 | 조립 토크(N·m), 정렬 상태, Busbar LOT |
| 3. 센서 검사 | 감도(mV/Pa), 노이즈(dB), 주파수 응답(Hz) |
| 4. 펌웨어 업로드 | 펌웨어 버전, 업로드 시간(초), 검증 상태 |
| 5. 로봇 조립 | 로봇 ID, 위치 오차(mm), 사이클 타임(초) |
| 6. 성능 검사 | 출력(mW), 효율(%), 온도(°C), 습도(%) |
| 7. 라벨 프린팅 | 라벨 품질, 바코드 판독 |
| 8. 포장+외관검사 | 외관 검사, 포장 상태, 중량(g) |

## API 연동

- `POST /api/v1/process-operations/start` - 착공 등록
- `POST /api/v1/process-operations/complete` - 완공 등록
- `GET /api/v1/wip-items/{wip_id}/trace` - WIP 이력 조회
- `GET /api/v1/processes` - 공정 목록 조회

## 브라우저 지원

- Chrome/Edge (Android, Windows)
- Safari (iPad)
- Firefox

**참고**: 카메라 접근을 위해 HTTPS 또는 localhost 환경이 필요합니다.

## 오프라인 동작

1. **네트워크 끊김 감지**: 자동으로 오프라인 모드 전환
2. **로컬 저장**: 착공/완공 요청을 IndexedDB에 저장
3. **대기 표시**: 헤더에 대기 중인 작업 수 표시
4. **자동 동기화**: 네트워크 복구 시 자동 전송
5. **재시도 로직**: 실패 시 최대 5회 재시도
