# Results/Reports 기능 테스트 계획

## 1. 테스트 범위

### Backend (station_service)
- API 엔드포인트 (`/api/reports/*`)
- ReportService 및 Generator 클래스
- ExportService 및 Exporter 클래스
- Repository 집계 쿼리

### Frontend (station_ui)
- React 컴포넌트 (ResultsTable, ResultsFilter, ReportViewer 등)
- React Query 훅 (useReports.ts)
- API 클라이언트 함수
- E2E 시나리오

---

## 2. Backend 테스트

### 2.1 Unit Tests

#### Repository 집계 쿼리
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| REPO-001 | `get_batch_statistics()` - 유효한 batch_id | 통계 데이터 반환 (total, pass, fail, avg_duration) |
| REPO-002 | `get_batch_statistics()` - 존재하지 않는 batch_id | 빈 통계 (total=0) 반환 |
| REPO-003 | `get_step_statistics_by_batch()` - 스텝별 통계 | 각 스텝별 pass_rate, duration 통계 |
| REPO-004 | `get_period_statistics()` - 일별 집계 | 날짜별 그룹화된 통계 |
| REPO-005 | `get_period_statistics()` - 주별 집계 | 주별 그룹화된 통계 |
| REPO-006 | `get_period_statistics()` - 월별 집계 | 월별 그룹화된 통계 |
| REPO-007 | `get_step_analysis()` - 실패율 높은 순 정렬 | fail_rate 내림차순 정렬 |
| REPO-008 | `get_failure_reasons_by_step()` - 에러 메시지 집계 | 에러별 발생 횟수 |

#### ReportService
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| RPT-001 | BatchSummaryReportGenerator - 정상 생성 | BatchSummaryReport 객체 반환 |
| RPT-002 | PeriodStatisticsReportGenerator - 일별 | dataPoints에 날짜별 데이터 |
| RPT-003 | PeriodStatisticsReportGenerator - 트렌드 계산 | increasing/decreasing/stable 판정 |
| RPT-004 | StepAnalysisReportGenerator - 실패 분석 | failureReasons 포함 |
| RPT-005 | StepAnalysisReportGenerator - slowestStep 식별 | P95 기준 가장 느린 스텝 |
| RPT-006 | ReportService.get_generator() - 등록된 타입 | 올바른 Generator 반환 |
| RPT-007 | ReportService.get_generator() - 미등록 타입 | ValueError 발생 |

#### ExportService
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| EXP-001 | JsonExporter - 리포트 내보내기 | application/json Response |
| EXP-002 | CsvExporter - 리포트 내보내기 | text/csv Response, 올바른 헤더 |
| EXP-003 | ExcelExporter - 리포트 내보내기 | xlsx 파일, openpyxl로 검증 |
| EXP-004 | PdfExporter - 리포트 내보내기 | application/pdf Response |
| EXP-005 | ExportService.get_exporter() - 등록된 포맷 | 올바른 Exporter 반환 |
| EXP-006 | ExportService.register_exporter() - 커스텀 등록 | 새 Exporter 사용 가능 |

### 2.2 API Integration Tests

#### /api/reports/batch/{batch_id}
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| API-001 | GET - format=json (기본값) | 200, JSON 리포트 |
| API-002 | GET - format=xlsx | 200, Excel 파일 다운로드 |
| API-003 | GET - format=pdf | 200, PDF 파일 다운로드 |
| API-004 | GET - 존재하지 않는 batch_id | 404 Not Found |
| API-005 | GET - 데이터 없는 batch_id | 404 "No execution data found" |

#### /api/reports/period
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| API-006 | GET - period=daily, from/to 필수 파라미터 | 200, 일별 통계 |
| API-007 | GET - period=weekly | 200, 주별 통계 |
| API-008 | GET - period=monthly | 200, 월별 통계 |
| API-009 | GET - from > to (잘못된 범위) | 400 Bad Request |
| API-010 | GET - batch_id 필터 적용 | 해당 배치만 포함 |

#### /api/reports/step-analysis
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| API-011 | GET - 필터 없이 전체 | 200, 전체 스텝 분석 |
| API-012 | GET - batch_id 필터 | 해당 배치 스텝만 |
| API-013 | GET - from/to 필터 | 기간 내 데이터만 |
| API-014 | GET - format=xlsx | Excel 파일 다운로드 |

#### /api/reports/types
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| API-015 | GET | 200, report_types + export_formats |

#### /api/results/export (Bulk)
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| API-016 | POST - 여러 result_ids | 200, 병합된 Export 파일 |
| API-017 | POST - 빈 result_ids | 400 Bad Request |

---

## 3. Frontend 테스트

### 3.1 Component Unit Tests (Vitest + Testing Library)

#### ResultsFilter
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-001 | 배치 선택 드롭다운 렌더링 | 옵션 목록 표시 |
| CMP-002 | 상태 필터 변경 | onStatusChange 콜백 호출 |
| CMP-003 | 날짜 필터 입력 | onFromDateChange/onToDateChange 호출 |
| CMP-004 | Clear 버튼 클릭 | onClear 콜백 호출 |
| CMP-005 | 필터 활성화 시 Clear 버튼 표시 | hasActiveFilters 조건 |

#### ResultsTable
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-006 | 빈 결과 시 "No results found" 표시 | 빈 상태 메시지 |
| CMP-007 | 로딩 중 스피너 표시 | LoadingSpinner 렌더링 |
| CMP-008 | 결과 행 렌더링 | status, sequence, batch, duration 표시 |
| CMP-009 | 체크박스 선택 | onSelectionChange 콜백 호출 |
| CMP-010 | 전체 선택 체크박스 | 모든 ID 선택/해제 |
| CMP-011 | 정렬 헤더 클릭 | onSort 콜백 호출 |
| CMP-012 | View 버튼 클릭 | onViewDetail 콜백 호출 |

#### ResultDetailModal
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-013 | 모달 렌더링 | 헤더, 요약, 스텝 목록 표시 |
| CMP-014 | 스텝 행 확장/축소 | 에러/결과 데이터 토글 |
| CMP-015 | Close 버튼 클릭 | onClose 콜백 호출 |
| CMP-016 | 실패 결과 표시 | Failed indicator 표시 |

#### ReportTypeSelector
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-017 | 3개 탭 렌더링 | batch_summary, period_stats, step_analysis |
| CMP-018 | 탭 클릭 | onSelect 콜백 호출 |
| CMP-019 | 선택된 탭 스타일 | 활성 스타일 적용 |

#### ExportButton
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-020 | 드롭다운 토글 | 옵션 목록 표시/숨김 |
| CMP-021 | 포맷 선택 | onExport(format) 콜백 호출 |
| CMP-022 | 로딩 상태 | 스피너 표시, 버튼 비활성화 |
| CMP-023 | 외부 클릭 시 닫힘 | 드롭다운 숨김 |

#### BatchSummaryReport
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-024 | batchId null 시 선택 안내 | "Select a batch" 메시지 |
| CMP-025 | 로딩 상태 | 스피너 표시 |
| CMP-026 | 데이터 표시 | 통계 카드 + 스텝 테이블 |
| CMP-027 | Export 버튼 동작 | useExportBatchSummaryReport 호출 |

#### PeriodStatsReport
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-028 | 기간 선택 드롭다운 | daily/weekly/monthly 옵션 |
| CMP-029 | 날짜 범위 기본값 | 최근 30일 |
| CMP-030 | 트렌드 아이콘 표시 | TrendingUp/Down/Minus |
| CMP-031 | 기간별 데이터 테이블 | dataPoints 렌더링 |

#### StepAnalysisReport
| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| CMP-032 | Most Failed Step 표시 | 배지 하이라이트 |
| CMP-033 | Slowest Step 표시 | 배지 하이라이트 |
| CMP-034 | 실패 원인 확장 | failureReasons 표시 |

### 3.2 Hook Tests

| 테스트 ID | 테스트 항목 | 예상 결과 |
|-----------|------------|----------|
| HK-001 | useBatchSummaryReport - enabled 조건 | batchId 있을 때만 fetch |
| HK-002 | usePeriodStatsReport - 파라미터 전달 | queryKey에 period, from, to 포함 |
| HK-003 | useExportBatchSummaryReport - 성공 시 | downloadBlob 호출 |
| HK-004 | useExportResultsBulk - mutation | 파일 다운로드 트리거 |

### 3.3 E2E Tests (Playwright)

| 테스트 ID | 시나리오 | 예상 결과 |
|-----------|---------|----------|
| E2E-001 | Results 페이지 진입 | List 뷰 기본 표시 |
| E2E-002 | 배치 필터 선택 → 테이블 필터링 | 선택된 배치만 표시 |
| E2E-003 | 상태 필터 선택 | 해당 상태만 표시 |
| E2E-004 | 날짜 범위 필터 | 기간 내 결과만 표시 |
| E2E-005 | 결과 행 선택 → Bulk Export | 파일 다운로드 |
| E2E-006 | View 버튼 → 상세 모달 | 모달 열림, 스텝 목록 표시 |
| E2E-007 | Reports 탭 전환 | 리포트 뷰 표시 |
| E2E-008 | Batch Summary 리포트 조회 | 배치 선택 → 통계 표시 |
| E2E-009 | Period Stats 리포트 조회 | 기간/날짜 선택 → 통계 표시 |
| E2E-010 | Step Analysis 리포트 조회 | 스텝별 분석 표시 |
| E2E-011 | Excel Export | .xlsx 파일 다운로드 |
| E2E-012 | PDF Export | .pdf 파일 다운로드 |

---

## 4. 테스트 데이터 준비

### 4.1 Fixtures
```python
# Backend fixtures
@pytest.fixture
def sample_executions():
    """10개 실행 결과 (7 PASS, 3 FAIL)"""
    pass

@pytest.fixture
def sample_batch_with_steps():
    """5개 스텝, 다양한 duration을 가진 배치"""
    pass
```

### 4.2 Mock Data
```typescript
// Frontend mocks
export const mockBatchSummaryReport: BatchSummaryReport = {
  batchId: 'batch-001',
  totalExecutions: 100,
  passCount: 95,
  failCount: 5,
  passRate: 0.95,
  // ...
};
```

---

## 5. 테스트 환경

### Backend
- pytest + pytest-asyncio
- httpx (AsyncClient for API tests)
- SQLite in-memory DB

### Frontend
- Vitest + React Testing Library
- MSW (Mock Service Worker) for API mocking
- Playwright for E2E

---

## 6. 테스트 실행 명령어

```bash
# Backend Unit/Integration
cd station_service
pytest tests/unit/test_report_service.py -v
pytest tests/unit/test_export_service.py -v
pytest tests/integration/test_reports_api.py -v

# Frontend Unit
cd station_ui
npm run test -- --run src/components/organisms/results/
npm run test -- --run src/hooks/useReports.test.ts

# Frontend E2E
npm run test:e2e -- results.spec.ts
```

---

## 7. 우선순위

| 우선순위 | 테스트 영역 | 이유 |
|---------|-----------|------|
| P0 (Critical) | API 엔드포인트 테스트 | 핵심 기능 동작 검증 |
| P0 (Critical) | Export 파일 생성 | 사용자 출력물 품질 |
| P1 (High) | 컴포넌트 렌더링 | UI 정상 동작 |
| P1 (High) | 필터/정렬 로직 | 데이터 정확성 |
| P2 (Medium) | E2E 시나리오 | 통합 워크플로우 |
| P3 (Low) | 엣지 케이스 | 예외 상황 처리 |

---

## 8. 완료 기준

- [ ] Backend Unit Tests 커버리지 80% 이상
- [ ] Frontend Component Tests 커버리지 70% 이상
- [ ] 모든 P0/P1 테스트 통과
- [ ] E2E 핵심 시나리오 (E2E-001 ~ E2E-012) 통과
- [ ] Export 파일 포맷 검증 완료 (Excel, PDF 수동 확인)
