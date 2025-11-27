# 공정별 착공/완공 데이터 요구사항 분석

Production Tracker App에서 MES 백엔드와 연동할 때 각 공정별로 필요한 데이터 구조를 정의합니다.

---

## 1. 공정 개요

| 공정 # | Process ID | 공정명 (Korean) | 공정명 (English) | 소요시간 | 재작업 |
|--------|------------|----------------|------------------|----------|--------|
| 1 | PROC-001 | 레이저 마킹 | Laser Marking | ~60초 | 불가 |
| 2 | PROC-002 | LMA 조립 | LMA Assembly | ~1시간 | 가능 |
| 3 | PROC-003 | 센서 검사 | Sensor Inspection | ~60초 | 가능 |
| 4 | PROC-004 | 펌웨어 업로드 | Firmware Upload | ~60초 | 가능 |
| 5 | PROC-005 | 로봇 조립 | Robot Assembly | ~1시간 | 가능 |
| 6 | PROC-006 | 성능검사 | Performance Test | ~10분 | 가능 |
| 7 | PROC-007 | 라벨 프린팅 | Label Printing | ~40초 | 가능 |
| 8 | PROC-008 | 포장+외관검사 | Packaging + Visual Inspection | TBD | - |

---

## 2. 착공 (Start) 데이터 요구사항

### 2.1 공통 착공 데이터

모든 공정의 착공 API (`POST /api/v1/process/start`)에 필요한 데이터:

```json
{
  "lot_number": "string (필수) - LOT 바코드 스캔 값",
  "line_id": "string (필수) - 생산라인 ID (예: LINE-A)",
  "process_id": "string (필수) - 공정 ID (PROC-001 ~ PROC-008)",
  "process_name": "string (필수) - 공정명 (한글)",
  "equipment_id": "string (필수) - 장비/설비 ID",
  "worker_id": "string (필수) - 작업자 ID",
  "start_time": "string (필수) - ISO 8601 타임스탬프"
}
```

### 2.2 착공 검증 규칙

1. **선행 공정 확인**: 이전 공정이 PASS 완료되어야 함 (공정 1 제외)
2. **LOT 상태 확인**: LOT이 CREATED 또는 IN_PROGRESS 상태여야 함
3. **중복 착공 방지**: 이미 PASS 완료된 경우 착공 불가 (FAIL 재시도는 허용)
4. **예외 사항**: 공정 7 (라벨 프린팅)은 공정 6이 FAIL이어도 착공 가능 (불량품도 라벨 필요)

---

## 3. 완공 (Complete) 데이터 요구사항

### 3.1 공통 완공 데이터 구조

```json
{
  "lot_number": "string (필수)",
  "line_id": "string (필수)",
  "process_id": "string (필수)",
  "process_name": "string (필수)",
  "equipment_id": "string (필수)",
  "worker_id": "string (필수)",
  "start_time": "string (필수) - ISO 8601",
  "complete_time": "string (필수) - ISO 8601",
  "result": "string (필수) - PASS 또는 FAIL",
  "process_data": { "object (필수) - 공정별 상세 데이터" }
}
```

---

### 3.2 공정 1: 레이저 마킹 (Laser Marking)

**목적**: 레이저로 LMA에 LOT 번호 각인

#### 완공 데이터 (process_data)

```json
{
  "process_data": {
    "lot_number_engraved": "string (필수) - 각인된 LOT 번호",
    "marking_result": "string (필수) - SUCCESS 또는 FAIL"
  }
}
```

#### 검증 규칙
- `marking_result`: "SUCCESS" 또는 "FAIL"만 허용

#### 품질 검사
- 바코드 리더기로 각인 결과 검증

#### 비고
- 재작업 **불가** (레이저 마킹 특성)
- 마킹 실패 시 제품은 불량 처리

---

### 3.3 공정 2: LMA 조립 (LMA Assembly)

**목적**: 플라스틱 부품 + SMA 스프링 조립

#### PASS 완공 데이터

```json
{
  "result": "PASS",
  "process_data": {
    "sma_spring_lot": "string (필수) - SMA 스프링 LOT (형식: SPRING-YYYYMMDDNN)",
    "busbar_lot": "string (필수) - 부스바 LOT (형식: BUSBAR-YYYYMMDDNN)",
    "assembly_time": "number (필수) - 조립 시간 (분, > 0)",
    "visual_inspection": "string (필수) - PASS 또는 FAIL"
  }
}
```

#### FAIL 완공 데이터 (작업자 판정)

```json
{
  "result": "FAIL",
  "process_data": {
    "sma_spring_lot": "string (필수)",
    "busbar_lot": "string (필수)",
    "assembly_time": "number (필수)",
    "visual_inspection": "string (필수) - FAIL",
    "defect_type": "string (필수) - PART_DEFECT 또는 ASSEMBLY_ERROR",
    "defect_part": "string (선택) - 불량 부품명 (예: SMA 스프링)",
    "defect_description": "string (선택) - 불량 설명"
  }
}
```

#### 불량 유형 코드
- `PART_DEFECT`: 부품 불량 (SMA 스프링, 플라스틱 부품)
- `ASSEMBLY_ERROR`: 조립 오류 (체결 실패, 순서 오류)

---

### 3.4 공정 3: 센서 검사 (Sensor Inspection)

**목적**: 온도 센서 (60C ± 1C) 및 TOF 센서 (I2C 통신) 테스트

#### PASS 완공 데이터

```json
{
  "result": "PASS",
  "process_data": {
    "temp_sensor": {
      "measured_temp": "number (필수) - 측정 온도 (유효: 59.0~61.0C)",
      "target_temp": "number (필수) - 목표 온도 (60.0)",
      "tolerance": "number (필수) - 허용 오차 (1.0)",
      "result": "string (필수) - PASS"
    },
    "tof_sensor": {
      "i2c_communication": "boolean (필수) - 연결 시 true",
      "result": "string (필수) - PASS"
    }
  }
}
```

#### FAIL 완공 데이터 (자동 검사)

```json
{
  "result": "FAIL",
  "process_data": {
    "temp_sensor": {
      "measured_temp": 58.0,
      "target_temp": 60.0,
      "tolerance": 1.0,
      "result": "FAIL"
    },
    "tof_sensor": {
      "i2c_communication": true,
      "result": "PASS"
    },
    "defect_type": "string (필수) - SENSOR_TEMP_FAIL 또는 SENSOR_TOF_FAIL",
    "defect_description": "string (필수) - 상세 실패 설명"
  }
}
```

#### 불량 유형 코드
- `SENSOR_TEMP_FAIL`: 온도 센서 범위 초과
- `SENSOR_TOF_FAIL`: TOF 센서 I2C 통신 실패

#### 검증 규칙
- `temp_sensor.measured_temp`: PASS를 위해 59.0 ~ 61.0 사이여야 함
- `tof_sensor.i2c_communication`: PASS를 위해 `true`여야 함

---

### 3.5 공정 4: 펌웨어 업로드 (Firmware Upload)

**목적**: 제어 보드 MCU에 펌웨어 업로드

#### 완공 데이터

```json
{
  "process_data": {
    "firmware_version": "string (필수) - 버전 형식 v1.2.3",
    "upload_result": "string (필수) - SUCCESS 또는 FAIL"
  }
}
```

#### 불량 유형 코드
- `FIRMWARE_UPLOAD_FAIL`: 업로드 중단, 검증 실패
- `FIRMWARE_COMM_ERROR`: 케이블 접촉 불량, 포트 오류

#### 비고
- 자동 재시도 최대 3회
- 펌웨어 파일은 `GET /api/v1/firmware/latest`를 통해 서버에서 배포
- MD5 해시 검증 필요

---

### 3.6 공정 5: 로봇 조립 (Robot Assembly)

**목적**: 로봇 본체에 LMA 조립, 케이블 연결

#### PASS 완공 데이터

```json
{
  "result": "PASS",
  "process_data": {
    "assembly_time": "number (필수) - 조립 시간 (분, > 0)",
    "cable_connection": "string (필수) - OK 또는 FAIL",
    "final_visual_check": "string (필수) - PASS 또는 FAIL"
  }
}
```

#### FAIL 완공 데이터

```json
{
  "result": "FAIL",
  "process_data": {
    "assembly_time": "number (필수)",
    "cable_connection": "string (필수)",
    "final_visual_check": "string (필수)",
    "defect_type": "string (필수) - ASSEMBLY_ERROR 또는 APPEARANCE_DEFECT",
    "defect_description": "string (선택) - 불량 설명"
  }
}
```

#### 불량 유형 코드
- `ASSEMBLY_ERROR`: 체결 불량
- `APPEARANCE_DEFECT`: 스크래치, 손상

#### 주요 점검 항목
- LMA 체결 상태
- 케이블 연결 상태 (단선, 접촉 불량)
- 외관 손상

---

### 3.7 공정 6: 성능검사 (Performance Test)

**목적**: 온도, 변위, 힘 측정

#### 완공 데이터

```json
{
  "result": "PASS",
  "process_data": {
    "test_results": [
      {
        "test_point_id": "string (필수) - 테스트 포인트 식별자 (예: T38_P170)",
        "temperature": "number (필수) - 측정 온도 (유효: 40~70C)",
        "displacement": "number (필수) - 측정 변위 (유효: 0~250mm)",
        "measured_force": "number (필수) - 측정 힘 (유효: 0~30kgf)",
        "spec": {
          "target_force": "number (필수) - 목표 힘 값",
          "tolerance": "number (필수) - 허용 오차 (일반적으로 1.0 kgf)"
        },
        "result": "string (필수) - PASS 또는 FAIL"
      }
    ],
    "overall_result": "string (필수) - PASS 또는 FAIL",
    "test_duration_seconds": "number (필수) - 총 테스트 시간",
    "tested_at": "string (필수) - ISO 8601 타임스탬프"
  }
}
```

#### 테스트 프로토콜 예시
- 조건: 200mm 변위에서 LMA를 52C로 가열
- 측정: 발생 힘 (kgf)
- 통과 기준: 목표 ± 2kgf

#### 불량 유형 코드
- `PERFORMANCE_FAIL`: 힘 측정치가 사양 미달

#### 검증 규칙
- `test_results`: 배열 길이 > 0
- `temperature`: 40-70C 범위
- `displacement`: 0-250mm 범위
- `measured_force`: 0-30kgf 범위

---

### 3.8 공정 7: 라벨 프린팅 (Label Printing)

**목적**: 시리얼 번호 생성, 바코드 라벨 인쇄 및 부착

#### 완공 데이터

```json
{
  "process_data": {
    "serial_number": "string (필수) - 생성된 시리얼 (형식: PSA10-KR-YYMMDDX-NNN-NNNN)",
    "label_printed": "boolean (필수) - 인쇄 성공 시 true",
    "printer_id": "string (필수) - 사용된 프린터 ID",
    "print_time": "string (필수) - ISO 8601 타임스탬프",
    "barcode_verified": "boolean (선택) - 바코드 검증 결과"
  }
}
```

#### 시리얼 번호 형식
`[LOT_NUMBER]-[SEQUENCE]`
- 예시: `PSA10-KR-251110D-001-0001`
- 시퀀스: 0001-9999 (일반적으로 LOT당 0001-0100)

#### 불량 유형 코드
- `LABEL_PRINT_FAIL`: 프린터 오류, 용지 부족
- `LABEL_ATTACH_ERROR`: 잘못된 위치, 접착 불량

#### 라벨 정보
- 크기: 60mm x 20mm
- 내용: 시리얼 번호, LOT 번호, 제품명, 생산일
- 프린터: Zebra ZT 시리즈 (ZPL 명령)

---

### 3.9 공정 8: 포장+외관검사 (Packaging + Visual Inspection)

**목적**: 최종 외관 검사 및 포장 (비닐 + 박스)

#### PASS 완공 데이터

```json
{
  "result": "PASS",
  "process_data": {
    "visual_defects": "array (필수) - 발견된 결함 목록 (빈 배열 가능)",
    "packaging_complete": "boolean (필수) - 포장 완료 시 true",
    "final_result": "string (필수) - PASS 또는 FAIL"
  }
}
```

#### FAIL 완공 데이터 (결함 발견 시)

```json
{
  "result": "FAIL",
  "process_data": {
    "visual_defects": [
      {
        "type": "string - scratch, dirt, dent, missing_part, label_issue",
        "severity": "string - minor, major, critical",
        "location": "string (선택) - 결함 위치",
        "description": "string (선택) - 상세 설명"
      }
    ],
    "packaging_complete": false,
    "final_result": "FAIL"
  }
}
```

#### 검사 항목
- 스크래치
- 오염
- 부품 누락
- 라벨 부착 상태

---

## 4. 공정간 데이터 흐름

### 4.1 공정 순서 제약

```
공정 1 (레이저) -> 공정 2 (LMA 조립) -> 공정 3 (센서) ->
공정 4 (펌웨어) -> 공정 5 (로봇 조립) -> 공정 6 (성능) ->
공정 7 (라벨) -> 공정 8 (포장)
```

### 4.2 데이터 상속/요구사항

| 공정 | 이전 공정에서 필요 | 다음 공정에 제공 |
|------|-------------------|-----------------|
| 1. 레이저 마킹 | 없음 (시작 공정) | 각인된 LOT 번호 |
| 2. LMA 조립 | 레이저 마킹 완료 | 조립된 LMA, 부품 LOT |
| 3. 센서 검사 | LMA 조립 완료 | 센서 테스트 결과 |
| 4. 펌웨어 업로드 | 센서 테스트 완료 | 펌웨어 버전 |
| 5. 로봇 조립 | 펌웨어 업로드 완료 | 완성된 로봇 유닛 |
| 6. 성능검사 | 로봇 조립 완료 | 성능 측정치 |
| 7. 라벨 프린팅 | 성능검사 완료 (또는 FAIL) | 시리얼 번호, 라벨 |
| 8. 포장 | 라벨 부착 완료 | 최종 제품 상태 |

### 4.3 추적성 체인

```
시리얼 번호
  -> LOT 번호
    -> 공정 데이터 (각 공정)
      -> 사용 장비
      -> 작업자 ID
      -> 타임스탬프
      -> 측정/테스트 결과
      -> 부품 LOT (예: SMA 스프링 LOT, 부스바 LOT)
```

---

## 5. API 엔드포인트 요구사항

### 5.1 착공 API

**엔드포인트**: `POST /api/v1/process/start`

**요청 본문**:
```json
{
  "lot_number": "PSA10-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-001",
  "process_name": "레이저 마킹",
  "equipment_id": "LASER-001",
  "worker_id": "W001",
  "start_time": "2025-11-10T09:00:00Z"
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "message": "공정 착공 완료",
  "data": {
    "lot_number": "PSA10-KR-251110D-001",
    "process_id": "PROC-001",
    "status": "IN_PROGRESS"
  }
}
```

### 5.2 완공 API

**엔드포인트**: `POST /api/v1/process/complete`

**요청 본문**:
```json
{
  "lot_number": "PSA10-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-001",
  "process_name": "레이저 마킹",
  "equipment_id": "LASER-001",
  "worker_id": "W001",
  "start_time": "2025-11-10T09:00:00Z",
  "complete_time": "2025-11-10T09:01:00Z",
  "result": "PASS",
  "process_data": {
    "lot_number_engraved": "PSA10-KR-251110D-001",
    "marking_result": "SUCCESS"
  }
}
```

**응답 (성공)**:
```json
{
  "success": true,
  "message": "공정 완공 완료",
  "data": {
    "lot_number": "PSA10-KR-251110D-001",
    "process_id": "PROC-001",
    "result": "PASS"
  }
}
```

---

## 6. 에러 코드 참조

### 6.1 공정 작업 API 에러 코드

| 에러 코드 | 설명 | HTTP 상태 |
|----------|------|-----------|
| LOT_NOT_FOUND | LOT 번호가 존재하지 않음 | 404 |
| PREVIOUS_PROCESS_NOT_COMPLETED | 이전 공정 미완료 | 400 |
| DUPLICATE_START | 이미 착공됨 (PASS 완료) | 409 |
| INVALID_PROCESS_SEQUENCE | 잘못된 공정 순서 | 400 |
| WORKER_NOT_FOUND | 작업자 ID 미등록 | 404 |
| PROCESS_ALREADY_PASSED | 이미 PASS 완료됨 | 409 |
| DUPLICATE_PASS_COMPLETE | 중복 PASS 완공 | 409 |
| PROCESS_NOT_STARTED | 아직 착공되지 않음 | 400 |
| INVALID_PROCESS_DATA | 데이터 검증 실패 | 400 |
| SERIAL_NOT_FOUND | 시리얼 번호 미발견 | 404 |
| PRINTER_NOT_FOUND | 프린터 ID 미등록 | 404 |
| PRINTER_NOT_CONNECTED | 프린터 연결 끊김 | 503 |
| PRINTER_OUT_OF_PAPER | 용지 부족 | 503 |

---

## 7. 데이터베이스 필드 매핑

### 7.1 lots 테이블 업데이트

착공/완공 시 업데이트되는 필드:

| 필드 | 착공 시 | 완공 시 |
|------|---------|---------|
| status | IN_PROGRESS | COMPLETED (마지막 공정 시) |
| current_process | 현재 공정 번호 | 다음 공정 번호 |
| updated_at | 현재 시간 | 현재 시간 |

### 7.2 process_results 테이블

| 필드 | 설명 |
|------|------|
| lot_id | LOT FK |
| process_id | 공정 ID |
| result | PASS/FAIL |
| process_data | JSONB (공정별 데이터) |
| started_at | 착공 시간 |
| completed_at | 완공 시간 |
| worker_id | 작업자 ID |
| equipment_id | 장비 ID |

---

## 8. 현재 구현 상태

### 8.1 구현된 기능 (production_tracker_app)

1. **공정 설정** (`utils/config.py`):
   - 8개 공정 모두 지원 (`process_number` 속성)
   - `PROCESS_NAMES` 딕셔너리에 공정명 정의
   - `PROC-NNN` 형식으로 process_id 생성

2. **착공 처리** (`services/work_service.py`):
   - `/api/v1/process/start`로 POST 전송
   - 포함: lot_number, line_id, process_id, process_name, equipment_id, worker_id, start_time

3. **완공 처리** (`services/work_service.py`):
   - `/api/v1/process/complete`로 POST 전송
   - 외부 앱에서 받은 전체 JSON 데이터 전달

4. **파일 감시** (`services/completion_watcher.py`):
   - `C:/neurohub_work/pending/` 폴더에서 JSON 파일 모니터링
   - process_id로 파일 매칭
   - 완료된 파일은 `completed/` 폴더로 이동
   - 오류 파일은 `error/` 폴더로 이동

5. **프린터 지원** (`services/print_service.py`, `utils/config.py`):
   - 프린터 큐 설정
   - ZPL 템플릿 경로 설정
   - 공정 7 (라벨 프린팅) 특수 처리

### 8.2 미구현 / 갭

1. **공정별 검증**: 현재 앱은 공정별 필수 필드 검증 없이 JSON을 그대로 전달

2. **펌웨어 동기화**: 공정 4용 펌웨어 다운로드/버전 확인 미구현

3. **라벨 인쇄 연동**: 프린터 설정은 있으나 시리얼 라벨용 실제 ZPL 생성/인쇄 구현 필요

4. **불량 유형 코드 강제**: 각 공정에 정의된 코드와 defect_type 일치 검증 없음

---

## 9. 파일 명명 규칙

### 완공 JSON 파일

**형식**: `{LOT_NUMBER}_{PROCESS_ID}_{TIMESTAMP}.json`

**예시**: `PSA10-KR-251110D-001_PROC-003_20251110090000.json`

---

## 10. 구현 체크리스트

Production Tracker App에서 착완공 시스템을 완전히 구현하기 위한 체크리스트:

### 착공 구현
- [ ] LOT 바코드 스캔 UI
- [ ] 이전 공정 완료 상태 확인
- [ ] 착공 API 호출 및 응답 처리
- [ ] 에러 처리 및 사용자 알림

### 완공 구현
- [ ] 공정별 데이터 입력 UI (또는 외부 앱 연동)
- [ ] 공정별 필수 필드 검증
- [ ] 완공 API 호출 및 응답 처리
- [ ] 파일 감시 기반 완공 처리
- [ ] 에러 처리 및 재시도 로직

### 공정별 특수 처리
- [ ] 공정 4: 펌웨어 다운로드 및 버전 관리
- [ ] 공정 7: 시리얼 번호 생성 및 라벨 인쇄
- [ ] 공정 6: 테스트 결과 배열 처리

### 품질 관리
- [ ] 불량 유형 코드 선택 UI
- [ ] 불량 설명 입력
- [ ] FAIL 시 재작업 플로우

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-11-19 | 1.0 | 초기 문서 작성 |
