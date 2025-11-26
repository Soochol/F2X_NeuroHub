# 3.5 기능 검수 항목

[← 목차로 돌아가기](../../README.md)

이 섹션은 MES 시스템의 각 기능 요구사항이 올바르게 구현되었는지 검증하기 위한 인수 검수(Acceptance Test) 항목을 정의합니다.


## 3.5.1 LOT 관리 검수

| 검수 ID | 검수 항목 | 검수 기준 | 검수 방법 |
|---------|----------|----------|----------|
| TC-LOT-001 | LOT 생성 기능 | 관리자 대시보드에서 LOT 생성 시 형식 준수 (`WF-KR-YYMMDD{D/N}-XXX`) | 대시보드에서 LOT 생성 후 데이터베이스 확인 |
| TC-LOT-002 | LOT 번호 자동 발급 | 당일 순번이 자동으로 증가 (001, 002, ...) | 동일 날짜에 여러 LOT 생성 후 순번 확인 |
| TC-LOT-003 | LOT 라벨 출력 | LOT 생성 시 바코드 라벨 자동 출력 성공 | Zebra 프린터로 라벨 출력 확인 |
| TC-LOT-004 | 중복 LOT 방지 | 동일한 LOT 번호를 재생성 시도 시 오류 반환 | 동일 LOT 번호로 생성 시도 후 오류 메시지 확인 |
| TC-LOT-005 | LOT 상태 관리 | LOT 생성 시 CREATED 상태, 모든 공정 완료 시 COMPLETED | 각 상태 변경 시점에 DB 확인 |
| TC-LOT-006 | LOT 조회 기능 | 대시보드에서 LOT 번호로 상세 정보 조회 가능 | LOT 검색 후 기본 정보 및 공정 현황 표시 확인 |


## 3.5.2 시리얼 번호 관리 검수

| 검수 ID | 검수 항목 | 검수 기준 | 검수 방법 |
|---------|----------|----------|----------|
| TC-SN-001 | 시리얼 번호 생성 | 라벨 프린팅 공정 착공 시 자동 생성, 형식 준수 (`WF-KR-YYMMDD{D/N}-XXX-YYYY`) | 라벨 프린팅 착공 후 DB에서 시리얼 번호 확인 |
| TC-SN-002 | 시리얼 순차 발급 | LOT당 0001부터 순차 증가 | 동일 LOT 내 여러 제품의 시리얼 번호 확인 |
| TC-SN-003 | 시리얼 라벨 출력 | 시리얼 번호 생성 시 바코드 라벨 자동 출력 | Zebra 프린터로 라벨 출력 및 내용 확인 |
| TC-SN-004 | 라벨 재출력 기능 | 라벨 손상/분실 시 재출력 가능, 이력 기록됨 | 재출력 요청 후 이력 테이블 확인 (사유, 작업자, 시간) |
| TC-SN-005 | 시리얼 중복 방지 | 동일 시리얼 번호 재발급 불가 | 동일 시리얼 생성 시도 시 오류 확인 |


## 3.5.3 WIP Item 관리 테스트

### TC-WIP-001: WIP Item 생성 (공정 1)

**목적**: LOT에서 WIP Item 생성 기능 검증

**전제조건**:
- LOT가 CREATED 상태로 존재
- LOT 번호: KR01PSA2511
- 생성 수량: 5개

**테스트 단계**:
1. POST `/api/v1/lots/{lot_id}/start-wip-generation?quantity=5` 호출
2. 응답에서 5개 WIP Item 확인
3. WIP ID 형식 검증: `WIP-KR01PSA2511-001` ~ `WIP-KR01PSA2511-005`
4. 각 WIP의 sequence_in_lot: 1~5 확인
5. 각 WIP의 상태: CREATED 확인
6. LOT 상태가 IN_PROGRESS로 변경되었는지 확인

**예상 결과**:
- HTTP 201 Created
- 5개 WIP Item이 순차적으로 생성됨
- WIP ID가 올바른 형식으로 생성됨
- LOT 상태가 IN_PROGRESS로 전환됨

**검증 쿼리**:
```sql
SELECT wip_id, sequence_in_lot, status
FROM wip_items
WHERE lot_id = {lot_id}
ORDER BY sequence_in_lot;
```

### TC-WIP-002: WIP 순번 연속성 테스트

**목적**: WIP 순번이 001부터 100까지 연속적으로 생성되는지 검증

**전제조건**:
- LOT가 CREATED 상태로 존재

**테스트 단계**:
1. POST `/api/v1/lots/{lot_id}/start-wip-generation?quantity=100` 호출
2. 100개 WIP Item 생성 확인
3. sequence_in_lot이 1~100 연속인지 확인
4. WIP ID가 001~100까지 순차적인지 확인
5. 추가 생성 시도 (101번째) → 400 Bad Request 확인

**예상 결과**:
- 100개까지 정상 생성
- 101번째 생성 시도는 실패 (BR-006 위반)
- 에러 메시지: "Maximum 100 WIPs per LOT exceeded"

### TC-WIP-003: WIP 바코드 스캔 (공정 2~6)

**목적**: WIP ID 바코드 스캔 기능 검증

**전제조건**:
- WIP Item이 생성되어 있음
- WIP ID: `WIP-KR01PSA2511-001`
- WIP 상태: IN_PROGRESS

**테스트 단계**:
1. POST `/api/v1/wip-items/WIP-KR01PSA2511-001/scan` 호출
2. WIP 상세 정보 응답 확인
3. 잘못된 형식 스캔: `INVALID-WIP-001` → 404 Not Found
4. 존재하지 않는 WIP: `WIP-KR01PSA2511-999` → 404 Not Found

**예상 결과**:
- 유효한 WIP ID: 정상 조회
- 무효한 형식: 404 오류
- 존재하지 않음: 404 오류

### TC-WIP-004: WIP 상태 전이

**목적**: WIP 상태 전이 규칙 검증

**상태 전이 테스트 케이스**:

| 현재 상태 | 공정 결과 | 예상 상태 | 설명 |
|----------|---------|---------|------|
| CREATED | 공정 1 PASS | IN_PROGRESS | 정상 전이 |
| IN_PROGRESS | 공정 2 PASS | IN_PROGRESS | 공정 진행 중 |
| IN_PROGRESS | 공정 6 PASS | COMPLETED | 모든 공정 완료 |
| IN_PROGRESS | 공정 3 FAIL | FAILED | 불량 발생 |
| IN_PROGRESS | 공정 4 REWORK | IN_PROGRESS | 재작업 허용 |

**검증 단계**:
1. 각 상태 전이에 대해 공정 완료 API 호출
2. 응답에서 상태 확인
3. 데이터베이스에서 상태 확인

### TC-WIP-005: WIP → Serial 전환 (공정 7)

**목적**: WIP를 Serial Number로 전환하는 기능 검증

**전제조건**:
- WIP ID: `WIP-KR01PSA2511-001`
- 공정 1~6 모두 PASS
- WIP 상태: COMPLETED
- sequence_in_lot: 1

**테스트 단계**:
1. POST `/api/v1/wip-items/WIP-KR01PSA2511-001/convert-to-serial` 호출
2. 응답에서 Serial Number 확인: `KR01PSA25110001`
3. WIP 상태가 CONVERTED로 변경되었는지 확인
4. WIP의 serial_id가 설정되었는지 확인
5. converted_at 타임스탬프 확인
6. Serial 상태가 CREATED인지 확인

**예상 결과**:
- HTTP 200 OK
- Serial Number 생성: `{LOT}{sequence:04d}` 형식
- WIP 상태: CONVERTED
- Serial과 WIP가 연결됨

**실패 케이스**:
- 공정 1~6 중 하나라도 미완료 → 400 Bad Request
- WIP 상태가 COMPLETED 아님 → 400 Bad Request
- 이미 전환된 WIP → 409 Conflict

### TC-WIP-006: REWORK 워크플로우

**목적**: REWORK 프로세스 검증

**시나리오**:
```
[WIP 생성] → [공정 1 PASS] → [공정 2 PASS] → [공정 3 FAIL + REWORK]
                                                         ↓
                              [공정 3 재실행] ← [상태: IN_PROGRESS]
                                      ↓
                              [공정 3 PASS] → [공정 4~6 진행]
```

**테스트 단계**:
1. 공정 3 완료 시 result: REWORK로 요청
2. WIP 상태 확인: IN_PROGRESS (FAILED 아님)
3. current_process_id 확인: null (재시작 가능)
4. 공정 3 재실행 가능 확인
5. 공정 3 PASS로 완료
6. 이후 공정 정상 진행 확인

**예상 결과**:
- REWORK 시 WIP 상태: IN_PROGRESS 유지
- 동일 공정 재실행 가능
- REWORK 횟수 제한 없음
- 최종 PASS 또는 FAIL로 완료 필요

### TC-WIP-007: WIP ID 고유성 검증

**목적**: WIP ID가 전역적으로 고유한지 검증

**테스트 단계**:
1. LOT A (KR01PSA2511)에서 WIP 생성: `WIP-KR01PSA2511-001`
2. LOT B (KR01PSA2512)에서 WIP 생성: `WIP-KR01PSA2512-001`
3. 두 WIP ID가 서로 다른지 확인
4. 데이터베이스 UNIQUE 제약 조건 확인

**검증 쿼리**:
```sql
SELECT COUNT(*) FROM wip_items WHERE wip_id = 'WIP-KR01PSA2511-001';
-- 결과: 1 (고유해야 함)
```

### TC-WIP-008: LOT당 최대 100개 제한

**목적**: LOT당 WIP 최대 개수 제한 검증 (BR-006)

**테스트 단계**:
1. LOT에서 100개 WIP 생성 성공 확인
2. 101번째 WIP 생성 시도 → 400 Bad Request
3. 에러 메시지 확인: "Maximum 100 WIPs per LOT"
4. 데이터베이스 CHECK 제약 조건 확인

**예상 결과**:
- 1~100: 정상 생성
- 101: 실패 (제약 조건 위반)


## 3.5.4 공정 관리 검수

| 검수 ID | 검수 항목 | 검수 기준 | 검수 방법 |
|---------|----------|----------|----------|
| TC-PROC-001 | 착공 등록 | LOT 바코드 스캔 시 착공 API 정상 호출 및 성공 응답 | 프론트엔드에서 바코드 스캔 후 HTTP 200 응답 확인 |
| TC-PROC-002 | 착공 검증 | 이전 공정 미완료 시 착공 불가, 적절한 오류 메시지 반환 | 공정 순서 위반 시도 후 에러 코드 확인 (`PREVIOUS_PROCESS_NOT_COMPLETED`) |
| TC-PROC-003 | 완공 등록 | JSON 파일 생성 시 백엔드가 자동 감지 및 처리 | File Watcher가 JSON 파일 감지, DB 저장 확인 |
| TC-PROC-004 | 완공 데이터 검증 | 공정별 필수 데이터 누락 시 오류 처리 | 필수 필드 누락 JSON 전송 후 오류 로그 확인 |
| TC-PROC-005 | 완공 파일 이동 | 처리 성공 시 `completed/`, 실패 시 `error/`로 이동 | 각 경우의 파일 이동 경로 확인 |
| TC-PROC-006 | 공정 순서 제어 | 정의된 순서대로만 진행 가능 | 순서 위반 시도 시 착공 차단 확인 |
| TC-PROC-007 | 작업자 기록 | 각 공정 착공/완공 시 작업자 ID 기록 | DB에서 작업자 정보 확인 |
| TC-PROC-008 | 시간 기록 | 착공/완공 시간 정확히 기록 | DB 타임스탬프와 실제 시간 비교 (오차 1초 이내) |


## 3.5.5 실시간 모니터링 검수

| 검수 ID | 검수 항목 | 검수 기준 | 검수 방법 |
|---------|----------|----------|----------|
| TC-DASH-001 | 금일 생산 현황 | 착공/완공/불량 수량 정확히 표시 | DB 집계값과 대시보드 표시값 비교 |
| TC-DASH-002 | LOT별 진행 상태 | 각 LOT의 현재 공정 및 진행률 표시 | 대시보드 표시값과 실제 DB 데이터 비교 |
| TC-DASH-003 | 대시보드 폴링 업데이트 | 10초 주기 폴링, 데이터 변경 시 10초 이내 반영 | 착공/완공 후 최대 10초 이내 대시보드 갱신 확인 |
| TC-DASH-004 | 대시보드 로딩 시간 | 초기 로드 시간 3초 이내 | 브라우저 개발자 도구로 로딩 시간 측정 |
| TC-DASH-005 | 알림 폴링 | 30초 주기로 알림 조회 API 호출 | 네트워크 탭에서 `/api/v1/alerts` 호출 주기 확인 |


## 3.5.6 추적성 검수

| 검수 ID | 검수 항목 | 검수 기준 | 검수 방법 |
|---------|----------|----------|----------|
| TC-TRACE-001 | LOT 이력 조회 | LOT 번호로 전체 공정 이력 조회 가능 | 대시보드에서 LOT 검색 후 8개 공정 이력 확인 |
| TC-TRACE-002 | 시리얼 이력 조회 | 시리얼 번호로 개별 제품의 상세 이력 조회 | 시리얼 검색 후 공정별 데이터 확인 |
| TC-TRACE-003 | 부품 LOT 추적 | 사용된 부품 LOT 정보 기록 및 조회 가능 | 조립 공정 데이터에서 부품 LOT 확인 (모선, 링크 등) |
| TC-TRACE-004 | 불량 추적 | 불량 발생 시 해당 공정 및 원인 추적 가능 | 불량 데이터 입력 후 이력 조회로 추적 |
| TC-TRACE-005 | 작업자 추적 | 각 공정 작업자 정보 조회 가능 | 이력 조회 시 작업자 ID 표시 확인 |
| TC-TRACE-006 | 데이터 무결성 | 모든 공정 데이터 누락 없이 저장 | 샘플 LOT의 전체 공정 데이터 완전성 확인 |


## 3.5.7 Given/When/Then 검수 시나리오

이 섹션은 주요 기능의 상세한 BDD(Behavior-Driven Development) 시나리오를 제공합니다.

### 시나리오 1: LOT 생성 및 라벨 출력

**참조:** TC-LOT-001, TC-LOT-002, TC-LOT-003

```gherkin
Feature: LOT 생성 및 라벨 출력
  As a 생산 관리자
  I want to LOT을 생성하고 바코드 라벨을 출력할 수 있어야
  So that 생산 추적을 시작할 수 있다

Scenario: 정상적인 LOT 생성
  Given 관리자 대시보드에 로그인되어 있고
    And 제품 모델 "NH-F2X-001"이 선택되어 있고
    And 오늘 날짜가 "2025-01-15"이고
    And 주간 교대(D)가 선택되어 있고
    And Zebra 프린터가 연결되어 있을 때
  When "LOT 생성" 버튼을 클릭하면
  Then LOT 번호 "WF-KR-250115D-001"이 생성되고
    And LOT 상태가 "CREATED"로 설정되고
    And 바코드 라벨이 자동으로 출력되고
    And 성공 메시지 "LOT이 생성되었습니다"가 표시된다

Scenario: 당일 두 번째 LOT 생성 (순번 증가)
  Given 오늘 날짜가 "2025-01-15"이고
    And 주간 교대(D)로 LOT "WF-KR-250115D-001"이 이미 생성되어 있을 때
  When "LOT 생성" 버튼을 클릭하면
  Then LOT 번호 "WF-KR-250115D-002"가 생성되고
    And 순번이 자동으로 증가하여 발급된다

Scenario: 중복 LOT 생성 방지
  Given LOT "WF-KR-250115D-001"이 이미 존재할 때
  When 동일한 조건으로 LOT을 재생성하려고 시도하면
  Then HTTP 409 Conflict 응답이 반환되고
    And 에러 메시지 "이미 존재하는 LOT 번호입니다"가 표시되고
    And 데이터베이스에 중복 레코드가 생성되지 않는다
```

### 시나리오 2: 공정 착공 및 순서 제어

**참조:** TC-PROC-001, TC-PROC-002, TC-PROC-006

```gherkin
Feature: 공정 착공 및 순서 제어
  As a 현장 작업자
  I want to 공정에 착공할 수 있어야
  So that 제품 생산을 진행할 수 있다

Scenario: 첫 번째 공정(라벨 프린팅) 정상 착공
  Given 프론트엔드 앱에 작업자 "USER001"로 로그인되어 있고
    And LOT "WF-KR-250115D-001"이 "CREATED" 상태로 존재하고
    And "라벨 프린팅" 공정(sequence=1)이 선택되어 있을 때
  When LOT 바코드 "WF-KR-250115D-001"을 스캔하면
  Then HTTP 201 Created 응답이 반환되고
    And 착공 시간이 기록되고
    And 작업자 "USER001"이 기록되고
    And LOT 상태가 "IN_PROGRESS"로 변경되고
    And 시리얼 번호 "WF-KR-250115D-001-0001"이 자동 생성되고
    And 시리얼 바코드 라벨이 출력된다

Scenario: 공정 순서 위반 차단
  Given 시리얼 "WF-KR-250115D-001-0001"이 존재하고
    And "라벨 프린팅" 공정(sequence=1)은 완료되지 않았고
    And "조립" 공정(sequence=2)이 선택되어 있을 때
  When 시리얼 바코드를 스캔하여 착공하려고 시도하면
  Then HTTP 400 Bad Request 응답이 반환되고
    And 에러 코드 "PREVIOUS_PROCESS_NOT_COMPLETED"가 반환되고
    And 에러 메시지 "이전 공정(라벨 프린팅)이 완료되지 않았습니다"가 표시되고
    And 착공이 차단된다

Scenario: 이전 공정 PASS 완료 후 정상 착공
  Given 시리얼 "WF-KR-250115D-001-0001"이 존재하고
    And "라벨 프린팅" 공정(sequence=1)이 "PASS"로 완료되었고
    And "조립" 공정(sequence=2)이 선택되어 있을 때
  When 시리얼 바코드를 스캔하면
  Then HTTP 201 Created 응답이 반환되고
    And "조립" 공정 착공이 정상 등록되고
    And 착공 시간과 작업자가 기록된다
```

### 시나리오 3: 공정 완공 및 File Watcher

**참조:** TC-PROC-003, TC-PROC-004, TC-PROC-005

```gherkin
Feature: 공정 완공 데이터 수집
  As a 외부 검사 장비
  I want to 완공 데이터를 JSON 파일로 전달할 수 있어야
  So that MES가 자동으로 데이터를 수집할 수 있다

Scenario: 정상적인 완공 데이터 처리
  Given File Watcher가 "C:/mes/pending/" 폴더를 감시 중이고
    And 시리얼 "WF-KR-250115D-001-0001"이 "조립" 공정에 착공되어 있을 때
  When 다음 JSON 파일이 pending 폴더에 생성되면:
    """
    {
      "schema_version": "1.0",
      "serial_number": "WF-KR-250115D-001-0001",
      "process_id": "PROC-002",
      "result": "PASS",
      "measured_data": {
        "온도": 60.5,
        "변위": 198.3,
        "힘": 15.2,
        "모선_lot": "MS-2025-100"
      },
      "timestamp": "2025-01-15T14:30:00Z"
    }
    """
  Then File Watcher가 파일을 5초 이내에 감지하고
    And 백엔드가 JSON을 파싱하여 DB에 저장하고
    And process_data 테이블에 완공 데이터가 기록되고
    And 시리얼 상태가 "IN_PROGRESS"로 업데이트되고
    And JSON 파일이 "C:/mes/completed/" 폴더로 이동된다

Scenario: 필수 필드 누락 시 오류 처리
  Given File Watcher가 "C:/mes/pending/" 폴더를 감시 중일 때
  When 다음과 같이 serial_number가 누락된 JSON 파일이 생성되면:
    """
    {
      "schema_version": "1.0",
      "process_id": "PROC-002",
      "result": "PASS",
      "timestamp": "2025-01-15T14:30:00Z"
    }
    """
  Then File Watcher가 파일을 감지하고
    And 백엔드가 검증 오류를 로그에 기록하고
    And JSON 파일이 "C:/mes/error/" 폴더로 이동되고
    And 에러 로그에 "필수 필드 누락: serial_number"가 기록된다

Scenario: 불합격 데이터 처리
  Given 시리얼 "WF-KR-250115D-001-0001"이 "검사" 공정에 착공되어 있을 때
  When result가 "FAIL"인 완공 JSON 파일이 생성되면
  Then 백엔드가 데이터를 처리하고
    And 시리얼 상태가 "FAILED"로 업데이트되고
    And 불량 원인이 측정 데이터에 기록되고
    And 관리자 대시보드에 불량 건수가 증가한다
```

### 시나리오 4: 대시보드 실시간 모니터링

**참조:** TC-DASH-001, TC-DASH-002, TC-DASH-003

```gherkin
Feature: 실시간 생산 모니터링
  As a 생산 관리자
  I want to 실시간으로 생산 현황을 확인할 수 있어야
  So that 생산 진행 상황을 모니터링할 수 있다

Scenario: 금일 생산 현황 표시
  Given 관리자 대시보드가 로드되어 있고
    And 오늘 날짜가 "2025-01-15"이고
    And 다음과 같은 데이터가 DB에 존재할 때:
      | LOT 번호 | 상태 | 착공 수 | 완공 수 | 불량 수 |
      | WF-KR-250115D-001 | IN_PROGRESS | 50 | 30 | 2 |
      | WF-KR-250115D-002 | IN_PROGRESS | 20 | 10 | 0 |
  When 대시보드의 "금일 현황" 패널을 확인하면
  Then 다음 정보가 표시된다:
    | 항목 | 값 |
    | 총 착공 | 70 |
    | 총 완공 | 40 |
    | 총 불량 | 2 |
    | 불량률 | 5.0% |

Scenario: 폴링을 통한 자동 갱신
  Given 대시보드가 로드되어 있고
    And 초기 착공 수가 70개로 표시되어 있고
    And 폴링 주기가 10초로 설정되어 있을 때
  When 5초 후 현장에서 새로운 착공이 발생하여 DB에 기록되면
  Then 최대 10초 이내에 대시보드가 폴링 API를 호출하고
    And 착공 수가 71개로 자동 갱신되고
    And 사용자가 새로고침 버튼을 누르지 않아도 된다

Scenario: 대시보드 초기 로딩 성능
  Given 관리자가 로그인되어 있고
    And DB에 100개의 LOT 데이터가 존재할 때
  When 대시보드 URL에 접속하면
  Then 3초 이내에 모든 패널이 렌더링되고
    And 네트워크 탭에서 API 응답 시간이 1초 이내이고
    And 사용자에게 로딩 인디케이터가 표시된다
```

### 시나리오 5: 시리얼 추적 (완전 추적성)

**참조:** TC-TRACE-002, TC-TRACE-003, TC-TRACE-004

```gherkin
Feature: 시리얼 번호 기반 제품 추적
  As a 품질 관리자
  I want to 시리얼 번호로 제품의 전체 이력을 조회할 수 있어야
  So that 문제 발생 시 원인을 빠르게 파악할 수 있다

Scenario: 시리얼 번호로 전체 이력 조회
  Given 시리얼 "WF-KR-250115D-001-0001"이 존재하고
    And 8개 공정을 모두 완료하여 "PASSED" 상태일 때
  When 대시보드에서 시리얼 번호를 검색하면
  Then 다음 정보가 5초 이내에 조회된다:
    | 항목 | 내용 |
    | LOT 번호 | WF-KR-250115D-001 |
    | 최종 상태 | PASSED |
    | 완료 공정 | 8/8 |
  And 공정별 상세 이력이 표시된다:
    | 공정명 | 작업자 | 착공시간 | 완공시간 | 결과 |
    | 라벨 프린팅 | USER001 | 09:00:00 | 09:05:00 | PASS |
    | 조립 | USER002 | 09:10:00 | 09:30:00 | PASS |
    | ... | ... | ... | ... | ... |
  And 측정 데이터가 JSON 형식으로 표시된다

Scenario: 부품 LOT 역추적
  Given 시리얼 "WF-KR-250115D-001-0001"의 조립 공정 데이터에
    And 다음과 같은 부품 LOT 정보가 기록되어 있을 때:
    """
    {
      "모선_lot": "MS-2025-100",
      "링크_lot": "LINK-2025-050"
    }
    """
  When 대시보드에서 부품 추적 탭을 확인하면
  Then 사용된 부품 LOT 목록이 표시되고
    And "MS-2025-100" 클릭 시 해당 부품을 사용한 모든 제품 목록이 조회되고
    And 부품 결함 발생 시 영향받는 제품을 빠르게 식별할 수 있다

Scenario: 불량 원인 추적
  Given 시리얼 "WF-KR-250115D-001-0050"이 "검사" 공정에서 불합격 처리되었고
    And 불량 원인이 다음과 같이 기록되어 있을 때:
    """
    {
      "result": "FAIL",
      "defect_code": "DEF-002",
      "defect_reason": "변위 측정값 초과 (210.5mm > 200mm)",
      "measured_data": {
        "변위": 210.5,
        "기준값": 200.0
      }
    }
    """
  When 대시보드에서 시리얼 번호를 조회하면
  Then 불량 상태가 명확히 표시되고
    And 불량 공정 "검사"가 강조되고
    And 불량 원인 "변위 측정값 초과"가 표시되고
    And 담당 작업자 정보가 표시되고
    And 이전 공정 데이터를 확인하여 근본 원인 분석이 가능하다
```

### 시나리오 6: 재작업 프로세스

**참조:** FR-DEFECT-004

```gherkin
Feature: 불량품 재작업 관리
  As a 품질 관리자
  I want to 불량품을 재작업 승인하고 추적할 수 있어야
  So that 불량품을 회수하여 생산 효율을 높일 수 있다

Scenario: 재작업 승인 및 재투입
  Given 시리얼 "WF-KR-250115D-001-0050"이 "FAILED" 상태이고
    And 불량 공정이 "검사"(sequence=7)이고
    And 품질 관리자 "MANAGER01"로 로그인되어 있을 때
  When 대시보드에서 재작업 승인 버튼을 클릭하고
    And 재작업 사유 "변위 측정값 재조정"을 입력하면
  Then 시리얼 상태가 "IN_PROGRESS"로 변경되고
    And rework_count가 1 증가하고
    And rework_approved_by가 "MANAGER01"로 기록되고
    And rework_approved_at이 현재 시간으로 기록되고
    And 다음 공정(Firmware Upgrade)부터 재착공 가능하다

Scenario: 재작업 횟수 제한
  Given 시리얼 "WF-KR-250115D-001-0050"의 rework_count가 3일 때
  When 재작업 승인을 다시 시도하면
  Then HTTP 400 Bad Request 응답이 반환되고
    And 에러 메시지 "재작업 횟수 제한 초과 (최대 3회)"가 표시되고
    And 승인이 차단된다

Scenario: 재작업 이력 조회
  Given 시리얼 "WF-KR-250115D-001-0050"이 재작업을 2회 수행했을 때
  When 대시보드에서 시리얼 이력을 조회하면
  Then 재작업 이력 섹션에 다음이 표시된다:
    | 재작업 차수 | 불량 공정 | 승인자 | 승인 시간 | 사유 |
    | 1차 | 검사 | MANAGER01 | 2025-01-15 10:00 | 변위 재조정 |
    | 2차 | 검사 | MANAGER01 | 2025-01-15 14:00 | 힘 측정 재검증 |
  And 각 재작업 후 공정 데이터에 is_rework=true 플래그가 설정되어 있다
```

### 시나리오 7: 동시성 제어

**참조:** NFR-PERF-002

```gherkin
Feature: 동시 사용자 처리
  As a 시스템
  I want to 여러 작업자의 동시 착공을 안전하게 처리할 수 있어야
  So that 데이터 무결성을 보장할 수 있다

Scenario: 동일 시리얼 동시 착공 방지
  Given 시리얼 "WF-KR-250115D-001-0001"이 "라벨 프린팅" 공정을 완료했고
    And 작업자 A와 작업자 B가 동시에 "조립" 공정 착공을 시도할 때
  When 두 요청이 1초 이내에 동시에 도착하면
  Then 먼저 도착한 요청만 성공하고 (HTTP 201)
    And 나중 요청은 실패하며 (HTTP 409 Conflict)
    And 에러 메시지 "해당 시리얼은 이미 공정 중입니다"가 반환되고
    And 데이터베이스에 중복 착공 데이터가 생성되지 않는다

Scenario: 부하 테스트 - 동시 착공 100건
  Given 100개의 서로 다른 시리얼이 준비되어 있고
    And 100명의 작업자가 동시에 착공을 시도할 때
  When 착공 API에 100개의 요청이 동시에 전송되면
  Then 모든 요청이 2초 이내에 처리되고
    And 100개 모두 성공 응답(HTTP 201)을 받고
    And 평균 응답 시간이 500ms 이하이고
    And 데이터베이스에 정확히 100개의 착공 레코드가 생성된다
```

### 시나리오 8: API 버전 전환

**참조:** 3.4.0 API 버전 관리 전략

```gherkin
Feature: API 버전 관리
  As a 클라이언트 개발자
  I want to API 버전을 안전하게 전환할 수 있어야
  So that 시스템 업그레이드 시 호환성을 유지할 수 있다

Scenario: v1 API 정상 동작
  Given 백엔드 API v1과 v2가 모두 배포되어 있고
    And 프론트엔드 앱이 v1을 사용 중일 때
  When "/api/v1/start-work" 엔드포인트를 호출하면
  Then HTTP 200 응답이 반환되고
    And v1 응답 스키마로 데이터가 제공된다

Scenario: v2 API로 전환
  Given 프론트엔드 앱이 v2로 업그레이드되었을 때
  When "/api/v2/start-work" 엔드포인트를 호출하면
  Then HTTP 200 응답이 반환되고
    And v2 응답 스키마(추가 필드 포함)로 데이터가 제공되고
    And v1 API는 계속 동작한다 (병렬 운영)

Scenario: v1 API 종료 예고
  Given v1 API가 6개월 후 종료 예정일 때
  When v1 엔드포인트를 호출하면
  Then HTTP 200 응답이 정상 반환되고
    And 응답 헤더에 "Deprecation: true"가 포함되고
    And 응답 헤더에 "Sunset: 2025-07-15T00:00:00Z"가 포함되어
    And 클라이언트가 마이그레이션 계획을 세울 수 있다
```

### 시나리오 9: WIP Item 라이프사이클 관리

**참조:** TC-WIP-001, TC-WIP-003, TC-WIP-004

```gherkin
Feature: WIP Item 라이프사이클 관리
  As a 생산 관리자
  I want to WIP Item을 생성하고 추적하고자 함
  So that 공정 1~6에서 개별 제품을 관리할 수 있다

Scenario: LOT에서 WIP 생성 및 공정 진행
  Given LOT "KR01PSA2511"이 "CREATED" 상태로 존재함
  When WIP 5개 생성 요청
  Then 5개 WIP Item이 생성됨
  And WIP ID는 "WIP-KR01PSA2511-001" ~ "WIP-KR01PSA2511-005"
  And 각 WIP 상태는 "CREATED"
  And LOT 상태는 "IN_PROGRESS"로 변경됨

  When "WIP-KR01PSA2511-001"로 공정 1 시작
  And 공정 1을 "PASS"로 완료
  Then WIP 상태는 "IN_PROGRESS"

  When 공정 2를 "PASS"로 완료
  And 공정 3을 "PASS"로 완료
  And 공정 4를 "PASS"로 완료
  And 공정 5를 "PASS"로 완료
  And 공정 6을 "PASS"로 완료
  Then WIP 상태는 "COMPLETED"
```

### 시나리오 10: WIP를 Serial로 전환

**참조:** TC-WIP-005

```gherkin
Feature: WIP to Serial 전환
  As a 생산 관리자
  I want to 완성된 WIP를 Serial Number로 전환하고자 함
  So that 공정 7부터 개별 Serial로 추적할 수 있다

Scenario: 모든 공정 완료 후 Serial 전환
  Given WIP "WIP-KR01PSA2511-001"이 존재함
  And 공정 1~6이 모두 "PASS" 상태
  And WIP 상태가 "COMPLETED"
  When WIP를 Serial로 전환 요청
  Then Serial Number "KR01PSA25110001"이 생성됨
  And WIP 상태는 "CONVERTED"
  And WIP의 serial_id가 설정됨
  And converted_at 타임스탬프가 기록됨
```

### 시나리오 11: REWORK 처리

**참조:** TC-WIP-006

```gherkin
Feature: WIP REWORK 처리
  As a 품질 관리자
  I want to 불량 WIP를 재작업할 수 있어야 함
  So that 생산 효율을 높일 수 있다

Scenario: 공정 실패 후 REWORK로 재작업
  Given WIP "WIP-KR01PSA2511-001"이 공정 3까지 진행됨
  When 공정 4를 "REWORK"로 완료
  Then WIP 상태는 "IN_PROGRESS" (FAILED 아님)
  And current_process_id는 null

  When 공정 4를 다시 시작
  And 공정 4를 "PASS"로 완료
  Then WIP 상태는 "IN_PROGRESS"
  And 공정 5~6 진행 가능
```

### 시나리오 12: LOT당 최대 WIP 개수 제한

**참조:** TC-WIP-002, TC-WIP-008

```gherkin
Feature: LOT당 WIP 개수 제한
  As a 시스템
  I want to LOT당 최대 100개 WIP만 생성 가능해야 함
  So that 데이터 무결성과 성능을 보장할 수 있다

Scenario: LOT당 최대 100개 WIP 제한
  Given LOT "KR01PSA2511"이 "CREATED" 상태
  When WIP 100개 생성 요청
  Then 100개 WIP가 정상 생성됨

  When WIP 1개 추가 생성 요청 (101번째)
  Then HTTP 400 Bad Request 응답
  And 에러 메시지 "Maximum 100 WIPs per LOT exceeded"
```

---

## 3.5.8 성능 및 비기능 요구사항 검수

| 검수 ID | 검수 항목 | 검수 기준 | NFR 참조 |
|---------|----------|----------|----------|
| TC-PERF-001 | API 응답 시간 | 착공 API 1초 이내, 완공 API 2초 이내 | NFR-PERF-001 |
| TC-PERF-002 | 대시보드 로딩 | 초기 로드 3초 이내 | NFR-PERF-003 |
| TC-PERF-003 | 동시 사용자 | 100명 동시 접속 시 응답 시간 저하 없음 | NFR-PERF-002 |
| TC-SEC-001 | 인증 검증 | JWT 토큰 없이 API 호출 시 HTTP 401 반환 | NFR-SEC-001 |
| TC-SEC-002 | 권한 검증 | WORKER 역할로 관리자 API 호출 시 HTTP 403 반환 | NFR-SEC-002 |
| TC-REL-001 | 데이터베이스 무결성 | LOT 상태 전이 규칙 위반 시 트리거가 차단 | NFR-REL-003 |
| TC-REL-002 | 트랜잭션 롤백 | 착공 처리 중 오류 발생 시 전체 롤백 | NFR-REL-004 |
| TC-MAINT-001 | 로그 기록 | 모든 에러에 대해 로그 레벨, 타임스탬프, 스택 트레이스 기록 | NFR-MAINT-002 |

---

**이전 섹션:** [3.4 데이터 인터페이스 요구사항](03-2-api-specs.md)
**다음 섹션:** [4.1 배포 옵션 비교](../04-architecture/04-1-deployment-options.md)
