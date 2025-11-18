# F2X NeuroHub MES - 공정 PC 앱 빠른 시작 가이드

## ⚡ 5분 안에 시작하기

### 1단계: 의존성 설치 (1분)

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

---

### 2단계: 백엔드 서버 시작 (30초)

**새 터미널 창에서**:
```bash
cd c:\myCodeRepoWindows\F2X_NeuroHub\backend
uvicorn app.main:app --reload
```

백엔드가 `http://localhost:8000`에서 실행됩니다.

---

### 3단계: 데스크톱 앱 실행 (10초)

**Windows**:
```batch
cd c:\myCodeRepoWindows\F2X_NeuroHub\pyside_process_app
run.bat
```

**또는 직접 실행**:
```bash
python main.py
```

---

### 4단계: 초기 설정 (2분)

#### 4.1 로그인
- **사용자명**: 백엔드에 등록된 작업자 계정
- **비밀번호**: 해당 계정 비밀번호
- **자동 로그인**: 체크 (권장)

#### 4.2 공정 선택
1. 메뉴: **설정 (Settings)**
2. **공정 번호** 선택: 1-8
   - 1: 레이저 마킹
   - 2: LMA 조립
   - 3: 센서 검사
   - 4: 펌웨어 업로드
   - 5: 로봇 조립
   - 6: 성능검사
   - 7: 라벨 프린팅
   - 8: 포장+외관검사
3. **JSON 감시 경로** 설정: `C:\json_watch\pending` (예시)
4. **저장** 클릭

#### 4.3 JSON 디렉토리 생성
```batch
mkdir C:\json_watch\pending
mkdir C:\json_watch\completed
mkdir C:\json_watch\error
```

---

## 🎯 기본 사용법

### 착공 (작업 시작)

1. **USB 바코드 스캐너로 LOT 바코드 스캔**
   - LOT 형식: `WF-KR-YYMMDD{D|N}-nnn`
   - 예: `WF-KR-250115D-001` (2025년 1월 15일, 주간, 1번)

2. **자동 착공 등록**
   - 백엔드 API 호출: `POST /api/v1/process-data`
   - UI 업데이트: 현재 LOT 정보 표시

### 완공 (작업 완료)

**외부 프로세스가 JSON 파일 생성**:
```json
{
  "lot_number": "WF-KR-250115D-001",
  "result": "PASS",
  "process_data": {
    "측정값1": 12.5,
    "측정값2": "OK",
    "온도": 25.3
  }
}
```

**파일 저장 위치**: `C:\json_watch\pending\result.json`

**자동 완공**:
1. 파일 감지 (QFileSystemWatcher)
2. JSON 스키마 검증
3. 백엔드 완공 등록
4. 파일 이동: `pending/` → `completed/`

---

## 🔍 주요 기능

### 작업 이력 조회 (Ctrl+H)

1. **단축키**: `Ctrl+H`
2. **필터 설정**:
   - 시작일/종료일: 날짜 범위 선택
   - 결과: 전체 / PASS / FAIL / REWORK
3. **조회 버튼** 클릭
4. **결과 확인**:
   - PASS: 녹색
   - FAIL: 빨간색
   - REWORK: 파란색

### 오프라인 모드

**자동 감지**:
- 백엔드 서버 연결 실패 → 🔴 오프라인 모드 전환

**요청 큐잉**:
- 오프라인 상태에서 발생한 요청 → 로컬 JSON 파일로 저장
- 저장 위치: `pyside_process_app/offline_queue/`

**자동 재시도**:
- 연결 복구 시 → 큐 요청 자동 전송
- 최대 3회 재시도 (exponential backoff)

**상태 확인**:
- 상태바: 🟢 온라인 / 🔴 오프라인
- 큐 크기: `큐: 0`

---

## 🐛 문제 해결

### 문제 1: 로그인 실패

**원인**: 백엔드 서버가 실행되지 않음

**해결**:
```bash
cd c:\myCodeRepoWindows\F2X_NeuroHub\backend
uvicorn app.main:app --reload
```

### 문제 2: 바코드 스캔 안됨

**원인**: LOT 번호 형식 오류

**해결**: 정확한 형식 확인
- 형식: `WF-KR-YYMMDD{D|N}-nnn`
- 예: `WF-KR-250115D-001`

### 문제 3: JSON 파일 감지 안됨

**원인 1**: JSON 감시 경로 설정 오류

**해결**: 설정 다이얼로그에서 경로 확인
- 메뉴 → 설정 → JSON 감시 경로

**원인 2**: JSON 스키마 오류

**해결**: 로그 파일 확인
- `logs/app_YYYYMMDD.log`
- 에러 메시지 확인

### 문제 4: 오프라인 모드에서 복구 안됨

**해결**: 수동 재시도
1. 백엔드 서버 시작 확인
2. 상태바 **재시도** 버튼 클릭
3. 로그 확인: `logs/app_YYYYMMDD.log`

---

## 📋 JSON 파일 형식 예시

### 공정 001: 레이저 마킹

```json
{
  "lot_number": "WF-KR-250115D-001",
  "result": "PASS",
  "process_data": {
    "레이저출력": 50,
    "마킹품질": "OK",
    "소요시간": 15
  }
}
```

### 공정 003: 센서 검사

```json
{
  "lot_number": "WF-KR-250115D-001",
  "result": "PASS",
  "process_data": {
    "온도센서": 25.3,
    "압력센서": 101.3,
    "습도센서": 45.2,
    "검사결과": "OK"
  }
}
```

### 공정 006: 성능검사

```json
{
  "lot_number": "WF-KR-250115D-001",
  "result": "PASS",
  "process_data": {
    "보행속도": 1.2,
    "배터리전압": 24.5,
    "모터토크": 50.3,
    "안전성테스트": "OK"
  }
}
```

### FAIL 예시

```json
{
  "lot_number": "WF-KR-250115D-002",
  "result": "FAIL",
  "process_data": {
    "온도센서": 30.5,
    "압력센서": 95.2,
    "습도센서": 60.1,
    "검사결과": "NG"
  },
  "remarks": "온도 범위 초과"
}
```

---

## 📊 로그 확인

### 로그 위치
```
pyside_process_app/logs/app_YYYYMMDD.log
```

### 로그 레벨
- **DEBUG**: 상세 디버깅 정보 (파일)
- **INFO**: 주요 이벤트 (콘솔 + 파일)
- **WARNING**: 경고 메시지
- **ERROR**: 에러 메시지

### 로그 예시

```
2025-01-15 14:30:22,123 - INFO - Application starting...
2025-01-15 14:30:22,234 - INFO - API URL: http://localhost:8000
2025-01-15 14:30:22,345 - INFO - Process: 3 - 센서 검사
2025-01-15 14:30:23,456 - INFO - Auto-login successful
2025-01-15 14:30:23,567 - INFO - User logged in: operator1
2025-01-15 14:30:23,678 - INFO - Main window displayed
2025-01-15 14:30:45,123 - INFO - Barcode scanned: WF-KR-250115D-001
2025-01-15 14:30:45,234 - INFO - Process started for LOT: WF-KR-250115D-001
2025-01-15 14:32:15,345 - INFO - JSON file detected: C:\json_watch\pending\result.json
2025-01-15 14:32:15,456 - INFO - Process completed for LOT: WF-KR-250115D-001, Result: PASS
```

---

## 🎯 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl+H` | 작업 이력 조회 |
| `Ctrl+S` | 설정 다이얼로그 (예정) |
| `Ctrl+Q` | 앱 종료 |
| `F5` | 새로고침 (통계) |

---

## 📞 추가 문서

- **프로젝트 개요**: `README.md`
- **오프라인 모드**: `OFFLINE_MODE_README.md`
- **작업 이력**: `HISTORY_DIALOG_IMPLEMENTATION.md`
- **아키텍처**: `ARCHITECTURE_DIAGRAM.md`
- **완료 보고서**: `PROJECT_COMPLETION_SUMMARY.md`

---

## ✅ 체크리스트

### 설치 및 설정
- [ ] Python 3.11+ 설치 확인
- [ ] pip install -r requirements.txt 실행
- [ ] 백엔드 서버 시작 (`http://localhost:8000`)
- [ ] 데스크톱 앱 실행 성공
- [ ] 로그인 성공
- [ ] 공정 번호 설정
- [ ] JSON 디렉토리 생성

### 기능 테스트
- [ ] 바코드 스캔 착공 성공
- [ ] JSON 파일 완공 성공
- [ ] 실시간 통계 표시 확인
- [ ] 작업 이력 조회 (Ctrl+H) 성공
- [ ] 오프라인 모드 테스트 (백엔드 중지 → 재시작)
- [ ] 로그 파일 확인

---

**준비 완료! 🚀**

문제 발생 시 로그 파일(`logs/app_YYYYMMDD.log`)을 먼저 확인하세요.
