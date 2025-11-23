# Performance Monitoring Setup Guide

## Overview

The F2X NeuroHub performance monitoring system provides comprehensive tracking of:
- Database query performance
- API endpoint latency
- System resource utilization
- Application-level metrics

## Quick Start

### 1. Enable Monitoring

Set the following environment variables in your `.env` file:

```bash
# Enable monitoring features
ENABLE_QUERY_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=true

# Performance thresholds
SLOW_QUERY_THRESHOLD_MS=100
RESPONSE_TIME_ALERT_MS=1000
MEMORY_ALERT_PERCENT=80
CPU_ALERT_PERCENT=80
ERROR_RATE_ALERT_PERCENT=5

# Log settings
MAX_QUERY_LOG_SIZE=10000
MAX_METRICS_LOG_SIZE=10000
```

### 2. Integration with FastAPI

Add monitoring to your FastAPI application:

```python
# backend/app/main.py
from app.monitoring import PerformanceMonitoringMiddleware
from app.monitoring.query_monitor import setup_sqlalchemy_monitoring
from app.database import engine

# Add performance monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)

# Enable SQLAlchemy query monitoring
setup_sqlalchemy_monitoring(engine)
```

### 3. Using Decorators

#### Monitor Database Queries

```python
from app.monitoring import monitor_query

@monitor_query("get_user_by_id")
async def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

#### Monitor API Endpoints

```python
from app.monitoring import monitor_endpoint

@router.get("/users/{user_id}")
@monitor_endpoint("/api/users/{id}")
async def get_user_endpoint(user_id: int):
    return await get_user(user_id)
```

#### Track Database Operations

```python
from app.monitoring import PerformanceTracker

tracker = PerformanceTracker()

# Manual tracking
tracker.track_database_operation(
    operation="SELECT",
    table="users",
    duration_ms=25.3,
    rows_affected=1
)
```

## Metrics to Track

### 1. Query Performance Metrics

| Metric | Description | Alert Threshold | Action Required |
|--------|-------------|-----------------|-----------------|
| Query Execution Time | Time taken to execute database queries | >100ms | Optimize query or add index |
| Query Count | Number of queries per request | >10 queries | Consider query optimization |
| Slow Query Rate | Percentage of slow queries | >5% | Review and optimize slow queries |
| Failed Query Rate | Percentage of failed queries | >1% | Investigate database issues |

### 2. API Endpoint Metrics

| Metric | Description | Alert Threshold | Action Required |
|--------|-------------|-----------------|-----------------|
| Response Time | Total time to process request | >1000ms | Optimize endpoint logic |
| Error Rate | Percentage of failed requests | >5% | Investigate errors |
| Request Volume | Requests per second | >1000 RPS | Consider scaling |
| Response Size | Size of response payload | >5MB | Implement pagination |

### 3. System Resource Metrics

| Metric | Description | Alert Threshold | Action Required |
|--------|-------------|-----------------|-----------------|
| CPU Usage | Percentage of CPU utilization | >80% | Scale horizontally or optimize |
| Memory Usage | Percentage of memory used | >80% | Check for memory leaks |
| Disk I/O | Read/Write operations per second | >1000 IOPS | Optimize database queries |
| Network I/O | Network throughput | >100 Mbps | Consider CDN or compression |

### 4. Application Metrics

| Metric | Description | Alert Threshold | Action Required |
|--------|-------------|-----------------|-----------------|
| Active Connections | Number of open database connections | >90% of pool | Increase pool size |
| Thread Count | Number of active threads | >500 | Review thread usage |
| Process Memory | Application memory usage | >2GB | Profile memory usage |
| Cache Hit Rate | Percentage of cache hits | <80% | Review caching strategy |

## Alert Thresholds

### Critical Alerts (Immediate Action)

```yaml
critical:
  query_time: >5000ms          # Extremely slow query
  response_time: >10000ms       # Request timeout territory
  error_rate: >10%              # High failure rate
  cpu_usage: >95%               # System overload
  memory_usage: >95%            # Out of memory risk
```

### Warning Alerts (Investigation Required)

```yaml
warning:
  query_time: >1000ms           # Slow query
  response_time: >3000ms        # Slow endpoint
  error_rate: >5%               # Elevated errors
  cpu_usage: >80%               # High CPU usage
  memory_usage: >80%            # High memory usage
```

### Info Alerts (Monitor Trend)

```yaml
info:
  query_time: >100ms            # Query slower than baseline
  response_time: >1000ms        # Response slower than target
  error_rate: >1%               # Errors present
  cpu_usage: >60%               # Moderate CPU usage
  memory_usage: >60%            # Moderate memory usage
```

## Accessing Metrics

### 1. Real-time Metrics API

```python
# Get current performance summary
GET /api/monitoring/metrics

# Get query statistics
GET /api/monitoring/queries

# Get system metrics
GET /api/monitoring/system
```

### 2. Programmatic Access

```python
from app.monitoring import get_query_stats, get_performance_summary

# Get query statistics
query_stats = get_query_stats()
print(f"Total queries: {query_stats['total_queries']}")
print(f"Slow queries: {query_stats['total_slow_queries']}")

# Get performance summary
perf_summary = get_performance_summary()
print(f"Total requests: {perf_summary['endpoint_metrics']['total_requests']}")
print(f"Error rate: {perf_summary['endpoint_metrics']['error_rate_percent']}%")
```

### 3. Export Metrics

```python
from app.monitoring import export_metrics, log_slow_queries

# Export performance metrics
metrics_file = export_metrics()
print(f"Metrics exported to: {metrics_file}")

# Export slow query log
query_log = log_slow_queries()
print(f"Query log exported to: {query_log}")
```

### 4. Log Files

Monitoring logs are stored in `logs/monitoring/`:

```
logs/monitoring/
├── slow_queries.log           # Slow query details
├── performance_metrics.log    # Performance metrics
├── query_stats_*.json         # Query statistics exports
└── performance_metrics_*.json # Performance metrics exports
```

## Integration with Monitoring Tools

### 1. Prometheus Integration

```python
# backend/app/monitoring/prometheus_exporter.py
from prometheus_client import Counter, Histogram, Gauge
import prometheus_client

# Define metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request latency')
database_query_duration_seconds = Histogram('db_query_duration_seconds', 'Database query latency')
memory_usage_bytes = Gauge('memory_usage_bytes', 'Memory usage in bytes')

# Export metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(prometheus_client.generate_latest(), media_type="text/plain")
```

### 2. Grafana Dashboard

Create a Grafana dashboard with the following panels:

```json
{
  "dashboard": {
    "title": "F2X NeuroHub Performance",
    "panels": [
      {
        "title": "API Response Time",
        "targets": [{
          "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
        }]
      },
      {
        "title": "Query Performance",
        "targets": [{
          "expr": "histogram_quantile(0.95, db_query_duration_seconds)"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(http_requests_total{status=~'5..'}[5m])"
        }]
      },
      {
        "title": "Memory Usage",
        "targets": [{
          "expr": "memory_usage_bytes / 1024 / 1024"
        }]
      }
    ]
  }
}
```

### 3. Datadog Integration

```python
# backend/app/monitoring/datadog_integration.py
from datadog import initialize, statsd
from app.monitoring import PerformanceTracker

# Initialize Datadog
initialize(api_key='YOUR_API_KEY', app_key='YOUR_APP_KEY')

# Send metrics to Datadog
def send_metrics_to_datadog():
    tracker = PerformanceTracker()
    summary = tracker.get_performance_summary()

    # Send metrics
    statsd.gauge('app.requests.total', summary['endpoint_metrics']['total_requests'])
    statsd.gauge('app.requests.errors', summary['endpoint_metrics']['total_errors'])
    statsd.gauge('app.response_time.avg', summary['endpoint_metrics']['response_time_stats'].get('avg', 0))

    # Send system metrics
    if summary['system_metrics']:
        statsd.gauge('system.cpu.percent', summary['system_metrics']['cpu_percent'])
        statsd.gauge('system.memory.percent', summary['system_metrics']['memory_percent'])
```

### 4. ELK Stack Integration

```yaml
# logstash.conf
input {
  file {
    path => "/app/logs/monitoring/slow_queries.log"
    type => "slow_query"
    codec => json
  }
  file {
    path => "/app/logs/monitoring/performance_metrics.log"
    type => "performance"
    codec => json
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "neurohub-%{type}-%{+YYYY.MM.dd}"
  }
}
```

## Performance Optimization Recommendations

### 1. Database Optimization

- **Add Indexes**: For queries taking >100ms consistently
- **Query Optimization**: Rewrite queries with multiple joins
- **Connection Pooling**: Adjust pool size based on concurrent load
- **Caching**: Implement Redis for frequently accessed data

### 2. API Optimization

- **Response Caching**: Cache responses for read-heavy endpoints
- **Pagination**: Implement for large result sets
- **Async Processing**: Move heavy operations to background tasks
- **Rate Limiting**: Prevent abuse and ensure fair usage

### 3. Resource Optimization

- **Memory Management**: Use generators for large datasets
- **CPU Optimization**: Profile and optimize hot code paths
- **I/O Optimization**: Batch database operations
- **Network Optimization**: Implement response compression

## Monitoring Best Practices

### 1. Development Environment

```bash
# Minimal monitoring for development
ENABLE_QUERY_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=false
SLOW_QUERY_THRESHOLD_MS=50
```

### 2. Staging Environment

```bash
# Full monitoring for staging
ENABLE_QUERY_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=true
SLOW_QUERY_THRESHOLD_MS=100
RESPONSE_TIME_ALERT_MS=2000
```

### 3. Production Environment

```bash
# Optimized monitoring for production
ENABLE_QUERY_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=true
SLOW_QUERY_THRESHOLD_MS=100
RESPONSE_TIME_ALERT_MS=1000
MEMORY_ALERT_PERCENT=80
CPU_ALERT_PERCENT=80
ERROR_RATE_ALERT_PERCENT=5
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check for memory leaks in long-running processes
   - Review query result set sizes
   - Implement proper cleanup in background tasks

2. **Slow Queries**
   - Check query execution plans
   - Add appropriate indexes
   - Consider query result caching

3. **High Error Rates**
   - Review error logs for patterns
   - Check database connection stability
   - Validate input data processing

4. **Performance Degradation**
   - Monitor trends over time
   - Check for increased load patterns
   - Review recent code changes

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Get detailed query information
from app.monitoring import QueryMonitor
monitor = QueryMonitor()
stats = monitor.get_statistics()
print(json.dumps(stats, indent=2))
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Review slow query logs
   - Check error rates
   - Monitor resource usage trends

2. **Weekly**
   - Export and analyze performance metrics
   - Review and optimize slow queries
   - Update alert thresholds based on patterns

3. **Monthly**
   - Performance report generation
   - Capacity planning review
   - Database index optimization

### Log Rotation

Configure log rotation to prevent disk space issues:

```yaml
# /etc/logrotate.d/neurohub
/app/logs/monitoring/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 app app
}
```

## API Reference

### Monitoring Endpoints

```python
from fastapi import APIRouter
from app.monitoring import get_query_stats, get_performance_summary

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

@router.get("/metrics")
async def get_metrics():
    """Get current performance metrics."""
    return get_performance_summary()

@router.get("/queries")
async def get_queries():
    """Get query statistics."""
    return get_query_stats()

@router.post("/reset")
async def reset_metrics():
    """Reset all monitoring metrics."""
    from app.monitoring import reset_query_stats
    from app.monitoring import PerformanceTracker

    reset_query_stats()
    PerformanceTracker().reset_metrics()
    return {"status": "metrics reset"}

@router.get("/export")
async def export_metrics():
    """Export metrics to file."""
    from app.monitoring import export_metrics, log_slow_queries

    perf_file = export_metrics()
    query_file = log_slow_queries()

    return {
        "performance_metrics": perf_file,
        "query_logs": query_file
    }
```

## Support

For issues or questions about monitoring:

1. Check the monitoring logs in `logs/monitoring/`
2. Review this documentation
3. Contact the development team
4. Submit an issue on the project repository