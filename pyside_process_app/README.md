# F2X NeuroHub MES - 공정 PC 착공/완공 앱

PySide6 기반 공정 현장용 데스크톱 애플리케이션

## 📋 개요

F2X NeuroHub MES 공정 PC 앱은 제조 현장의 8개 공정에서 사용되는 착공(작업 시작) 및 완공(작업 완료) 추적 애플리케이션입니다.

### 주요 기능

- ✅ **바코드 스캔 착공**: USB HID 바코드 스캐너로 LOT 바코드 스캔 → 자동 착공 등록
- ✅ **JSON 파일 완공**: 외부 프로세스가 생성한 JSON 파일 자동 감지 → 완공 처리
- ✅ **공정 선택**: 1개 앱으로 8개 공정 모두 지원 (설정에서 공정 번호 선택)
- ✅ **자동 로그인**: 작업자 계정 저장 및 자동 로그인
- ✅ **실시간 현황**: 현재 LOT 정보, 금일 작업 통계 실시간 표시
- ✅ **오프라인 모드**: 네트워크 장애 시 자동 큐잉 및 재시도 지원
- ✅ **작업 이력 조회**: 날짜/결과별 필터링, 9컬럼 상세 이력 표시 (Ctrl+H)
- ✅ **MVVM Architecture**: Clean separation of concerns
- ✅ **에러 처리**: 사용자 친화적 한글 에러 메시지 및 로깅

## 🚀 빠른 시작

### 시스템 요구사항

- **OS**: Windows 11
- **Python**: 3.11 이상
- **메모리**: 4GB RAM 이상

### 설치

```bash
cd c:\myCodeRepoWindows\F2X_NeuroHub\pyside_process_app
pip install -r requirements.txt
```

**필수 패키지**:
- PySide6 >= 6.6.0
- requests >= 2.31.0
- pydantic >= 2.5.2
- python-dateutil >= 2.8.2
- watchdog >= 3.0.0

### 실행

#### Windows:
```batch
run.bat
```

#### 직접 실행:
```bash
python main.py
```

## Configuration

The application uses `QSettings` for persistent configuration:

- **API URL**: Default `http://localhost:8000`
- **Process Number**: 1-8 (mapped to specific processes)
- **Auto-login**: Enable/disable auto-login
- **JSON Watch Path**: Directory for automatic file processing

### Process Mapping

1. 레이저 마킹 (Laser Marking)
2. LMA 조립 (LMA Assembly)
3. 센서 검사 (Sensor Inspection)
4. 펌웨어 업로드 (Firmware Upload)
5. 로봇 조립 (Robot Assembly)
6. 성능검사 (Performance Testing)
7. 라벨 프린팅 (Label Printing)
8. 포장+외관검사 (Packaging + Visual Inspection)

## Usage

### Windows

```batch
run.bat
```

Or directly:

```bash
python main.py
```

### Linux/Mac

```bash
chmod +x run.sh
./run.sh
```

Or directly:

```bash
python3 main.py
```

## Project Structure

```
pyside_process_app/
├── main.py                 # Application entry point
├── config.py              # Configuration management (QSettings)
├── run.bat               # Windows launcher
├── run.sh                # Linux/Mac launcher
├── services/
│   ├── api_client.py     # REST API client with offline support
│   ├── auth_service.py   # JWT authentication
│   ├── process_service.py # Process data operations
│   ├── history_service.py # Work history queries
│   ├── file_watcher_service.py # JSON file watcher
│   ├── offline_manager.py # Offline request queue manager
│   └── retry_manager.py  # Automatic retry logic
├── viewmodels/
│   ├── app_state.py      # Global application state
│   └── main_viewmodel.py # Main window business logic
├── views/
│   ├── login_dialog.py   # Login dialog
│   ├── main_window.py    # Main application window
│   ├── settings_dialog.py # Settings configuration
│   └── history_dialog.py # Work history viewer (Ctrl+H)
├── utils/
│   └── logger.py         # Logging configuration
└── logs/                 # Application logs (auto-created)
```

## Auto-login Flow

1. Check if auto-login is enabled and saved token exists
2. Validate saved JWT token with backend
3. If valid → load user info → show main window
4. If invalid → show login dialog → save new token
5. If login cancelled → exit application

## Logging

Logs are automatically created in the `logs/` directory:
- Format: `app_YYYYMMDD.log`
- Daily rotation
- Console output for INFO level
- File output for DEBUG level

## Development

### Key Components

- **AppConfig**: QSettings-based configuration manager
- **APIClient**: HTTP client with retry logic, JWT support, and offline mode
- **AuthService**: JWT authentication lifecycle management
- **ProcessService**: Process data CRUD operations
- **HistoryService**: Work history queries with advanced filtering
- **FileWatcherService**: Automatic JSON file processing
- **OfflineManager**: Request queuing and connection monitoring
- **RetryManager**: Automatic retry with exponential backoff
- **AppState**: Singleton global state manager
- **MainViewModel**: Business logic layer (signals/slots)
- **MainWindow**: Primary UI with status indicator (MVVM pattern)
- **LoginDialog**: Authentication UI
- **SettingsDialog**: Configuration UI
- **HistoryDialog**: Work history viewer with filtering

### Signals & Slots

The application uses Qt's signals/slots pattern for loose coupling:

```python
# ViewModel emits signals
viewmodel.stats_updated.emit(stats)

# View connects to signals
viewmodel.stats_updated.connect(self.on_stats_updated)
```

## Backend Integration

The application connects to the FastAPI backend:

- **Auth**: `/api/v1/auth/login`, `/api/v1/auth/me`
- **Process Data**: `/api/v1/process-data`
- **Lots**: `/api/v1/lots`
- **Analytics**: `/api/v1/analytics`

## 사용 가이드

### 기본 작업 흐름

1. **앱 실행**: `run.bat` 또는 `python main.py`
2. **자동 로그인**: 저장된 토큰으로 자동 로그인 (최초 실행 시 로그인 필요)
3. **착공 처리**: USB 바코드 스캐너로 LOT 바코드 스캔
4. **완공 처리**: 외부 프로세스가 JSON 파일 생성 → 자동 감지 및 완공
5. **이력 조회**: `Ctrl+H` 또는 메뉴 → 작업 이력

### 오프라인 모드

- **자동 감지**: 백엔드 서버 연결 실패 시 자동으로 오프라인 모드 전환
- **요청 큐잉**: 오프라인 상태에서 발생한 요청은 로컬 JSON 파일로 저장
- **자동 재시도**: 연결 복구 시 저장된 요청 자동 재시도 (최대 3회)
- **상태 표시**: 상태바에 🟢 온라인 / 🔴 오프라인 상태 실시간 표시
- **상세 문서**: `OFFLINE_MODE_README.md` 참조

### 작업 이력 조회

- **단축키**: `Ctrl+H`
- **필터링**: 날짜 범위 (시작일~종료일), 결과 타입 (전체/PASS/FAIL/REWORK)
- **컬럼**: DateTime, LOT, Serial, Process, Operator, Duration, Result, Measurements, Notes
- **색상 코딩**: PASS (녹색), FAIL (빨간색), REWORK (파란색)
- **상세 문서**: `HISTORY_DIALOG_IMPLEMENTATION.md` 참조

## 아키텍처

### MVVM 패턴

```
View (UI) → ViewModel (Business Logic) → Model (Data)
    ↑              ↓ Signals                ↓
    └──────── Slots ←─────────────── Services
```

### 주요 설계 패턴

- **Singleton**: AppState (전역 상태 관리)
- **Observer**: Qt Signals/Slots (이벤트 기반 통신)
- **Dependency Injection**: 서비스 레이어 주입
- **Repository**: Service 레이어로 데이터 접근 추상화

상세 아키텍처는 `ARCHITECTURE_DIAGRAM.md` 참조

## TODO

- [ ] Add equipment status monitoring
- [ ] Implement serial-level tracking
- [ ] Add real-time dashboard
- [ ] Add Excel export for work history
- [ ] Implement print functionality
- [ ] Add batch processing support

## License

Copyright (c) 2025 F2X. All rights reserved.
