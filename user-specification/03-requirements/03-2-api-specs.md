# 3.4 데이터 인터페이스 요구사항

[← 목차로 돌아가기](../../README.md)

---

## 3.4.0 API 버전 관리 전략

### 개요

본 MES 시스템의 API는 명확한 버전 관리 전략을 통해 하위 호환성을 보장하고, 안정적인 시스템 확장을 지원합니다.

### 버전 정책

**현재 버전:**
- **v1**: Phase 1 기본 버전 (현재)
- 모든 API 경로: `/api/v1/...`

**향후 버전 (계획):**
- **v2**: Phase 2 고도화 (AI 기능, ERP 연동, 고급 분석)
- **v3**: 향후 확장 (글로벌 다국어, 다중 공장 지원 등)

**버전 수명 주기:**
- 신규 버전 출시 후 **이전 버전 최소 1년 유지**
- 폐기 예정 버전은 **6개월 전 사전 공지**
- 폐기 예정 버전 API 호출 시 응답 헤더에 `X-API-Deprecated: true` 포함

### 하위 호환성 보장 원칙

**DO (허용):**
- ✅ 선택적(optional) 필드 추가
- ✅ 새로운 API 엔드포인트 추가
- ✅ 새로운 열거형(enum) 값 추가
- ✅ 응답 필드 추가 (기존 필드 유지)

**DON'T (금지 - 새 버전 필요):**
- ❌ 필수(required) 필드 추가
- ❌ 기존 필드 제거
- ❌ 필드 타입 변경 (예: string → integer)
- ❌ 필드 이름 변경
- ❌ 기존 열거형(enum) 값 제거
- ❌ 에러 응답 형식 변경

### 버전 전환 예시

**v1 API (현재):**
```http
POST /api/v1/process/start
Content-Type: application/json

{
  "lot_number": "WF-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-002",
  "worker_id": "W001"
}
```

**v2 API (Phase 2 계획):**
```http
POST /api/v2/process/start
Content-Type: application/json

{
  "lot_number": "WF-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-002",
  "worker_id": "W001",
  "worker_rfid": "1234-5678-9ABC",  // 새 필드 추가
  "start_mode": "auto"                // 새 필드 추가
}
```

**v1과 v2 동시 지원:**
```
v1 API: /api/v1/process/start (기존 필드만)
v2 API: /api/v2/process/start (신규 필드 포함)

→ v1 호출 시에도 정상 동작 (신규 필드는 기본값 사용)
→ 1년 동안 v1, v2 모두 지원
```

### 외부 앱 대응 (File Watcher)

외부 공정 앱은 File Watcher 방식으로 연동되므로, JSON 스키마 버전 필드를 사용합니다.

**v1 스키마 (현재):**
```json
{
  "schema_version": "1.0",
  "lot_number": "WF-KR-251110D-001",
  "process_id": "PROC-003",
  "process_data": {
    "temp_sensor": { "measured_temp": 60.2, "result": "PASS" }
  }
}
```

**v2 스키마 (향후):**
```json
{
  "schema_version": "2.0",
  "lot_number": "WF-KR-251110D-001",
  "process_id": "PROC-003",
  "process_data": {
    "temp_sensor": {
      "measured_temp": 60.2,
      "result": "PASS",
      "measurement_unit": "celsius"  // 새 필드
    },
    "ai_prediction": { ... }  // AI 기능 추가
  }
}
```

**백엔드 처리 로직:**
```python
# backend/app/api/v1/endpoints/process.py
def process_complete_data(data: dict):
    schema_version = data.get("schema_version", "1.0")

    if schema_version == "1.0":
        # v1 스키마 처리
        return process_v1_schema(data)
    elif schema_version == "2.0":
        # v2 스키마 처리 (Phase 2)
        return process_v2_schema(data)
    else:
        raise ValueError(f"Unsupported schema version: {schema_version}")
```

### Content Negotiation (선택사항)

향후 `Accept` 헤더를 통한 버전 협상도 지원 가능:

```http
GET /api/lots/WF-KR-251110D-001
Accept: application/vnd.mes.v1+json

→ v1 형식 응답

GET /api/lots/WF-KR-251110D-001
Accept: application/vnd.mes.v2+json

→ v2 형식 응답
```

### 폐기 프로세스

**1. 폐기 예정 공지 (D-180일)**
- API 문서에 `DEPRECATED` 표시
- 응답 헤더에 `X-API-Deprecated: true` 추가
- 응답 헤더에 `X-API-Sunset: 2026-01-01` (폐기 예정일) 추가

**2. 폐기 경고 (D-90일)**
- 이메일 공지 (모든 개발자)
- 대시보드 경고 메시지 표시

**3. 폐기 실행 (D-day)**
- API 요청 시 `410 Gone` 응답 반환
```json
{
  "error": {
    "code": "API_DEPRECATED",
    "message": "This API version has been deprecated. Please use /api/v2/...",
    "migration_guide": "https://docs.mes.com/api/v1-to-v2-migration"
  }
}
```

### API 문서 자동 생성

FastAPI의 자동 문서 생성 기능을 활용:

```
v1 API 문서: https://mes-api.com/docs/v1
v2 API 문서: https://mes-api.com/docs/v2
```

각 버전별 Swagger UI 및 ReDoc 제공

---

## 3.4.1 착공 인터페이스

**개요:** 현장 작업자가 프론트엔드 앱에서 LOT 바코드를 스캔하여 공정 착공을 등록하는 인터페이스

**통신 방식:** HTTP REST API (프론트엔드 ↔ 백엔드)

**API 엔드포인트:** `POST /api/v1/process/start`

**요청 (Request) 스키마:**

```json
{
  "lot_number": "WF-KR-251110D-001",
  "line_id": "LINE-A",
  "process_id": "PROC-001",
  "process_name": "레이저 마킹",
  "equipment_id": "LASER-01",
  "worker_id": "W001",
  "start_time": "2025-01-10T09:00:00+09:00"
}
```

**필드 설명:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| lot_number | string | Y | LOT 번호 (바코드 스캔 값) |
| line_id | string | Y | 생산 라인 ID (LINE-A, LINE-B 등) |
| process_id | string | Y | 공정 ID (PROC-001 ~ PROC-008) |
| process_name | string | Y | 공정명 (한글) |
| equipment_id | string | Y | 설비/장비 ID (LASER-01, SENSOR-CHECK-01 등) |
| worker_id | string | Y | 작업자 ID |
| start_time | string | Y | 착공 시간 (ISO 8601) |

**응답 (Response) - 성공:**

```json
{
  "status": "success",
  "message": "착공이 등록되었습니다",
  "data": {
    "lot_number": "WF-KR-251110D-001",
    "line_id": "LINE-A",
    "process_id": "PROC-001",
    "process_name": "레이저 마킹",
    "equipment_id": "LASER-01",
    "worker_id": "W001",
    "start_time": "2025-01-10T09:00:00+09:00",
    "work_order_id": "WO-20250110-001",
    "sequence_number": 1
  }
}
```

**응답 (Response) - 실패:**

```json
{
  "status": "error",
  "message": "이전 공정이 완료되지 않았습니다",
  "error_code": "PREVIOUS_PROCESS_NOT_COMPLETED",
  "data": {
    "lot_number": "WF-KR-251110D-001",
    "current_process": "센서 검사",
    "previous_process": "LMA 조립",
    "required_action": "LMA 조립 공정을 먼저 완료해주세요"
  }
}
```

**주요 에러 코드:** [2.8 API 에러 코드 체계](../02-product-process.md#28-api-에러-코드-체계) 참조

## 3.4.2 완공 데이터 인터페이스

**개요:** 외부 공정 앱에서 공정 작업 완료 후 완공 데이터를 MES 백엔드로 전송하는 인터페이스

**통신 방식:** JSON 파일 기반 (File Watcher)

> **중요:** 외부 업체가 개발한 공정 앱은 소스 코드 접근이 불가능하므로 JSON 파일 기반 연동만 가능합니다.

**배경:**
- 외부 업체가 개발한 공정 앱 (레이저 마킹, 센서 검사, 성능검사 등)
- 소스 코드 접근 불가, API 연동 불가
- 파일 기반 데이터 교환 방식 채택

**데이터 전송 프로세스:**

1. 외부 공정 앱이 작업 완료 후 JSON 파일 생성
2. 지정된 디렉토리에 파일 저장: `C:\neurohub_work\pending\`
3. **프론트엔드 앱(PyQt5)의 File Watcher**가 파일 감지
4. 프론트엔드가 JSON 파일을 읽고 HTTP POST로 백엔드에 전송
5. 백엔드가 완공 데이터 파싱, 검증 및 데이터베이스 저장
6. 프론트엔드가 처리 완료 파일을 `C:\neurohub_work\completed\`로 이동
   - 전송 실패 시: `C:\neurohub_work\error\`로 이동하고 오류 로그 생성

**기본 JSON 스키마:**

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
    "공정별 데이터 (아래 참조)": "..."
  }
}
```

**필드 설명:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| lot_number | string | Y | LOT 번호 (예: WF-KR-251110D-001, 상세는 [2.6.1 LOT 번호 체계](../02-product-process.md#261-lot-번호-체계) 참조) |
| line_id | string | Y | 생산 라인 ID (LINE-A, LINE-B 등) |
| process_id | string | Y | 공정 ID (PROC-001 ~ PROC-008) |
| process_name | string | Y | 공정명 (한글) |
| equipment_id | string | Y | 설비/장비 ID (공정별 설비 식별자) |
| worker_id | string | Y | 작업자 ID |
| start_time | string | Y | 착공 시간 (ISO 8601) |
| complete_time | string | Y | 완공 시간 (ISO 8601) |
| process_data | object | Y | 공정별 측정/검사 데이터 (아래 참조) |

**공정별 process_data 상세 스키마:**

### 공정 1: 레이저 마킹

```json
{
  "process_data": {
    "lot_number_engraved": "WF-KR-251110D-001",
    "marking_result": "SUCCESS"
  }
}
```

### 공정 2: LMA 조립

**PASS 예시:**
```json
{
  "result": "PASS",
  "process_data": {
    "sma_spring_lot": "SPRING-2025011001",
    "busbar_lot": "BUSBAR-2025011001",
    "assembly_time": 55,
    "visual_inspection": "PASS"
  }
}
```

**FAIL 예시 (작업자 판단):**
```json
{
  "result": "FAIL",
  "process_data": {
    "sma_spring_lot": "SPRING-2025011001",
    "busbar_lot": "BUSBAR-2025011001",
    "assembly_time": 45,
    "visual_inspection": "FAIL",
    "defect_type": "PART_DEFECT",
    "defect_part": "SMA 스프링",
    "defect_description": "스프링 변형 발견"
  }
}
```

### 공정 3: 센서 검사

**PASS 예시:**
```json
{
  "result": "PASS",
  "process_data": {
    "temp_sensor": {
      "measured_temp": 60.2,
      "target_temp": 60.0,
      "tolerance": 1.0,
      "result": "PASS"
    },
    "tof_sensor": {
      "i2c_communication": true,
      "result": "PASS"
    }
  }
}
```

**FAIL 예시 (자동 검사):**
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
    "defect_type": "SENSOR_TEMP_FAIL",
    "defect_description": "온도 센서 측정값 범위 초과 (58.0℃, 허용범위: 59-61℃)"
  }
}
```

### 공정 4: 펌웨어 업로드

```json
{
  "process_data": {
    "firmware_version": "v1.2.3",
    "upload_result": "SUCCESS"
  }
}
```

### 공정 6: 성능검사

```json
{
  "process_data": {
    "test_results": [
      {
        "test_point_id": "T38_P170",
        "temperature": 38,
        "displacement": 170,
        "measured_force": 12.5,
        "spec": {
          "target_force": 12.8,
          "tolerance": 1.0
        },
        "result": "PASS"
      },
      {
        "test_point_id": "T50_P180",
        "temperature": 50,
        "displacement": 180,
        "measured_force": 14.2,
        "spec": {
          "target_force": 14.5,
          "tolerance": 1.0
        },
        "result": "PASS"
      },
      {
        "test_point_id": "T52_P200",
        "temperature": 52,
        "displacement": 200,
        "measured_force": 15.8,
        "spec": {
          "target_force": 16.0,
          "tolerance": 1.0
        },
        "result": "PASS"
      }
    ],
    "overall_result": "PASS",
    "test_duration_seconds": 45,
    "tested_at": "2025-01-10T11:00:00+09:00"
  }
}
```

### 공정 7: 라벨 프린팅

```json
{
  "process_data": {
    "label_printed": true,
    "printer_id": "PRINTER-07",
    "print_time": "2025-01-10T14:30:00+09:00",
    "barcode_verified": true
  }
}
```

### 공정 8: 포장 + 외관검사

```json
{
  "process_data": {
    "inspection_result": "PASS"
  }
}
```

**참고:** 향후 포장 라벨 출력이 필요한 경우 `packaging_label_printed`, `packaging_printer_id` 등의 필드를 추가할 수 있습니다.

**파일명 규칙:**

- 형식: `{LOT_NUMBER}_{PROCESS_ID}_{TIMESTAMP}.json`
- 예시: `WF-KR-251110D-001_PROC-003_20250110090000.json`

**처리 결과:**

- 성공: 파일을 `C:\neurohub_work\completed\`로 이동
- 실패: 파일을 `C:\neurohub_work\error\`로 이동하고 오류 로그 생성

**주요 에러 코드:** [2.8 API 에러 코드 체계](../02-product-process.md#28-api-에러-코드-체계) 참조

**공정별 필수 데이터 및 검증 규칙:**

| 공정 | 필수 필드 | 데이터 타입 | 검증 규칙 | 비고 |
|------|----------|------------|----------|------|
| **레이저 마킹** | marking_result | string | "PASS" or "FAIL" | 마킹 품질 검사 |
| **LMA 조립** | assembly_time | number | > 0 (분) | 조립 소요 시간 |
| | 모선_lot | string | 형식: MS-YYYY-nnn | 사용된 모선 LOT 번호 |
| | visual_inspection | string | "PASS" or "FAIL" | 육안 검사 결과 |
| **센서 검사** | temp_sensor.measured_temp | number | 59.0 ~ 61.0 (℃) | 온도 센서 측정값 |
| | temp_sensor.result | string | "PASS" or "FAIL" | 온도 센서 검사 결과 |
| | tof_sensor.communication | string | "OK" or "FAIL" | TOF I2C 통신 확인 |
| | tof_sensor.result | string | "PASS" or "FAIL" | TOF 센서 검사 결과 |
| | overall_result | string | "PASS" or "FAIL" | **필수** 전체 검사 결과 |
| **펌웨어 업로드** | firmware_version | string | 형식: v1.2.3 | 업로드된 펌웨어 버전 |
| | upload_result | string | "SUCCESS" or "FAIL" | 업로드 성공 여부 |
| | board_serial | string | 길이 > 0 | MCU 보드 시리얼 |
| **로봇 조립** | assembly_time | number | > 0 (분) | 조립 소요 시간 |
| | cable_connection | string | "OK" or "FAIL" | 케이블 연결 확인 |
| | final_visual_check | string | "PASS" or "FAIL" | 최종 육안 검사 |
| **성능검사** | test_results | array | length > 0 | 측정 데이터 배열 |
| | test_results[].temperature | number | 40 ~ 70 (℃) | 측정 온도 |
| | test_results[].displacement | number | 0 ~ 250 (mm) | 측정 변위 |
| | test_results[].force | number | 0 ~ 30 (kgf) | 측정 힘 |
| | overall_result | string | "PASS" or "FAIL" | **필수** 전체 검사 결과 |
| **라벨 프린팅** | serial_number | string | 형식: WF-KR-YYMMDDX-nnn-nnnn | 생성된 시리얼 번호 |
| | label_printed | boolean | true | 라벨 출력 확인 |
| | printer_id | string | 길이 > 0 | 사용된 프린터 ID |
| **포장+외관검사** | visual_defects | array | - | 발견된 결함 목록 (빈 배열 가능) |
| | defects[].type | string | "scratch", "dirt", "dent" 등 | 결함 유형 |
| | defects[].severity | string | "minor", "major", "critical" | 결함 심각도 |
| | packaging_complete | boolean | true | 포장 완료 확인 |
| | final_result | string | "PASS" or "FAIL" | **필수** 최종 검사 결과 |

> **중요:** `overall_result` 또는 `final_result` 필드는 각 공정의 합격/불합격 판정에 필수입니다. 이 값이 "FAIL"인 경우 해당 제품은 불량으로 표시됩니다.

> **참고:** JSONB 필드 검증은 백엔드 API에서 JSON Schema 또는 Pydantic 모델을 사용하여 수행됩니다.

## 3.4.3 라벨 출력 인터페이스

**개요:** LOT 바코드 라벨 및 시리얼 번호 바코드 라벨을 산업용 프린터로 출력하는 인터페이스

**통신 방식:** 직렬 통신 (Serial) 또는 네트워크 (TCP/IP)

**지원 프린터:**

- Zebra ZT series

**출력 대상:**

| 라벨 종류 | 출력 시점 | 포함 정보 | 관련 요구사항 |
|-----------|-----------|-----------|---------------|
| LOT 바코드 라벨 | LOT 생성 직후 | LOT 번호, 제품명, 생성일, 목표 수량 | FR-LOT-002 |
| 시리얼 번호 바코드 라벨 | Label Printing 공정 착공 시 | 시리얼 번호, LOT 번호, 제품명, 생성일 | FR-SN-002 |

**라벨 출력 요청 API:**

**API 엔드포인트:** `POST /api/v1/label/print`

**요청 (Request) - LOT 라벨:**

```json
{
  "label_type": "LOT",
  "lot_number": "WF-KR-251110D-001",
  "product_model": "Withforce",
  "target_quantity": 100,
  "created_date": "2025-01-10",
  "printer_id": "PRINTER-01"
}
```

**요청 (Request) - 시리얼 라벨:**

```json
{
  "label_type": "SERIAL",
  "serial_number": "WF-KR-251110D-001-0001",
  "lot_number": "WF-KR-251110D-001",
  "product_model": "Withforce",
  "created_date": "2025-01-10",
  "printer_id": "PRINTER-07"
}
```

**응답 (Response) - 성공:**

```json
{
  "status": "success",
  "message": "라벨이 출력되었습니다",
  "data": {
    "label_type": "SERIAL",
    "serial_number": "WF-KR-251110D-001-0001",
    "printer_id": "PRINTER-07",
    "print_time": "2025-01-10T14:30:00+09:00"
  }
}
```

**응답 (Response) - 실패:**

```json
{
  "status": "error",
  "message": "프린터 연결 실패",
  "error_code": "PRINTER_NOT_CONNECTED",
  "data": {
    "printer_id": "PRINTER-07",
    "printer_status": "offline"
  }
}
```

**주요 에러 코드:** [2.8 API 에러 코드 체계](../02-product-process.md#28-api-에러-코드-체계) 참조

## 3.4.4 펌웨어 배포 인터페이스

**개요:** 공정 4 (펌웨어 업로드) 착공 시 최신 펌웨어를 백엔드에서 프론트엔드로 배포하고, 외부 로컬 앱이 제어 보드에 업로드하는 인터페이스

**배경:**
- 펌웨어는 백엔드 서버에서 중앙 관리
- 버전 불일치 방지를 위한 동기화 메커니즘 필요
- 로컬 앱이 항상 최신 펌웨어만 사용하도록 보장

**디렉토리 구조:**

```
C:\neurohub_work\firmware\
  ├── firmware_v1.2.3.bin      (펌웨어 바이너리 파일)
  └── firmware_meta.json       (메타데이터 파일)
```

**펌웨어 동기화 프로세스:**

1. **착공 시 버전 확인 (프론트엔드)**
   - 공정 4 착공 API 호출: `POST /api/v1/process/start`
   - 착공 완료 후 프론트엔드가 펌웨어 정보 조회 API 호출 (폴링)
   - **폴링 설정:**
     - API 엔드포인트: `GET /api/v1/firmware/latest`
     - 폴링 주기: 2초
     - 최대 재시도: 5회 (총 10초)
     - 타임아웃 후 작업자에게 오류 알림 및 수동 재시도 안내
   - 프론트엔드가 로컬 `firmware_meta.json`과 비교

2. **펌웨어 다운로드 (버전 불일치 시)**
   - 기존 `.bin` 파일 삭제
   - 백엔드에서 최신 펌웨어 다운로드: `GET /api/v1/firmware/download/{version}`
   - **다운로드 재시도:**
     - 최대 재시도: 3회
     - 재시도 간격: 2초, 4초, 8초 (exponential backoff)
     - 실패 시 오류 로그 기록 및 작업자 알림
   - 새 펌웨어 파일 저장: `firmware_v{version}.bin`
   - `firmware_meta.json` 업데이트

3. **로컬 앱 펌웨어 업로드**
   - 로컬 앱이 `firmware_meta.json` 감시 (File Watcher)
   - 파일 변경 감지 시 메타데이터 읽기
   - `filename`에 지정된 `.bin` 파일 존재 확인
   - MD5 해시 검증
   - 제어 보드에 펌웨어 업로드

4. **완공 보고**
   - 업로드 결과를 JSON 파일로 생성
   - 프론트엔드가 백엔드로 완공 보고: `POST /api/v1/process/complete`

**펌웨어 정보 조회 API:**

**API 엔드포인트:** `GET /api/v1/firmware/latest`

**요청 예시:**

```
GET /api/v1/firmware/latest
Authorization: Bearer {JWT_TOKEN}
```

**응답:**

```json
{
  "status": "success",
  "data": {
    "version": "v1.2.3",
    "filename": "firmware_v1.2.3.bin",
    "file_size": 65536,
    "md5_hash": "5d41402abc4b2a76b9719d911017c592",
    "download_url": "/api/v1/firmware/download/v1.2.3",
    "release_date": "2025-01-10T09:00:00+09:00"
  }
}
```

**펌웨어 다운로드 API:**

**API 엔드포인트:** `GET /api/v1/firmware/download/{version}`

**요청 예시:**

```
GET /api/v1/firmware/download/v1.2.3
Authorization: Bearer {JWT_TOKEN}
```

**응답:**
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename="firmware_v1.2.3.bin"`
- Binary file stream

**firmware_meta.json 스키마:**

```json
{
  "version": "v1.2.3",
  "filename": "firmware_v1.2.3.bin",
  "file_size": 65536,
  "md5_hash": "5d41402abc4b2a76b9719d911017c592",
  "downloaded_at": "2025-01-10T10:00:15+09:00",
  "status": "READY",
  "target_mcu": "STM32F103"
}
```

**필드 설명:**

| 필드 | 타입 | 설명 |
|------|------|------|
| version | string | 펌웨어 버전 (예: v1.2.3) |
| filename | string | 펌웨어 파일명 |
| file_size | integer | 파일 크기 (bytes) |
| md5_hash | string | MD5 체크섬 (무결성 검증용) |
| downloaded_at | string | 다운로드 완료 시간 (ISO 8601) |
| status | string | 상태 (READY, UPLOADING, UPLOADED, ERROR) |
| target_mcu | string | 대상 MCU 정보 |

**로컬 앱 연동 가이드:**

로컬 앱은 다음 로직을 구현해야 합니다:

1. **파일 감시**: `firmware_meta.json` 변경 감지
2. **메타데이터 읽기**: JSON 파싱
3. **파일 검증**:
   - `filename` 필드의 파일 존재 확인
   - MD5 해시 계산 및 `md5_hash`와 비교
4. **펌웨어 업로드**:
   - 제어 보드에 시리얼/USB로 업로드
   - `status`를 "UPLOADING"으로 업데이트 (선택사항)
5. **결과 보고**: 완공 JSON 파일 생성

**완공 데이터 (공정 4: 펌웨어 업로드) 업데이트:**

```json
{
  "process_data": {
    "firmware_version": "v1.2.3",
    "upload_result": "SUCCESS"
  }
}
```

**에러 처리:**

| 상황 | 처리 방법 |
|------|-----------|
| 다운로드 실패 | 프론트엔드가 재시도 (최대 3회), 실패 시 작업자에게 알림 |
| MD5 불일치 | 로컬 앱이 펌웨어 업로드 중단, 완공 JSON에 오류 기록 |
| 업로드 실패 | 로컬 앱이 재시도 (최대 3회), 완공 JSON에 실패 기록 |
| 구버전 펌웨어 감지 | 프론트엔드가 자동으로 최신 버전 다운로드 |

## 3.4.5 알림 조회 인터페이스

**개요:** 생산 과정에서 발생하는 이벤트(불량 발생, 목표 미달, 공정 지연 등)를 관리자 및 작업자에게 알리기 위한 알림 조회 인터페이스

**통신 방식:** REST API (폴링 기반)

**알림 유형:**

| 알림 유형 코드 | 설명 | 심각도 | 발생 조건 |
|--------------|------|--------|----------|
| DEFECT_DETECTED | 불량 발생 | HIGH | 공정 완공 시 FAIL 발생 |
| TARGET_NOT_MET | 생산 목표 미달 | MEDIUM | 일일 생산량이 목표의 80% 미만 |
| PROCESS_DELAYED | 공정 지연 | MEDIUM | 착공 후 예상 시간의 150% 초과 |
| LOT_COMPLETED | LOT 완료 | LOW | 전체 공정 완료 시 |
| FIRMWARE_UPDATE | 펌웨어 업데이트 | LOW | 새 펌웨어 버전 등록 시 |

**알림 조회 API:**

**API 엔드포인트:** `GET /api/v1/alerts`

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| status | string | N | unread | 알림 상태 (unread, read, all) |
| severity | string | N | all | 심각도 필터 (high, medium, low, all) |
| limit | number | N | 10 | 조회 개수 (최대 100) |
| offset | number | N | 0 | 페이징 오프셋 |
| start_date | string | N | - | 조회 시작일 (ISO 8601) |
| end_date | string | N | - | 조회 종료일 (ISO 8601) |

**요청 예시:**

```
GET /api/v1/alerts?status=unread&severity=high&limit=10
Authorization: Bearer {JWT_TOKEN}
```

**응답:**

```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "alert_id": "ALT-20250110-001",
        "alert_type": "DEFECT_DETECTED",
        "severity": "high",
        "title": "불량 발생",
        "message": "LOT-WF-KR-251110D-001, 공정 3 (센서 검사)에서 불량 발생",
        "related_lot": "WF-KR-251110D-001",
        "related_process": "PROC-003",
        "created_at": "2025-01-10T09:30:00+09:00",
        "is_read": false
      },
      {
        "alert_id": "ALT-20250110-002",
        "alert_type": "PROCESS_DELAYED",
        "severity": "medium",
        "title": "공정 지연",
        "message": "LOT-WF-KR-251110D-002, 공정 5 (로봇 조립)이 예상 시간 초과",
        "related_lot": "WF-KR-251110D-002",
        "related_process": "PROC-005",
        "created_at": "2025-01-10T09:25:00+09:00",
        "is_read": false
      }
    ],
    "total": 25,
    "unread_count": 12,
    "limit": 10,
    "offset": 0
  }
}
```

**알림 읽음 처리 API:**

**API 엔드포인트:** `PUT /api/v1/alerts/{alert_id}/read`

**요청 예시:**

```
PUT /api/v1/alerts/ALT-20250110-001/read
Authorization: Bearer {JWT_TOKEN}
```

**응답:**

```json
{
  "status": "success",
  "message": "알림이 읽음 처리되었습니다",
  "data": {
    "alert_id": "ALT-20250110-001",
    "is_read": true,
    "read_at": "2025-01-10T09:35:00+09:00"
  }
}
```

**폴링 권장 주기:**
- 관리자 대시보드: 30초
- 작업자 화면: 60초
- 심각도 HIGH 알림 발생 시: 10초로 일시 단축 (5분간)

**에러 코드:** [2.8 API 에러 코드 체계](../02-product-process.md#28-api-에러-코드-체계) 참조

---

**이전 섹션:** [3.1-3.3 기능 요구사항](03-1-functional.md)
**다음 섹션:** [3.5 기능 검수 항목](03-3-acceptance.md)
