# Offline Mode & Error Handling Enhancement

## Overview

This enhancement adds robust offline mode support and user-friendly error handling to the PySide6 process tracking application. When the backend server is unreachable, the application gracefully degrades to offline mode, queues requests locally, and automatically retries when connection is restored.

## Key Features

### 1. Graceful Offline Handling
- Automatic detection of connection failures
- Local queue for failed requests
- Visual indicator in status bar (🟢 Online / 🔴 Offline)
- No data loss during network outages

### 2. Automatic Retry
- Auto-retry when connection restored
- Configurable retry limits (default: 3 attempts)
- Exponential backoff strategy
- Manual retry option via UI button

### 3. User-Friendly Error Messages
- Emoji-rich Korean error messages
- Specific errors for different scenarios:
  - 🔴 Connection errors
  - ⏱️ Timeout errors
  - 🔐 Authentication errors
  - ⚠️ Validation errors
  - 🔍 Not found errors
  - ❌ Server errors

### 4. Queue Management
- Persistent JSON-based queue
- Automatic cleanup of old requests (72 hours)
- Queue size display in UI
- Request ordering preservation

## Architecture

### Components

1. **OfflineManager** (`services/offline_manager.py`)
   - Manages offline queue
   - Tracks connection status
   - Emits Qt signals for UI updates

2. **RetryManager** (`services/retry_manager.py`)
   - Handles retry logic
   - Processes queued requests
   - Reports success/failure

3. **Enhanced APIClient** (`services/api_client.py`)
   - Automatic error detection
   - Request queuing on failure
   - Connection status updates

4. **Updated ViewModel** (`viewmodels/main_viewmodel.py`)
   - Integrates offline components
   - Enhanced error handling
   - Signal forwarding to UI

5. **Updated MainWindow** (`views/main_window.py`)
   - Connection status indicator
   - Queue size display
   - Manual retry button

## Installation

### Requirements

```bash
pip install PySide6 requests
```

### File Structure

```
pyside_process_app/
├── services/
│   ├── offline_manager.py        # NEW
│   ├── retry_manager.py          # NEW
│   ├── api_client.py             # MODIFIED
│   ├── process_service.py        # MODIFIED
│   └── __init__.py               # MODIFIED
├── viewmodels/
│   └── main_viewmodel.py         # MODIFIED
├── views/
│   └── main_window.py            # MODIFIED
├── utils/
│   └── constants.py              # MODIFIED
├── examples/
│   └── offline_mode_example.py   # NEW
├── OFFLINE_MODE_SETUP.md         # NEW
├── OFFLINE_MODE_IMPLEMENTATION_SUMMARY.md  # NEW
└── OFFLINE_MODE_README.md        # THIS FILE
```

## Quick Start

### Basic Setup

```python
from services import APIClient, OfflineManager, RetryManager

# 1. Create offline manager
offline_manager = OfflineManager(queue_path="offline_queue")

# 2. Create API client with offline support
api_client = APIClient(
    base_url="http://localhost:8000",
    offline_manager=offline_manager
)

# 3. Create retry manager
retry_manager = RetryManager(offline_manager, api_client)
```

### Full Application Setup

See `examples/offline_mode_example.py` for complete integration example.

## Usage

### Normal Operation (Online)

```
User Action → API Request → Backend
                                ↓
                           Success
                                ↓
                           UI Update
```

### Offline Operation

```
User Action → API Request → Connection Error
                                ↓
                          Queue Request
                                ↓
                       Show Offline Indicator
                                ↓
                       Display "큐: 1" in UI
```

### Connection Restored

```
Connection Restored → Emit Status Change
                            ↓
                      Auto-Retry Queue
                            ↓
                   ┌────────┴────────┐
                   ▼                 ▼
               Success           Failure
                   │                 │
          Remove from Queue   Increment Retry
                   │                 │
            UI Update          Max 3 Retries
```

## Testing

### Test Offline Mode

1. **Start Application**
   ```bash
   cd pyside_process_app
   python main.py
   ```

2. **Stop Backend Server**
   - Press Ctrl+C on your FastAPI backend
   - Or stop the backend service

3. **Observe Offline Behavior**
   - Status bar shows: 🔴 오프라인
   - Retry button appears
   - Try to perform action (착공/완공)
   - Error message displayed
   - Queue count increases: "큐: 1"

4. **Restart Backend**
   - Start your backend server again
   - Wait 2 seconds for auto-retry
   - Or click "재시도" button
   - Observe: 🟢 온라인
   - Queue count decreases: "큐: 0"
   - Retry button disappears

### Test Queue Persistence

```bash
# View queued requests
ls offline_queue/

# Inspect a queued request
cat offline_queue/20250115_103000_123456.json

# Output:
{
  "type": "POST",
  "endpoint": "/api/v1/process-data",
  "data": {...},
  "timestamp": "2025-01-15T10:30:00.123456",
  "retry_count": 0
}
```

### Test Standalone

```bash
cd pyside_process_app/examples
python offline_mode_example.py
```

Edit the file to uncomment `test_offline_mode()` for unit testing.

## Configuration

### In `utils/constants.py`

```python
# Queue Settings
OFFLINE_QUEUE_MAX_AGE_HOURS = 72  # Auto-cleanup after 72 hours
OFFLINE_QUEUE_MAX_RETRIES = 3     # Max retry attempts
OFFLINE_QUEUE_RETRY_INTERVAL_MS = 30000  # Health check interval

# Error Messages (customize as needed)
ERROR_MESSAGES = {
    'connection_error': '🔴 백엔드 서버에 연결할 수 없습니다.\n오프라인 모드로 전환되었습니다.',
    'timeout_error': '⏱️ 서버 응답 시간이 초과되었습니다.\n잠시 후 다시 시도해주세요.',
    # ... more messages
}
```

## API Reference

### OfflineManager

```python
class OfflineManager(QObject):
    # Signals
    connection_status_changed = Signal(bool)
    offline_queue_changed = Signal(int)

    # Methods
    def queue_request(request_type: str, endpoint: str, data: dict)
    def get_queued_requests() -> List[dict]
    def remove_from_queue(filename: str)
    def set_connection_status(is_online: bool)
    def get_queue_size() -> int
    def clear_old_requests(max_age_hours: int = 72)
```

### RetryManager

```python
class RetryManager(QObject):
    # Signals
    retry_success = Signal(str)
    retry_failed = Signal(str, str)
    retry_progress = Signal(int, int)

    # Methods
    def process_queue()
    def manual_retry()
    def clear_failed_requests() -> int
```

### Enhanced APIClient

```python
class APIClient:
    def __init__(base_url: str, offline_manager=None)
    def set_offline_manager(offline_manager)
    def health_check() -> bool
    # ... standard REST methods (get, post, put, delete)
```

### MainViewModel Extensions

```python
# New signals
connection_status_changed = Signal(bool)
offline_queue_changed = Signal(int)

# New methods
def manual_retry_offline_queue()
def get_offline_queue_size() -> int
def is_online() -> bool
```

## Error Handling Examples

### Connection Error

```python
try:
    result = api_client.post('/api/v1/process-data', data)
except ConnectionError as e:
    # Automatically handled:
    # 1. Request queued
    # 2. Status set to offline
    # 3. User sees: "🔴 백엔드 서버에 연결할 수 없습니다"
    pass
```

### Timeout Error

```python
try:
    result = api_client.get('/api/v1/lots/123')
except Timeout as e:
    # User sees: "⏱️ 서버 응답 시간이 초과되었습니다"
    pass
```

### HTTP Error

```python
try:
    result = api_client.post('/api/v1/process-data', invalid_data)
except HTTPError as e:
    # User sees specific message based on status code:
    # 401: "🔐 인증에 실패했습니다"
    # 404: "🔍 요청한 리소스를 찾을 수 없습니다"
    # 422: "⚠️ 입력 데이터가 올바르지 않습니다"
    # 5xx: "❌ 서버 오류가 발생했습니다"
    pass
```

## Logging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Log Output Examples

```
2025-01-15 10:30:00 - services.offline_manager - INFO - OfflineManager initialized: offline_queue
2025-01-15 10:30:15 - services.api_client - ERROR - POST /api/v1/process-data failed: Connection refused
2025-01-15 10:30:15 - services.offline_manager - INFO - Queued offline request: 20250115_103015_123456.json
2025-01-15 10:30:15 - services.offline_manager - INFO - Connection status changed: OFFLINE
2025-01-15 10:32:00 - services.offline_manager - INFO - Connection status changed: ONLINE
2025-01-15 10:32:02 - services.retry_manager - INFO - Connection restored, scheduling offline queue processing...
2025-01-15 10:32:04 - services.retry_manager - INFO - Processing 1 queued requests...
2025-01-15 10:32:04 - services.retry_manager - INFO - Successfully processed: 20250115_103015_123456.json
```

## Troubleshooting

### Problem: Queue Not Processing

**Symptoms**: Requests stay in queue after connection restored

**Solutions**:
1. Check if backend is actually reachable
2. Verify RetryManager is initialized
3. Check logs for errors
4. Try manual retry button

### Problem: Requests Failing After 3 Retries

**Symptoms**: Requests removed from queue without success

**Solutions**:
1. Check backend logs for actual errors
2. Verify data format is correct
3. Check authentication token validity
4. Review endpoint URLs

### Problem: Queue Growing Too Large

**Symptoms**: Many files in offline_queue/

**Solutions**:
1. Verify backend is running correctly
2. Check network connectivity
3. Run manual cleanup:
   ```python
   offline_manager.clear_old_requests(max_age_hours=24)
   ```
4. Delete old files manually:
   ```bash
   rm offline_queue/*.json
   ```

### Problem: UI Not Updating

**Symptoms**: Status indicator not changing

**Solutions**:
1. Verify signal connections in MainWindow
2. Check ViewModel initialization
3. Ensure offline_manager and retry_manager are passed to ViewModel
4. Check for exceptions in logs

## Performance Considerations

### Queue Size

- Each queued request is a JSON file (~1-5KB)
- 1000 requests ≈ 1-5MB disk space
- Auto-cleanup after 72 hours prevents bloat

### Retry Interval

- Default: 30 seconds (health check)
- Adjust in constants.py if needed
- Lower = faster recovery, higher CPU
- Higher = slower recovery, lower CPU

### Memory Usage

- OfflineManager: ~1MB baseline
- RetryManager: ~500KB baseline
- Queue processing: ~100KB per request

## Best Practices

1. **Always Initialize Offline Manager**
   ```python
   offline_manager = OfflineManager(queue_path="offline_queue")
   api_client = APIClient(base_url=url, offline_manager=offline_manager)
   ```

2. **Connect All Signals**
   ```python
   offline_manager.connection_status_changed.connect(handler)
   offline_manager.offline_queue_changed.connect(handler)
   retry_manager.retry_success.connect(handler)
   retry_manager.retry_failed.connect(handler)
   ```

3. **Handle Offline Responses**
   ```python
   result = process_service.start_process(data)
   if result.get('status') == 'queued':
       # Offline mode - inform user
       show_message("요청이 큐에 저장되었습니다")
   ```

4. **Monitor Queue Size**
   ```python
   queue_size = offline_manager.get_queue_size()
   if queue_size > 100:
       logger.warning(f"Large queue size: {queue_size}")
   ```

5. **Regular Cleanup**
   ```python
   # Run daily
   offline_manager.clear_old_requests(max_age_hours=72)
   ```

## Security Considerations

1. **Queue Files**
   - Stored in plain JSON
   - May contain sensitive data
   - Secure file permissions recommended
   - Consider encryption for sensitive environments

2. **Authentication Tokens**
   - Tokens stored in queued requests
   - May expire before retry
   - Handle 401 errors gracefully

3. **Data Validation**
   - Validate before queuing
   - Re-validate before retry
   - Prevent malformed data propagation

## Future Enhancements

Potential improvements:

1. **Queue Encryption**
   - Encrypt sensitive data in queue
   - Use application key

2. **Priority Queue**
   - Different priorities for different request types
   - Process high-priority first

3. **Network Quality Monitoring**
   - Track connection quality
   - Adjust retry strategy based on quality

4. **Queue Analytics**
   - Dashboard for queue metrics
   - Success/failure rates
   - Average retry time

5. **Sync Conflict Resolution**
   - Handle data conflicts after long offline periods
   - User-facing conflict resolution UI

## Support

For issues or questions:

1. Check logs in `app.log`
2. Review queue files in `offline_queue/`
3. Read `OFFLINE_MODE_SETUP.md` for integration help
4. See `OFFLINE_MODE_IMPLEMENTATION_SUMMARY.md` for architecture details

## License

Same as main project.

## Changelog

### Version 1.0.0 (2025-01-15)
- Initial implementation
- Offline queue management
- Automatic retry
- UI indicators
- User-friendly error messages
- Comprehensive documentation
