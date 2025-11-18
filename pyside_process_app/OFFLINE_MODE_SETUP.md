# Offline Mode Integration Guide

This guide explains how to integrate the offline mode and error handling enhancements into your PySide6 application.

## Overview

The offline mode system consists of three main components:

1. **OfflineManager** - Manages offline queue and connection status
2. **RetryManager** - Handles automatic retry of queued requests
3. **Enhanced APIClient** - Automatically queues failed requests

## Setup Instructions

### 1. Initialize Components in Main Application

```python
from services import APIClient, OfflineManager, RetryManager, ProcessService
from viewmodels.main_viewmodel import MainViewModel

# Create offline manager
offline_manager = OfflineManager(queue_path="offline_queue")

# Create API client with offline support
api_client = APIClient(
    base_url="http://localhost:8000",
    offline_manager=offline_manager
)

# Create retry manager
retry_manager = RetryManager(offline_manager, api_client)

# Create process service
process_service = ProcessService(api_client)

# Create view model with offline support
viewmodel = MainViewModel(
    process_service=process_service,
    file_watcher_service=file_watcher_service,
    config=config,
    app_state=app_state,
    offline_manager=offline_manager,
    retry_manager=retry_manager
)
```

### 2. Connect to UI (MainWindow)

The MainWindow automatically connects to offline mode signals:

```python
# In MainWindow.__init__
self.viewmodel.connection_status_changed.connect(self.on_connection_status_changed)
self.viewmodel.offline_queue_changed.connect(self.on_offline_queue_changed)
```

## Features

### Connection Status Indicator

The status bar shows:
- 🟢 온라인 - Backend is reachable
- 🔴 오프라인 - Backend is unreachable

### Offline Queue Display

- Shows number of queued requests: "큐: 5"
- Hidden when queue is empty
- Updates automatically

### Manual Retry Button

- Appears when offline
- Allows user to manually trigger queue processing
- Processes all queued requests

### Automatic Retry

When connection is restored:
- Automatically detects connection recovery
- Waits 2 seconds for stability
- Processes entire offline queue
- Removes successfully processed requests

## Error Handling

### User-Friendly Error Messages

All errors show emojis and clear Korean messages:

```python
from utils.constants import ERROR_MESSAGES

# Connection errors
🔴 백엔드 서버에 연결할 수 없습니다.
오프라인 모드로 전환되었습니다.

# Timeout errors
⏱️ 서버 응답 시간이 초과되었습니다.
잠시 후 다시 시도해주세요.

# Authentication errors
🔐 인증에 실패했습니다.
다시 로그인해주세요.

# Validation errors
⚠️ 입력 데이터가 올바르지 않습니다.

# Server errors
❌ 서버 오류가 발생했습니다.
관리자에게 문의하세요.
```

### Graceful Degradation

When backend is offline:

1. **POST/PUT/DELETE requests** are automatically queued
2. **GET requests** fail gracefully (not queued)
3. User is notified of offline mode
4. Application continues to function
5. Data is saved locally

## Queue Management

### Queue File Format

Queued requests are stored as JSON files in `offline_queue/`:

```json
{
  "type": "POST",
  "endpoint": "/api/v1/process-data",
  "data": {
    "lot_id": 123,
    "process_id": 1,
    "operator_id": 1,
    "started_at": "2025-01-15T10:30:00Z"
  },
  "timestamp": "2025-01-15T10:30:00.123456",
  "retry_count": 0
}
```

### Retry Logic

- **Max retries**: 3 attempts
- **Retry interval**: 30 seconds (health check)
- **Auto-retry**: On connection restoration
- **Manual retry**: Via UI button

### Queue Cleanup

Old requests (72+ hours) are automatically cleaned up:

```python
# Cleanup happens automatically
offline_manager.clear_old_requests(max_age_hours=72)
```

## Configuration Constants

In `utils/constants.py`:

```python
# Offline Queue Settings
OFFLINE_QUEUE_MAX_AGE_HOURS = 72  # 72 hours
OFFLINE_QUEUE_MAX_RETRIES = 3
OFFLINE_QUEUE_RETRY_INTERVAL_MS = 30000  # 30 seconds

# Connection Status Messages
CONNECTION_STATUS = {
    'online': '🟢 온라인',
    'offline': '🔴 오프라인',
    'connecting': '🟡 연결 중...',
}
```

## Testing Offline Mode

### Simulate Backend Down

```python
# Stop backend server to test offline mode
# Ctrl+C your FastAPI backend

# Then in the app:
1. Try to start a process (착공)
2. Observe offline message
3. Check queue count in status bar
4. Restart backend
5. Wait for auto-retry or click "재시도"
```

### Check Offline Queue

```bash
# View queued requests
ls offline_queue/
cat offline_queue/20250115_103000_123456.json
```

## Logging

All offline operations are logged:

```python
import logging

logger = logging.getLogger(__name__)

# Example log messages:
# INFO: OfflineManager initialized: offline_queue
# INFO: Queued offline request: 20250115_103000_123456.json
# INFO: Connection status changed: OFFLINE
# INFO: Connection restored, processing offline queue...
# INFO: Successfully processed: 20250115_103000_123456.json
# WARNING: Max retries reached for 20250115_103000_123456.json
```

## Best Practices

1. **Don't lose data**: Always queue critical operations (POST/PUT/DELETE)
2. **Preserve order**: Queue uses timestamp-based filenames
3. **Handle partial failures**: Each request is processed independently
4. **Test edge cases**: Network drops mid-request are handled gracefully
5. **Monitor queue size**: Show users how many pending requests exist
6. **Clear old data**: Automatic cleanup prevents queue bloat

## Troubleshooting

### Queue Not Processing

Check:
1. Is backend actually reachable?
2. Is RetryManager connected to OfflineManager?
3. Are there any errors in logs?

### Requests Failing After 3 Retries

- Check backend logs for actual errors
- Verify data format is correct
- Check authentication token validity

### Queue Growing Too Large

- Verify backend is running
- Check network connectivity
- Manual cleanup: Delete files in `offline_queue/`

## API Reference

### OfflineManager Methods

```python
offline_manager.queue_request(method, endpoint, data)
offline_manager.get_queued_requests()
offline_manager.remove_from_queue(filename)
offline_manager.set_connection_status(is_online)
offline_manager.get_queue_size()
offline_manager.clear_old_requests(max_age_hours)
```

### RetryManager Methods

```python
retry_manager.process_queue()
retry_manager.manual_retry()
retry_manager.clear_failed_requests()
```

### MainViewModel Methods

```python
viewmodel.manual_retry_offline_queue()
viewmodel.get_offline_queue_size()
viewmodel.is_online()
```

## Signals

### OfflineManager Signals

```python
connection_status_changed = Signal(bool)  # True=online, False=offline
offline_queue_changed = Signal(int)  # Queue size
```

### RetryManager Signals

```python
retry_success = Signal(str)  # filename
retry_failed = Signal(str, str)  # filename, error
retry_progress = Signal(int, int)  # current, total
```

### MainViewModel Signals

```python
connection_status_changed = Signal(bool)
offline_queue_changed = Signal(int)
```
