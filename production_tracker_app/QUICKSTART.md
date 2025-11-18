# Quick Start Guide - Production Tracker App

## 🚀 5분 안에 시작하기

### 1단계: 의존성 설치 (1분)

```bash
cd c:\myCodeRepoWindows\F2X_NeuroHub\production_tracker_app
pip install -r requirements.txt
```

### 2단계: 백엔드 서버 시작 (1분)

```bash
# 다른 터미널에서
cd c:\myCodeRepoWindows\F2X_NeuroHub\backend
python -m uvicorn app.main:app --reload
```

백엔드가 http://localhost:8000에서 실행됩니다.

### 3단계: 앱 실행 (30초)

```bash
cd c:\myCodeRepoWindows\F2X_NeuroHub\production_tracker_app
python main.py
```

### 4단계: 로그인 (30초)

- 사용자명: (백엔드에 등록된 사용자)
- 비밀번호: (해당 비밀번호)
- "자동 로그인" 체크 권장

### 5단계: 초기 설정 (2분)

메뉴 → 설정:

1. **공정 선택**: 1~8번 중 선택 (예: 3. 센서 검사)
2. **파일 감시 폴더**: `C:/neurohub_work` (기본값)
3. **설비 ID**: `EQUIP-001` (예시)
4. **라인 ID**: `LINE-A` (예시)
5. **백엔드 URL**: `http://localhost:8000` (기본값)
6. **저장** 클릭
7. 앱 재시작

---

## 📱 사용 예시

### 착공 테스트

1. 앱 윈도우 포커스
2. 키보드로 LOT 번호 입력: `WF-KR-251110D-001`
3. Enter 키
4. ✅ 착공 완료 메시지 확인
5. LOT 정보 카드 업데이트 확인
6. 통계 카드 업데이트 확인

### 완공 테스트

1. 테스트 JSON 파일 생성:

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
  "result": "PASS",
  "process_data": {
    "temp_sensor": {
      "measured_temp": 60.2,
      "result": "PASS"
    }
  }
}
```

2. 파일 저장: `C:/neurohub_work/pending/test_completion.json`
3. 3초 이내 자동 감지 및 처리
4. ✅ 완공 완료 메시지 확인
5. 파일이 `completed/` 폴더로 이동 확인
6. 통계 카드 업데이트 확인

---

## 🎯 다음 단계

- [README.md](README.md) - 전체 문서
- [../docs/user-specification/](../docs/user-specification/) - 사용자 명세
- 로그 확인: `logs/tracker_YYYYMMDD.log`

---

## ⚠️ 문제 발생 시

### 백엔드 연결 실패
- 백엔드 서버 실행 확인
- URL 확인: http://localhost:8000
- 방화벽 확인

### 바코드 스캔 안 됨
- 앱 윈도우 포커스 확인
- LOT 형식 확인: `WF-KR-251110D-001`
- 키보드 입력 후 Enter 필수

### 완공 파일 처리 안 됨
- 폴더 확인: `C:/neurohub_work/pending/`
- JSON 형식 확인
- process_id 일치 확인 (설정에서 선택한 공정)
- 로그 파일 확인

---

## 📞 지원

문제가 계속되면:
1. 로그 파일 확인: `logs/`
2. 에러 메시지 캡처
3. IT 지원팀 문의
