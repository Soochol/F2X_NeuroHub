# Threading Implementation - Production Tracker App

## Overview

This document describes the QThread-based threading implementation added to the production_tracker_app to prevent UI blocking during network and database operations.

## Problem Statement

The app was making synchronous API calls and database operations that could freeze the UI, resulting in poor user experience. Network timeouts could cause the entire application to become unresponsive for up to 10 seconds.

## Solution

Implemented QThread workers for all blocking operations with signal/slot pattern for thread-safe communication.

## Architecture

### 1. Worker Classes (`services/workers.py`)

All worker classes follow this pattern:

```python
class APIWorker(QThread):
    result_ready = Signal(object)  # Success signal
    error_occurred = Signal(str)   # Error signal

    def run(self):
        # Perform blocking operation
        # Emit result via signals

    def cancel(self):
        # Allow graceful cancellation
```

#### Worker Types

1. **LoginWorker** - Handles authentication
   - Signals: `login_success`, `login_failed`
   - Used by: `AuthService`

2. **StartWorkWorker** - Handles work start operations
   - Signals: `work_started`, `work_failed`
   - Used by: `WorkService`

3. **CompleteWorkWorker** - Handles work completion
   - Signals: `work_completed`, `work_failed`
   - Used by: `WorkService`

4. **StatsWorker** - Handles statistics fetching
   - Signals: `stats_ready` (no failure signal - returns defaults on error)
   - Used by: `WorkService`

5. **TokenValidationWorker** - Handles token validation
   - Signals: `validation_success`, `validation_failed`
   - Used by: `AuthService`

### 2. Service Layer Updates

#### WorkService (`services/work_service.py`)

**Before:**
```python
def start_work(self, lot_number: str, worker_id: str) -> Dict:
    response = self.api_client.post("/api/v1/process/start", data)
    return response  # BLOCKING
```

**After:**
```python
def start_work(self, lot_number: str, worker_id: str):
    worker = StartWorkWorker(self.api_client, lot_number, worker_id, self.config)
    worker.work_started.connect(self._on_work_started)
    worker.work_failed.connect(self._on_work_failed)
    worker.start()  # NON-BLOCKING
```

#### AuthService (`services/auth_service.py`)

**Before:**
```python
def login(self, username: str, password: str) -> bool:
    response = self.api_client.post('/api/v1/auth/login', {...})
    return True  # BLOCKING
```

**After:**
```python
def login(self, username: str, password: str):
    worker = LoginWorker(self.api_client, username, password)
    worker.login_success.connect(self._on_login_success)
    worker.login_failed.connect(self._on_login_failed)
    worker.start()  # NON-BLOCKING
```

### 3. ViewModel Integration (`viewmodels/main_viewmodel.py`)

The MainViewModel orchestrates threaded operations:

```python
def _connect_signals(self):
    # Connect to service signals
    self.work_service.work_started.connect(self.on_work_started_success)
    self.work_service.work_completed.connect(self.on_work_completed_success)
    self.work_service.stats_ready.connect(self.on_stats_ready)
    self.work_service.error_occurred.connect(self.on_work_service_error)

def on_barcode_scanned(self, lot_number: str):
    # Initiate threaded operation
    self.work_service.start_work(lot_number, worker_id)
    # UI remains responsive while operation runs

def on_work_started_success(self, response: dict):
    # Handle result when thread completes
    self.work_started.emit(self.current_lot)
    self.lot_updated.emit({...})
```

### 4. View Layer Updates

#### MainWindow (`views/main_window.py`)

Added proper cleanup in closeEvent:

```python
def closeEvent(self, event):
    if reply == QMessageBox.Yes:
        # Clean up ViewModel resources (stops timers, cancels threads)
        self.viewmodel.cleanup()
        event.accept()
```

#### LoginDialog (`views/login_dialog.py`)

Updated to use threaded login:

```python
def on_login(self):
    # Disable button while login in progress
    self.login_button.setEnabled(False)
    self.login_button.setText("로그인 중...")

    # Initiate threaded login
    self.auth_service.login(username, password)

def on_login_success(self, user_data: dict):
    # Re-enable button
    self.login_button.setEnabled(True)
    self.accept()
```

## Signal Flow

### Work Start Flow

```
User scans barcode
    ↓
MainWindow.eventFilter() captures key
    ↓
BarcodeService.process_key()
    ↓
BarcodeService.barcode_valid.emit(lot_number)
    ↓
MainViewModel.on_barcode_scanned(lot_number)
    ↓
WorkService.start_work(lot_number, worker_id)
    ↓
StartWorkWorker.start() [BACKGROUND THREAD]
    ↓
StartWorkWorker.work_started.emit(response)
    ↓
WorkService._on_work_started(response)
    ↓
WorkService.work_started.emit(response)
    ↓
MainViewModel.on_work_started_success(response)
    ↓
MainViewModel.work_started.emit(lot_number)
    ↓
MainWindow.on_work_started(lot_number)
    ↓
UI updated
```

## Thread Safety

### Safe Practices

1. **No direct UI updates from worker threads** - All UI updates via signals
2. **Worker lifecycle management** - Workers tracked and cleaned up properly
3. **Cancellation support** - All workers support graceful cancellation
4. **Proper cleanup** - Workers deleted via `deleteLater()` after completion

### Cleanup Pattern

```python
class WorkService(QObject):
    def __init__(self):
        self._active_workers = []

    def start_work(self, ...):
        worker = StartWorkWorker(...)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()

    def _cleanup_worker(self, worker):
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()

    def cancel_all_operations(self):
        for worker in self._active_workers[:]:
            if hasattr(worker, 'cancel'):
                worker.cancel()
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)
        self._active_workers.clear()
```

## Benefits

### 1. UI Responsiveness
- Network operations no longer freeze the UI
- User can continue interacting with the app during API calls
- Timeouts don't cause complete application hangs

### 2. Better Error Handling
- Errors communicated via signals
- UI can display loading states
- Graceful degradation on network failures

### 3. Improved UX
- Login button shows "로그인 중..." during authentication
- Stats refresh happens in background
- File watcher already uses Qt's built-in threading

### 4. Clean Shutdown
- All workers cancelled on app close
- No zombie threads
- Proper resource cleanup

## Testing

### Manual Testing

Run the test script:
```bash
python production_tracker_app/test_threading.py
```

The test widget demonstrates:
1. UI counter keeps incrementing during network operations
2. Multiple operations can run concurrently
3. Proper cleanup on close

### Integration Testing

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. Run the production tracker app:
   ```bash
   python production_tracker_app/main.py
   ```

3. Test scenarios:
   - Login (watch button state)
   - Scan barcode (UI should not freeze)
   - Watch stats update in background
   - Close app (check console for cleanup logs)

## Performance Considerations

### Thread Pool Size

- Each operation creates a new QThread
- QThread is lightweight (reuses OS thread pool)
- Workers are cleaned up after completion
- Maximum concurrent operations limited by service

### Memory Management

- Workers use `deleteLater()` for Qt-safe deletion
- Active workers tracked in lists
- Cleanup removes references
- Qt handles actual memory deallocation

## Future Enhancements

1. **Thread Pool Pattern**
   - Could implement QThreadPool for better resource management
   - Would reduce thread creation overhead

2. **Operation Queue**
   - Queue operations when network is slow
   - Prevent overlapping start_work calls

3. **Progress Signals**
   - Add progress reporting for long operations
   - Show progress bars during completion

4. **Retry Logic**
   - Automatic retry for failed operations
   - Exponential backoff

5. **Operation Timeout**
   - Individual timeout per operation type
   - Cancel operation after timeout

## Troubleshooting

### Issue: UI still freezes

**Cause:** Worker not being used for operation
**Solution:** Check that service method uses worker, not direct API call

### Issue: Signals not received

**Cause:** Worker destroyed before signal emission
**Solution:** Ensure worker is kept alive until finished signal

### Issue: Memory leak

**Cause:** Workers not being cleaned up
**Solution:** Check that `finished` signal is connected to cleanup

### Issue: Multiple error messages

**Cause:** Overlapping operations
**Solution:** Disable UI elements during operation

## References

- Qt Threading: https://doc.qt.io/qt-6/thread-basics.html
- QThread: https://doc.qt.io/qt-6/qthread.html
- Signals & Slots: https://doc.qt.io/qt-6/signalsandslots.html

## File Changes Summary

### New Files
- `services/workers.py` - All QThread worker classes

### Modified Files
- `services/work_service.py` - Threaded API operations
- `services/auth_service.py` - Threaded authentication
- `viewmodels/main_viewmodel.py` - Signal integration and cleanup
- `views/main_window.py` - Cleanup in closeEvent
- `views/login_dialog.py` - Threaded login

### Key Metrics
- Lines of code added: ~450
- Number of worker classes: 5
- Services updated: 2 (WorkService, AuthService)
- Blocking operations eliminated: 6
  - login
  - token validation
  - start_work
  - complete_work
  - get_today_stats
  - (file watching already threaded via QFileSystemWatcher)
