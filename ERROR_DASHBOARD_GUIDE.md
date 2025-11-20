# 에러 로깅 대시보드 구현 가이드

## 개요

표준화된 에러 시스템의 로그를 수집하고 시각화하는 대시보드 구현 가이드입니다.

## 아키텍처

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Frontend    │─────▶│  Backend     │─────▶│  Database    │
│  (React)     │      │  (FastAPI)   │      │  (PostgreSQL)│
└──────────────┘      └──────────────┘      └──────────────┘
     │                      │                      │
     │                      │                      │
     ▼                      ▼                      ▼
┌──────────────────────────────────────────────────────────┐
│           Error Dashboard (실시간 모니터링)                │
│  - 에러 발생 추이 (시간별, 일별)                           │
│  - 에러 타입별 분포 (Pie Chart)                          │
│  - 최근 에러 로그 (Table)                                │
│  - trace_id 검색 및 필터링                                │
└──────────────────────────────────────────────────────────┘
```

## Phase 1: 백엔드 에러 로그 수집

### 1.1 에러 로그 테이블 생성

```sql
-- database/ddl/02_tables/error_logs.sql
CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    trace_id UUID NOT NULL UNIQUE,
    error_code VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    path VARCHAR(500),
    method VARCHAR(10),
    status_code INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(id),
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for fast querying
    INDEX idx_error_logs_timestamp (timestamp DESC),
    INDEX idx_error_logs_error_code (error_code),
    INDEX idx_error_logs_trace_id (trace_id),
    INDEX idx_error_logs_user_id (user_id)
);

-- Partition by month for performance
CREATE TABLE error_logs_2025_11 PARTITION OF error_logs
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

### 1.2 에러 로깅 미들웨어

```python
# backend/app/middleware/error_logging.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.error_log import ErrorLog
from app.schemas.error import StandardErrorResponse

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    모든 에러 응답을 데이터베이스에 로깅하는 미들웨어
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 4xx, 5xx 에러만 로깅
        if response.status_code >= 400:
            await self.log_error(request, response)

        return response

    async def log_error(self, request: Request, response):
        """에러를 데이터베이스에 저장"""
        try:
            db: Session = SessionLocal()

            # Response body 읽기
            body = await response.body()
            error_data = json.loads(body)

            # StandardErrorResponse 형식인지 확인
            if 'error_code' in error_data and 'trace_id' in error_data:
                error_log = ErrorLog(
                    trace_id=error_data['trace_id'],
                    error_code=error_data['error_code'],
                    message=error_data['message'],
                    path=error_data.get('path'),
                    method=request.method,
                    status_code=response.status_code,
                    user_id=getattr(request.state, 'user_id', None),
                    details=error_data.get('details'),
                    timestamp=datetime.fromisoformat(error_data['timestamp']),
                )

                db.add(error_log)
                db.commit()
        except Exception as e:
            # 로깅 실패는 무시 (원본 응답에 영향 없음)
            logger.error(f"Failed to log error: {e}")
        finally:
            db.close()
```

### 1.3 에러 로그 API 엔드포인트

```python
# backend/app/api/v1/error_logs.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud
from app.api import deps
from app.schemas.error_log import ErrorLogList, ErrorLogStats

router = APIRouter(prefix="/error-logs", tags=["Error Logs"])

@router.get("/", response_model=ErrorLogList)
def get_error_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    error_code: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.require_admin_role),
):
    """
    에러 로그 목록 조회 (관리자 전용)

    - 필터링: error_code, 날짜 범위
    - 정렬: 최신순 (timestamp DESC)
    """
    logs = crud.error_log.get_multi(
        db,
        skip=skip,
        limit=limit,
        error_code=error_code,
        start_date=start_date,
        end_date=end_date,
    )
    return logs

@router.get("/stats", response_model=ErrorLogStats)
def get_error_stats(
    hours: int = Query(24, ge=1, le=168),  # 최근 1-7일
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.require_admin_role),
):
    """
    에러 통계 조회

    - 시간별 에러 발생 추이
    - 에러 코드별 분포
    - 가장 많이 발생하는 에러 Top 10
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    stats = {
        "total_errors": crud.error_log.count(db, since=since),
        "by_error_code": crud.error_log.count_by_error_code(db, since=since),
        "by_hour": crud.error_log.count_by_hour(db, since=since),
        "top_paths": crud.error_log.get_top_paths(db, since=since, limit=10),
    }

    return stats

@router.get("/{trace_id}")
def get_error_by_trace_id(
    trace_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.require_admin_role),
):
    """
    trace_id로 에러 상세 조회

    디버깅 시 사용자가 제공한 trace_id로 에러 컨텍스트 확인
    """
    error_log = crud.error_log.get_by_trace_id(db, trace_id=trace_id)
    if not error_log:
        raise ResourceNotFoundException("Error log", trace_id)
    return error_log
```

## Phase 2: 프론트엔드 대시보드 구현

### 2.1 에러 대시보드 페이지

```tsx
// frontend/src/pages/ErrorDashboardPage.tsx
import React, { useState, useEffect } from 'react';
import { Card, Select, DatePicker, Table, message } from 'antd';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import { errorLogsApi } from '@/api/endpoints/errorLogs';
import { ERROR_MESSAGES_KO } from '@/types/error';

const ErrorDashboardPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState(24); // hours

  useEffect(() => {
    loadData();
  }, [timeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, logsData] = await Promise.all([
        errorLogsApi.getStats(timeRange),
        errorLogsApi.getErrorLogs({ limit: 50 }),
      ]);
      setStats(statsData);
      setLogs(logsData.items);
    } catch (error) {
      message.error('데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="error-dashboard">
      <h1>에러 모니터링 대시보드</h1>

      {/* Time Range Selector */}
      <Select
        value={timeRange}
        onChange={setTimeRange}
        options={[
          { value: 1, label: '최근 1시간' },
          { value: 24, label: '최근 24시간' },
          { value: 168, label: '최근 7일' },
        ]}
      />

      {/* Error Statistics Cards */}
      <div className="stats-cards">
        <Card title="총 에러 수">
          <h2>{stats?.total_errors || 0}</h2>
        </Card>
        <Card title="가장 많은 에러">
          <h3>{stats?.by_error_code?.[0]?.error_code}</h3>
          <p>{stats?.by_error_code?.[0]?.count}건</p>
        </Card>
      </div>

      {/* Error Trend Chart */}
      <Card title="시간별 에러 발생 추이">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={stats?.by_hour || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Error Distribution Pie Chart */}
      <Card title="에러 코드별 분포">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={stats?.by_error_code || []}
              dataKey="count"
              nameKey="error_code"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {stats?.by_error_code?.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </Card>

      {/* Recent Error Logs Table */}
      <Card title="최근 에러 로그">
        <Table
          dataSource={logs}
          columns={[
            {
              title: 'Timestamp',
              dataIndex: 'timestamp',
              key: 'timestamp',
              render: (val) => new Date(val).toLocaleString('ko-KR'),
            },
            {
              title: 'Error Code',
              dataIndex: 'error_code',
              key: 'error_code',
              render: (code) => ERROR_MESSAGES_KO[code] || code,
            },
            {
              title: 'Path',
              dataIndex: 'path',
              key: 'path',
            },
            {
              title: 'Trace ID',
              dataIndex: 'trace_id',
              key: 'trace_id',
              render: (id) => (
                <code style={{ fontSize: '0.8em' }}>
                  {id.substring(0, 8)}...
                </code>
              ),
            },
            {
              title: 'Actions',
              key: 'actions',
              render: (_, record) => (
                <a onClick={() => showErrorDetails(record)}>상세</a>
              ),
            },
          ]}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default ErrorDashboardPage;
```

### 2.2 에러 로그 API 클라이언트

```typescript
// frontend/src/api/endpoints/errorLogs.ts
import apiClient from '@/api/client';

export interface ErrorLog {
  id: number;
  trace_id: string;
  error_code: string;
  message: string;
  path?: string;
  method?: string;
  status_code: number;
  timestamp: string;
  details?: any;
}

export interface ErrorLogStats {
  total_errors: number;
  by_error_code: Array<{ error_code: string; count: number }>;
  by_hour: Array<{ hour: string; count: number }>;
  top_paths: Array<{ path: string; count: number }>;
}

export const errorLogsApi = {
  /**
   * 에러 로그 목록 조회
   */
  async getErrorLogs(params?: {
    skip?: number;
    limit?: number;
    error_code?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<{ items: ErrorLog[]; total: number }> {
    const response = await apiClient.get<{ items: ErrorLog[]; total: number }>(
      '/error-logs/',
      { params }
    );
    return response.data;
  },

  /**
   * 에러 통계 조회
   */
  async getStats(hours: number = 24): Promise<ErrorLogStats> {
    const response = await apiClient.get<ErrorLogStats>('/error-logs/stats', {
      params: { hours },
    });
    return response.data;
  },

  /**
   * trace_id로 에러 조회
   */
  async getByTraceId(traceId: string): Promise<ErrorLog> {
    const response = await apiClient.get<ErrorLog>(`/error-logs/${traceId}`);
    return response.data;
  },
};
```

## Phase 3: 알림 및 모니터링

### 3.1 실시간 알림 (선택적)

WebSocket을 통한 실시간 에러 알림:

```python
# backend/app/websockets/error_monitor.py
from fastapi import WebSocket
from typing import List

class ErrorMonitorManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_error(self, error_log: dict):
        """새로운 에러를 모든 연결된 클라이언트에 전송"""
        for connection in self.active_connections:
            await connection.send_json(error_log)

manager = ErrorMonitorManager()

@app.websocket("/ws/errors")
async def error_monitor_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 3.2 슬랙 알림 통합 (선택적)

심각한 에러 발생 시 Slack 알림:

```python
# backend/app/notifications/slack.py
import requests

def send_slack_alert(error_log: ErrorLog):
    """
    심각한 에러 발생 시 Slack에 알림

    조건:
    - 5xx 서버 에러
    - 5분 내 동일 에러 10회 이상
    """
    if error_log.status_code < 500:
        return  # Only alert on server errors

    webhook_url = settings.SLACK_WEBHOOK_URL

    message = {
        "text": f"🚨 서버 에러 발생",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{error_log.error_code}: {error_log.message}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Path:*\n{error_log.path}"},
                    {"type": "mrkdwn", "text": f"*Trace ID:*\n`{error_log.trace_id}`"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{error_log.timestamp}"},
                ]
            }
        ]
    }

    requests.post(webhook_url, json=message)
```

## Phase 4: 성능 최적화

### 4.1 데이터베이스 최적화

```sql
-- 파티셔닝으로 쿼리 성능 향상
-- 월별 파티션 자동 생성 (pg_cron)
CREATE EXTENSION IF NOT EXISTS pg_cron;

SELECT cron.schedule(
    'create-monthly-partition',
    '0 0 1 * *',  -- 매월 1일
    $$
    CREATE TABLE IF NOT EXISTS error_logs_' || to_char(CURRENT_DATE + interval '1 month', 'YYYY_MM') || '
    PARTITION OF error_logs
    FOR VALUES FROM (''' || (CURRENT_DATE + interval '1 month')::text || ''')
    TO (''' || (CURRENT_DATE + interval '2 months')::text || ''');
    $$
);

-- 오래된 로그 자동 삭제 (90일 이상)
SELECT cron.schedule(
    'cleanup-old-errors',
    '0 2 * * 0',  -- 매주 일요일 02:00
    $$
    DELETE FROM error_logs
    WHERE timestamp < CURRENT_DATE - interval '90 days';
    $$
);
```

### 4.2 캐싱

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=100)
def get_error_stats_cached(hours: int) -> ErrorLogStats:
    """에러 통계를 5분간 캐싱"""
    # 실제로는 Redis 사용 권장
    return get_error_stats(hours)
```

## 테스트

### E2E 테스트

```typescript
// frontend/e2e/error-dashboard.spec.ts
test('should display error statistics', async ({ page }) => {
  await page.goto('/admin/errors');

  // Stats cards should be visible
  await expect(page.locator('text=총 에러 수')).toBeVisible();

  // Charts should render
  await expect(page.locator('.recharts-wrapper')).toHaveCount(2);

  // Table should show recent errors
  const table = page.locator('table');
  await expect(table).toBeVisible();

  // Should be able to filter by error code
  await page.selectOption('select[name="error_code"]', 'RES_002');
  await page.waitForTimeout(500);

  // Table should update
  await expect(table.locator('tbody tr')).toHaveCount(greaterThan(0));
});
```

## 배포 체크리스트

- [ ] error_logs 테이블 생성 및 파티셔닝
- [ ] 에러 로깅 미들웨어 등록
- [ ] API 엔드포인트 구현 및 권한 설정
- [ ] 프론트엔드 대시보드 페이지 추가
- [ ] 관리자 전용 라우트 설정
- [ ] WebSocket 설정 (선택)
- [ ] Slack 알림 설정 (선택)
- [ ] 데이터 보관 정책 설정 (90일)
- [ ] 성능 모니터링 및 최적화

## 보안 고려사항

1. **접근 제어**: 에러 로그는 관리자만 열람
2. **민감 정보 마스킹**: 에러 메시지에서 비밀번호, 토큰 등 제거
3. **Rate Limiting**: 로그 조회 API에 rate limit 적용
4. **감사 로그**: 누가 언제 에러 로그를 조회했는지 기록
