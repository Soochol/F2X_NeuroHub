# 착공/완공 Workflow 테스트 계획

## 테스트 환경 준비

### 필수 서비스
- [ ] Backend MES 서버 실행 (localhost:8000)
- [ ] Station Service 실행 (localhost:8080)
- [ ] Station UI 실행 (localhost:5174 dev 또는 localhost:8080/ui)

### 테스트 데이터
- **Operator Account**: admin / admin123
- **Batch**: sensor_inspection (process_id: 3)
- **WIP ID**: 테스트용 WIP ID 생성 필요

---

## Phase 1: 로그인 기능 테스트

### 1.1 로그인 성공
| 단계 | 예상 결과 |
|------|----------|
| 1. Station UI 접속 | 로그인 페이지 표시 |
| 2. admin / admin123 입력 | - |
| 3. Sign In 클릭 | Dashboard로 이동 |
| 4. Header 확인 | "admin" 사용자 이름 표시 |

### 1.2 로그인 실패
| 단계 | 예상 결과 |
|------|----------|
| 1. 잘못된 비밀번호 입력 | "Invalid username or password" 에러 |
| 2. 빈 필드로 로그인 시도 | "Username and password are required" |

### 1.3 로그아웃
| 단계 | 예상 결과 |
|------|----------|
| 1. Header의 사용자 이름 클릭 | 드롭다운 메뉴 표시 |
| 2. Logout 클릭 | 로그인 페이지로 이동 |

---

## Phase 2: Workflow 설정 테스트

### 2.1 Workflow 활성화
| 단계 | 예상 결과 |
|------|----------|
| 1. Settings 페이지 이동 | Process Workflow 섹션 표시 |
| 2. WIP Process Start/Complete 토글 ON | "Process Workflow Enabled" 알림 |
| 3. 설정 확인 | WIP Input Mode, Auto-start 옵션 표시 |

### 2.2 Workflow 비활성화
| 단계 | 예상 결과 |
|------|----------|
| 1. WIP Process Start/Complete 토글 OFF | "Process Workflow Disabled" 알림 |
| 2. 설정 확인 | 추가 옵션들 숨김 |

### 2.3 WIP Input Mode 설정
| 단계 | 예상 결과 |
|------|----------|
| 1. Manual Input (Popup) 선택 | 팝업 모드 활성화 |
| 2. Barcode Scanner 선택 | 바코드 스캐너 설정 섹션 표시 |

---

## Phase 3: 착공 (Process Start) 테스트

### 3.1 Popup 모드 착공
**전제조건**: Workflow 활성화, Input Mode = Popup

| 단계 | 예상 결과 |
|------|----------|
| 1. Batches 페이지에서 sensor_inspection 선택 | Batch 상세 페이지 |
| 2. Start Sequence 버튼 클릭 | WIP ID 입력 팝업 표시 |
| 3. 유효한 WIP ID 입력 | - |
| 4. Confirm 클릭 | 착공 API 호출 → 시퀀스 시작 |

### 3.2 착공 실패 케이스
| 케이스 | 예상 결과 |
|--------|----------|
| WIP ID 없음 | "WIP not found" 에러 |
| 선행 공정 미완료 | "Prerequisite not met" 에러 |
| 백엔드 연결 실패 | "Backend connection error" |

### 3.3 Workflow 비활성화 상태
| 단계 | 예상 결과 |
|------|----------|
| 1. Workflow OFF 상태에서 Start Sequence | WIP 팝업 없이 바로 시퀀스 시작 |

---

## Phase 4: 완공 (Process Complete) 테스트

### 4.1 시퀀스 성공 완료
**전제조건**: 착공 완료 후 시퀀스 실행 중

| 단계 | 예상 결과 |
|------|----------|
| 1. 시퀀스 모든 스텝 완료 | - |
| 2. 시퀀스 종료 | 완공 API 자동 호출 |
| 3. 결과 확인 | result=PASS, measurements 전송 |

### 4.2 시퀀스 실패 완료
| 단계 | 예상 결과 |
|------|----------|
| 1. 시퀀스 중 실패 발생 | - |
| 2. 시퀀스 종료 | 완공 API 호출 (result=FAIL) |
| 3. 결과 확인 | defects 정보 포함 |

### 4.3 시퀀스 중단
| 단계 | 예상 결과 |
|------|----------|
| 1. 시퀀스 실행 중 Stop 클릭 | 시퀀스 중단 |
| 2. 완공 처리 | 완공 API 호출 (result=ABORT 또는 미호출) |

---

## Phase 5: 통합 시나리오

### 5.1 전체 플로우 (Happy Path)
```
1. 로그인 (admin/admin123)
2. Settings → Workflow 활성화
3. Batches → sensor_inspection 선택
4. Start Sequence → WIP ID 입력 → 착공
5. 시퀀스 실행 (스텝 완료)
6. 시퀀스 완료 → 완공
7. Results에서 결과 확인
```

### 5.2 재작업 시나리오
```
1. 동일 WIP ID로 재시도
2. 중복 PASS 방지 확인
3. FAIL 후 재작업 가능 확인
```

---

## API 검증 체크리스트

### Backend API 호출 확인
```bash
# 착공 요청
POST /api/v1/process-operations/start
{
  "wip_id": "WIP-XXX",
  "process_id": 3,
  "operator_id": 1,
  "equipment_id": 1
}

# 완공 요청
POST /api/v1/process-operations/complete
{
  "wip_id": "WIP-XXX",
  "process_id": 3,
  "result": "PASS",
  "measurements": {...},
  "defects": []
}
```

### Station Service 로그 확인
```bash
# 로그 모니터링
tail -f station_service.log | grep -E "착공|완공|process"
```

---

## 테스트 실행 명령어

```bash
# 1. Backend 서버 실행
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# 2. Station Service 실행
cd station_service && source venv/bin/activate && python -m station_service.main

# 3. Station UI 개발 서버 (선택)
cd station_ui && npm run dev

# 4. 세션 상태 확인
curl -s http://localhost:8080/api/system/operator | python3 -m json.tool

# 5. Workflow 설정 확인
curl -s http://localhost:8080/api/system/workflow | python3 -m json.tool
```

---

## 알려진 이슈

1. **WebSocket 연결 불안정**: dev 서버에서 WebSocket 재연결 시 경고 발생 (기능에 영향 없음)
2. **바코드 스캐너**: Phase 2에서 구현 예정, 현재는 UI만 존재

---

## 테스트 완료 기준

- [ ] 로그인/로그아웃 정상 동작
- [ ] Workflow ON/OFF 토글 정상
- [ ] 착공 API 정상 호출
- [ ] 완공 API 정상 호출
- [ ] 에러 케이스 적절한 메시지 표시
- [ ] Backend MES에 데이터 정상 저장
