# F2X NeuroHub Production Tracker

**착공/완공 전용 공정 추적 애플리케이션**

생산 현장에서 LOT 바코드 스캔으로 착공을 등록하고, JSON 파일 모니터링으로 완공을 자동 처리하는 전용 앱입니다.

## 📋 주요 기능

- ✅ **바코드 스캔 착공**: USB HID 바코드 리더기로 LOT 스캔 → 자동 착공 등록
- ✅ **자동 완공 처리**: JSON 파일 감지 → 자동 완공 처리
- ✅ **공정별 설정**: 1개 앱으로 8개 공정 지원 (설정에서 공정 선택)
- ✅ **실시간 통계**: 오늘의 착공/완공/합격/불량 통계 표시
- ✅ **온라인/오프라인 표시**: 백엔드 연결 상태 실시간 표시
- ✅ **자동 로그인**: 사용자 정보 저장 및 자동 로그인
- ✅ **400x600px UI**: 생산 현장 최적화 크기 (크기 조절 가능)

## 🚀 빠른 시작

### 시스템 요구사항

- **OS**: Windows 10/11
- **Python**: 3.11 이상
- **메모리**: 4GB RAM 이상

### 설치

```bash
# 1. 폴더 이동
cd c:\myCodeRepoWindows\F2X_NeuroHub\production_tracker_app

# 2. 필수 패키지 설치
pip install -r requirements.txt
```

### 실행

```bash
# 일반 모드
python main.py

# 개발 모드 (Hot Reload - 파일 변경 시 자동 재시작)
python hot_reload.py
```

### 🛠️ 개발 도구 (skill.md 기반)

#### Hot Reload - 자동 재시작
파일 변경 시 앱 자동 재시작으로 개발 생산성 향상:
```bash
python hot_reload.py
```

**기능:**
- `.py`, `.json` 파일 감지
- 1초 디바운스 (중복 재시작 방지)
- 콘솔 출력 유지
- Ctrl+C로 종료

#### Visual Debugger - 위젯 분석
실시간 위젯 트리 시각화 및 속성 검사:
```python
from visual_debugger import launch_with_debugger

# main.py 수정
app = QApplication(sys.argv)
window = MainWindow(viewmodel, config)
debugger = launch_with_debugger(window)  # 추가
sys.exit(app.exec())
```

**기능:**
- 📂 위젯 트리 (계층 구조)
- 🔧 속성 Inspector (geometry, visibility 등)
- 🎨 스타일시트 뷰어
- ⚠️ 자동 이슈 감지
- ✨ 선택 위젯 하이라이트
- 🖼️ "모든 테두리 표시" 모드

## ⚙️ 초기 설정

앱을 처음 실행하면 다음 설정이 필요합니다:

### 1. 로그인

- 사용자명과 비밀번호 입력
- "자동 로그인" 체크 시 다음부터 자동 로그인

### 2. 환경설정 (메뉴 → 설정)

#### 공정 설정
- 공정 선택: 1~8번 중 선택
  1. 레이저 마킹
  2. LMA 조립
  3. 센서 검사
  4. 펌웨어 업로드
  5. 로봇 조립
  6. 성능검사
  7. 라벨 프린팅
  8. 포장+외관검사

#### 파일 감시 폴더
- 기본값: `C:/neurohub_work`
- 하위 폴더 자동 생성:
  - `pending/` - 완공 JSON 파일 대기
  - `completed/` - 처리 완료 파일
  - `error/` - 오류 파일

#### 설비 설정
- 설비 ID: (예: EQUIP-001)
- 라인 ID: (예: LINE-A)

#### API 설정
- 백엔드 URL: (예: http://localhost:8000)

## 📱 사용 방법

### 착공 처리

1. 작업자가 바코드 리더기로 LOT 바코드 스캔
2. LOT 번호 자동 인식 (형식: WF-KR-251110D-001)
3. 백엔드 API 호출 (`POST /api/v1/process/start`)
4. 착공 완료 메시지 표시
5. 현재 LOT 정보 카드 업데이트

### 완공 처리

1. 외부 공정 앱이 작업 완료 후 JSON 파일 생성
   - 저장 위치: `C:/neurohub_work/pending/`
   - 파일명 예: `PROC-003_20250110_103025.json`
2. 파일 감시 서비스가 3초마다 자동 스캔
3. 해당 공정 ID와 일치하는 파일 감지
4. JSON 파싱 및 백엔드 API 호출 (`POST /api/v1/process/complete`)
5. 완공 완료 메시지 표시
6. 파일을 `completed/` 폴더로 이동

### 통계 확인

- 오늘의 통계 카드에 실시간 표시
  - 착공 건수
  - 완공 건수
  - 합격 건수
  - 불량 건수
  - 진행중 건수
- 5초마다 자동 갱신

## 🗂️ 프로젝트 구조

```
production_tracker_app/
├── main.py                    # 앱 진입점
├── config.py                  # 설정 관리 (QSettings)
├── requirements.txt           # 패키지 의존성
├── README.md                  # 이 파일
│
├── services/                  # 비즈니스 로직 서비스
│   ├── api_client.py         # HTTP API 클라이언트
│   ├── auth_service.py       # JWT 인증
│   ├── work_service.py       # 착공/완공 처리
│   ├── barcode_service.py    # 바코드 처리
│   └── completion_watcher.py # 파일 감시
│
├── viewmodels/               # MVVM 뷰모델
│   └── main_viewmodel.py    # 메인 비즈니스 로직
│
├── views/                    # UI 뷰
│   ├── main_window.py       # 메인 윈도우 (400x600)
│   ├── login_dialog.py      # 로그인 대화상자
│   └── settings_dialog.py   # 설정 대화상자
│
├── widgets/                  # 커스텀 UI 위젯
│   ├── lot_display_card.py  # LOT 정보 카드
│   └── stats_card.py        # 통계 카드
│
└── utils/                    # 유틸리티
    ├── logger.py            # 로깅 설정
    └── constants.py         # 상수 정의
```

## 📊 아키텍처

### MVVM 패턴

```
View (MainWindow, Dialogs)
    ↓ Signals/Slots
ViewModel (MainViewModel) - 비즈니스 로직
    ↓
Services (API, Barcode, FileWatcher)
    ↓
Backend API + JSON Files
```

### 주요 흐름

#### 착공 흐름
```
바코드 스캔 → BarcodeService → MainViewModel → WorkService → Backend API
              (validation)      (handle)        (POST)        (DB 저장)
```

#### 완공 흐름
```
JSON 파일 생성 → CompletionWatcher → MainViewModel → WorkService → Backend API
                 (감지 & 파싱)       (handle)        (POST)        (DB 저장)
```

## 🔗 백엔드 API 연동

### 필수 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|----------|--------|------|
| `/api/v1/auth/login` | POST | 로그인 |
| `/api/v1/auth/me` | GET | 현재 사용자 정보 |
| `/api/v1/process/start` | POST | 착공 등록 |
| `/api/v1/process/complete` | POST | 완공 등록 |
| `/api/v1/analytics/daily` | GET | 일일 통계 |

### JSON 완공 파일 형식

```json
{
  "lot_number": "WF-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-003",
  "process_name": "센서 검사",
  "equipment_id": "SENSOR-CHECK-01",
  "worker_id": "W001",
  "start_time": "2025-01-10T09:00:00+09:00",
  "complete_time": "2025-01-10T09:15:00+09:00",
  "process_data": {
    "temp_sensor": {
      "measured_temp": 60.2,
      "result": "PASS"
    },
    "tof_sensor": {
      "i2c_status": "connected",
      "result": "PASS"
    }
  }
}
```

## 📝 로그

- 위치: `logs/` 폴더 (자동 생성)
- 파일명: `tracker_YYYYMMDD.log`
- 일별 자동 로테이션
- 콘솔 + 파일 동시 출력

## ⚠️ 문제 해결

### 바코드 스캔이 안 됨
- 바코드 리더기가 USB HID 키보드 모드인지 확인
- Enter 키 suffix 설정 확인
- 앱 윈도우가 포커스되어 있는지 확인

### 완공 파일이 처리되지 않음
- 파일 위치 확인: `C:/neurohub_work/pending/`
- 파일명에 올바른 process_id 포함 여부 확인
- JSON 형식이 올바른지 확인 (JSONLint 등으로 검증)
- 로그 파일 확인

### 백엔드 연결 실패
- 백엔드 서버가 실행 중인지 확인
- API URL이 올바른지 확인 (설정 → API 설정)
- 방화벽 설정 확인
- 상태바의 연결 상태 확인 (🟢 온라인 / 🔴 오프라인)

## 🔐 보안

- JWT 토큰 기반 인증
- 토큰은 QSettings에 암호화되어 저장 (Windows Registry)
- 모든 API 요청에 Authorization 헤더 포함

## 🎨 UI 테마 (JSON 기반 - skill.md)

### JSON Theme System
모든 스타일링은 `theme.json`에 중앙화:

```json
{
  "colors": {
    "brand": { "main": "#3ECF8E" },  // 브랜드 색상
    "background": { "main": "#0f0f0f", "card": "#1a1a1a" }
  },
  "window": {
    "defaultSize": { "width": 800, "height": 700 }  // 윈도우 크기
  }
}
```

### 테마 커스터마이징
1. `theme.json` 편집
2. Hot Reload 사용 시 즉시 적용
3. 일반 모드는 앱 재시작

### 컴포넌트 기반 스타일링
```python
from widgets.base_components import ThemedButton, ThemedCard

# 테마가 자동 적용됨
button = ThemedButton("확인", button_type="primary")
card = ThemedCard(min_height=120)
```

**장점:**
- ✅ 중앙화된 스타일 관리
- ✅ 일관된 디자인
- ✅ Hot Reload로 즉시 확인
- ✅ 하드코딩 색상 제거

**참고:** [ARCHITECTURE.md](ARCHITECTURE.md) - 상세한 테마 시스템 가이드

## 📦 배포

### PyInstaller로 실행 파일 생성

```bash
# 1. PyInstaller 설치
pip install pyinstaller

# 2. 실행 파일 빌드
pyinstaller --onefile --windowed --name="F2X_Production_Tracker" main.py

# 3. 결과 파일
# dist/F2X_Production_Tracker.exe
```

### 생산 PC 설치

1. 실행 파일 복사: `C:\Program Files\F2X\ProductionTracker\`
2. 바로가기 생성: 바탕화면에 배치
3. 자동 시작 설정: `shell:startup` 폴더에 바로가기 복사
4. 초기 설정 실행

## 📚 관련 문서

- [프로젝트 개요](../docs/user-specification/01-project-overview.md)
- [공정 현황](../docs/user-specification/02-product-process.md)
- [API 명세](../docs/user-specification/03-requirements/03-2-api-specs.md)

## 🔄 버전 이력

### v1.0.0 (2025-01-18)
- ✅ 초기 릴리스
- ✅ 바코드 스캔 착공
- ✅ JSON 파일 자동 완공
- ✅ 공정별 설정
- ✅ 실시간 통계
- ✅ 온/오프라인 상태 표시

## 📄 라이선스

Copyright (c) 2025 F2X. All rights reserved.

## 👥 지원

문제가 발생하면 다음으로 문의하세요:
- 이메일: support@f2x.com
- 사내 IT 지원팀
