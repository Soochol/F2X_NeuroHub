# Materialized View Refresh Guide

## Overview

This document provides guidance on refreshing the WIP tracking materialized views since `pg_cron` extension is not available in the current PostgreSQL container.

## Current Environment

- **PostgreSQL Version**: 14.20 on Alpine Linux
- **pg_cron Status**: ❌ Not available (requires installation and container rebuild)
- **Materialized Views**:
  - `mv_wip_status_dashboard` - LOT-level WIP status aggregation
  - `mv_process_wip_queue` - Process-level WIP queue monitoring

## Refresh Functions Available

The following refresh functions are already deployed:

```sql
-- Refresh single view
SELECT refresh_process_wip_queue();

-- Refresh all WIP views
SELECT refresh_all_wip_views();
```

## Recommended Refresh Strategies

### Option 1: Application-Level Scheduling (RECOMMENDED)

Use Python application scheduler to refresh views automatically.

#### Using APScheduler (FastAPI)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text
from backend.app.core.database import get_db

scheduler = AsyncIOScheduler()

async def refresh_wip_views():
    """Refresh WIP materialized views"""
    async with get_db() as db:
        await db.execute(text("SELECT refresh_all_wip_views()"))
        await db.commit()

# Schedule every 2 minutes during production hours
scheduler.add_job(
    refresh_wip_views,
    'cron',
    minute='*/2',
    hour='6-22',  # 6 AM to 10 PM
    id='refresh_wip_views',
    replace_existing=True
)

scheduler.start()
```

#### Using Celery Beat

```python
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import create_engine, text

app = Celery('f2x_neurohub')

@app.task
def refresh_wip_views():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT refresh_all_wip_views()"))
        conn.commit()

# Schedule in celeryconfig.py
app.conf.beat_schedule = {
    'refresh-wip-views': {
        'task': 'tasks.refresh_wip_views',
        'schedule': crontab(minute='*/2', hour='6-22'),
    },
}
```

### Option 2: System Cron Job

Create a shell script and schedule it with system cron.

#### Create Refresh Script

```bash
# File: /opt/scripts/refresh_wip_views.sh
#!/bin/bash

CONTAINER_NAME="f2x-postgres"
DB_NAME="f2x_neurohub_mes"
DB_USER="postgres"

docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "SELECT refresh_all_wip_views();"
```

#### Add to System Crontab

```bash
# Edit crontab
crontab -e

# Add refresh job (every 2 minutes, 6 AM to 10 PM)
*/2 6-22 * * * /opt/scripts/refresh_wip_views.sh >> /var/log/wip_refresh.log 2>&1
```

### Option 3: Manual API Endpoint

Create an API endpoint to trigger refresh manually or via external scheduler.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.core.database import get_db

router = APIRouter()

@router.post("/admin/refresh-wip-views")
async def refresh_wip_views(db: AsyncSession = Depends(get_db)):
    """Manually refresh WIP materialized views"""
    try:
        await db.execute(text("SELECT refresh_all_wip_views()"))
        await db.commit()
        return {
            "status": "success",
            "message": "WIP materialized views refreshed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to refresh views: {str(e)}"
        }
```

### Option 4: Install pg_cron (Advanced)

If automatic database-level scheduling is required, install `pg_cron` extension.

#### Step 1: Modify Docker Image

```dockerfile
# In Dockerfile
FROM postgres:14-alpine

# Install pg_cron
RUN apk add --no-cache postgresql-dev build-base git \
    && git clone https://github.com/citusdata/pg_cron.git \
    && cd pg_cron \
    && make && make install

# Modify postgresql.conf
RUN echo "shared_preload_libraries = 'pg_cron'" >> /usr/local/share/postgresql/postgresql.conf.sample
```

#### Step 2: Rebuild and Deploy

```bash
# Rebuild container
docker-compose down
docker-compose up -d --build

# Create extension
docker exec f2x-postgres psql -U postgres -d f2x_neurohub_mes -c "CREATE EXTENSION pg_cron;"

# Schedule refresh job
docker exec f2x-postgres psql -U postgres -d f2x_neurohub_mes -c "
SELECT cron.schedule(
    'refresh-wip-views',
    '*/2 6-22 * * *',  -- Every 2 minutes from 6 AM to 10 PM
    'SELECT refresh_all_wip_views();'
);
"
```

## Performance Monitoring

### Check View Freshness

```sql
-- Check when views were last refreshed
SELECT
    matviewname,
    last_refreshed_at
FROM (
    SELECT 'mv_wip_status_dashboard' as matviewname, last_refreshed_at
    FROM mv_wip_status_dashboard
    LIMIT 1

    UNION ALL

    SELECT 'mv_process_wip_queue' as matviewname, last_refreshed_at
    FROM mv_process_wip_queue
    LIMIT 1
) views;
```

### Monitor Refresh Performance

```sql
-- Check refresh duration
\timing on
SELECT refresh_all_wip_views();
\timing off
```

### View Size and Row Count

```sql
SELECT
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
FROM pg_matviews
WHERE matviewname LIKE '%wip%';
```

## Refresh Frequency Recommendations

| Environment | Refresh Interval | Reasoning |
|------------|------------------|-----------|
| **Development** | 5-10 minutes | Lower frequency for testing |
| **Production** | 1-2 minutes | Real-time monitoring during production hours |
| **Off-Hours** | 10-15 minutes | Reduced frequency during non-production hours |
| **High Load** | On-demand via API | Manual control during peak operations |

## Troubleshooting

### Slow Refresh Performance

If refresh takes longer than expected:

```sql
-- Check indexes exist
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('wip_items', 'wip_process_history');

-- Analyze tables
ANALYZE wip_items;
ANALYZE wip_process_history;

-- Check table sizes
SELECT
    relname,
    n_live_tup as row_count,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_stat_user_tables
WHERE relname LIKE 'wip%'
ORDER BY n_live_tup DESC;
```

### Lock Conflicts

If CONCURRENT refresh fails:

```sql
-- Check for blocking locks
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) as blocked_by,
    query as blocked_query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

### View Definition Issues

If refresh fails with errors:

```sql
-- Drop and recreate views
DROP MATERIALIZED VIEW IF EXISTS mv_wip_status_dashboard CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_process_wip_queue CASCADE;

-- Re-run creation scripts
\i views/wip_views/01_mv_wip_status_dashboard.sql
\i views/wip_views/02_mv_process_wip_queue.sql
```

## Summary

✅ **Completed Setup**:
- Refresh functions created (`refresh_all_wip_views()`)
- Materialized views deployed with CONCURRENT refresh support
- Unique indexes created for concurrent refresh

⏳ **Pending Configuration**:
- Choose and implement one of the refresh strategies above
- Set up monitoring for view freshness
- Configure alerts for refresh failures

📝 **Recommendation**:
Use **Option 1 (Application-Level Scheduling with APScheduler)** for the best integration with the existing FastAPI backend and easier deployment management.

## Next Steps

1. **Immediate**: Test manual refresh with `SELECT refresh_all_wip_views();`
2. **Short-term**: Implement application-level scheduling (Option 1)
3. **Long-term**: Consider pg_cron installation if database-level scheduling is preferred (Option 4)
