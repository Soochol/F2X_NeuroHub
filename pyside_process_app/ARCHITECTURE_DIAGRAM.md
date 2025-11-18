# Work History Dialog Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Application                         │
│                      (main.py)                               │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Initializes
             ↓
┌────────────────────────────────────────────────────────────┐
│                    Services Layer                           │
├────────────────────────────────────────────────────────────┤
│  • APIClient                                                │
│  • AuthService                                              │
│  • ProcessService                                           │
│  • HistoryService  ← NEW                                    │
│  • FileWatcherService                                       │
└────────────┬───────────────────────────────────────────────┘
             │
             │ Injected into
             ↓
┌────────────────────────────────────────────────────────────┐
│                   MainWindow                                │
│                (views/main_window.py)                       │
├────────────────────────────────────────────────────────────┤
│  Constructor:                                               │
│    __init__(viewmodel, config, app_state, history_service) │
│                                                             │
│  Menu Items:                                                │
│    파일(File) > 종료(Exit)                                  │
│    보기(View) > 새로고침(Refresh) [F5]                      │
│              > 작업 이력(History) [Ctrl+H] ← NEW            │
│    설정(Settings) > 환경설정(Config)                        │
│    도움말(Help) > 정보(About)                               │
└────────────┬───────────────────────────────────────────────┘
             │
             │ Opens dialog
             ↓
┌────────────────────────────────────────────────────────────┐
│                  HistoryDialog                              │
│              (views/history_dialog.py)                      │
├────────────────────────────────────────────────────────────┤
│  Constructor:                                               │
│    __init__(history_service, config, app_state, parent)    │
│                                                             │
│  UI Components:                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Filter Section:                                      │  │
│  │  • Date Range: [Start Date] ~ [End Date]             │  │
│  │  • Result: [ComboBox: 전체/PASS/FAIL/REWORK]         │  │
│  │  • [🔍 조회] [📊 Excel 내보내기]                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  History Table (9 columns):                           │  │
│  │  ┌──────┬─────┬────┬────┬────┬────┬────┬────┬────┐  │  │
│  │  │일시  │LOT  │SN  │공정│작업│시간│결과│측정│비고│  │  │
│  │  ├──────┼─────┼────┼────┼────┼────┼────┼────┼────┤  │  │
│  │  │...   │...  │... │... │... │... │... │... │... │  │  │
│  │  └──────┴─────┴────┴────┴────┴────┴────┴────┴────┘  │  │
│  │  Features:                                            │  │
│  │  • Sortable columns                                   │  │
│  │  • Alternating row colors                             │  │
│  │  • Color-coded results (🟢🔴🔵)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Status: [총 X건 조회됨]                   [닫기]    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬───────────────────────────────────────────────┘
             │
             │ Uses
             ↓
┌────────────────────────────────────────────────────────────┐
│                 HistoryService                              │
│             (services/history_service.py)                   │
├────────────────────────────────────────────────────────────┤
│  Methods:                                                   │
│  • get_process_history(                                    │
│      process_id, operator_id,                              │
│      start_date, end_date,                                 │
│      result_filter, skip, limit)                           │
│  • get_lot_history(lot_id)                                 │
│  • get_serial_history(serial_id)                           │
└────────────┬───────────────────────────────────────────────┘
             │
             │ Calls API via
             ↓
┌────────────────────────────────────────────────────────────┐
│                     APIClient                               │
│              (services/api_client.py)                       │
├────────────────────────────────────────────────────────────┤
│  Methods:                                                   │
│  • get(endpoint, params)                                    │
│  • post(endpoint, data)                                     │
│  • put(endpoint, data)                                      │
│  • delete(endpoint)                                         │
│                                                             │
│  Features:                                                  │
│  • JWT authentication                                       │
│  • Retry logic                                              │
│  • Offline queue support                                    │
│  • Error handling                                           │
└────────────┬───────────────────────────────────────────────┘
             │
             │ HTTP Requests
             ↓
┌────────────────────────────────────────────────────────────┐
│              FastAPI Backend Server                         │
│                 (backend/app/main.py)                       │
├────────────────────────────────────────────────────────────┤
│  Endpoints:                                                 │
│  GET /api/v1/process-data                                   │
│  GET /api/v1/process-data/process/{process_id}             │
│  GET /api/v1/process-data/result/{result}                  │
│  GET /api/v1/process-data/operator/{operator_id}           │
│  GET /api/v1/process-data/date-range                       │
│  GET /api/v1/process-data/lot/{lot_id}                     │
│  GET /api/v1/process-data/serial/{serial_id}               │
└────────────┬───────────────────────────────────────────────┘
             │
             │ Database queries
             ↓
┌────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                        │
├────────────────────────────────────────────────────────────┤
│  Tables:                                                    │
│  • process_data (main table)                                │
│  • lots (related)                                           │
│  • serials (related)                                        │
│  • processes (related)                                      │
│  • users (related, for operator info)                       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Opening History Dialog

```
User Action (Ctrl+H or Menu)
    ↓
MainWindow.on_show_history()
    ↓
Create HistoryDialog(history_service, config, app_state, parent)
    ↓
HistoryDialog.__init__()
    ↓
setup_ui()  → Build UI components
    ↓
load_initial_data()  → Trigger initial query
    ↓
load_history()
```

### Querying History Data

```
User clicks [🔍 조회] button
    ↓
HistoryDialog.load_history()
    ├─ Disable search button
    ├─ Show "조회 중..." status
    ├─ Get filter values (dates, result)
    └─ Call HistoryService.get_process_history()
        ↓
    HistoryService determines endpoint based on filters
        ├─ process_id → /api/v1/process-data/process/{id}
        ├─ result_filter → /api/v1/process-data/result/{result}
        ├─ date_range → /api/v1/process-data/date-range
        └─ default → /api/v1/process-data
        ↓
    APIClient.get(endpoint, params)
        ├─ Add JWT token to headers
        ├─ Send HTTP GET request
        ├─ Handle retries if needed
        └─ Parse JSON response
        ↓
    Return List[Dict[str, Any]] to HistoryService
        ↓
    Return to HistoryDialog
        ↓
    HistoryDialog.update_table(history)
        ├─ Set table row count
        ├─ For each record:
        │   ├─ Parse datetime
        │   ├─ Extract nested objects (lot, serial, process, operator)
        │   ├─ Format duration
        │   ├─ Color-code result
        │   ├─ Truncate measurements
        │   └─ Add QTableWidgetItem to table
        ├─ Enable sorting
        └─ Update status: "총 X건 조회됨"
        ↓
    Enable search button
        ↓
    Display results to user
```

## Key Design Patterns

### 1. Dependency Injection
```python
# Services injected through constructor
class HistoryDialog(QDialog):
    def __init__(self, history_service, config, app_state, parent=None):
        self.history_service = history_service  # Injected
        self.config = config                    # Injected
        self.app_state = app_state              # Injected
```

### 2. Service Layer Pattern
```python
# Business logic in service layer
class HistoryService:
    def get_process_history(self, ...):
        # Determine endpoint
        # Make API call
        # Return clean data
```

### 3. Error Handling
```python
try:
    # API call
    response = self.api_client.get(endpoint, params)
except Exception as e:
    logger.error(f"Error: {e}")
    # Show user-friendly message
    QMessageBox.critical(self, "조회 실패", str(e))
finally:
    # Re-enable UI
    self.search_btn.setEnabled(True)
```

### 4. Defensive Programming
```python
# Safe nested object access
lot = item.get('lot', {})
if isinstance(lot, dict):
    lot_number = lot.get('lot_number', '-')
else:
    lot_number = '-'
```

### 5. UI State Management
```python
def load_history(self):
    # Disable UI during async operation
    self.search_btn.setEnabled(False)
    self.status_label.setText("조회 중...")

    try:
        # ... perform operation ...
    finally:
        # Re-enable UI
        self.search_btn.setEnabled(True)
```

## Integration Points

### 1. Main Application
- Creates HistoryService
- Passes to MainWindow

### 2. MainWindow
- Stores history_service reference
- Creates menu action
- Opens dialog on command

### 3. HistoryDialog
- Uses HistoryService for data
- Uses Config for process info
- Uses AppState for current user

### 4. HistoryService
- Uses APIClient for HTTP
- Handles filter logic
- Returns clean data

### 5. APIClient
- Manages authentication
- Handles network errors
- Provides retry logic

## Thread Safety

### Current Implementation
- **Single-threaded**: All operations on main Qt thread
- **Blocking UI**: Network calls block UI temporarily
- **Acceptable for small datasets**: Quick queries (<1 second)

### Future Enhancements
```python
# Use QThread for async loading
class HistoryLoadWorker(QThread):
    data_loaded = Signal(list)

    def run(self):
        history = self.history_service.get_process_history(...)
        self.data_loaded.emit(history)

# In dialog
worker = HistoryLoadWorker(self.history_service)
worker.data_loaded.connect(self.update_table)
worker.start()
```

## Configuration

### Config Parameters Used
```python
config.process_number  # Filter by current process
config.api_base_url    # (via APIClient in service)
```

### AppState Parameters Used
```python
app_state.current_user  # For user context (future use)
```

## Extension Points

### Adding New Filters
1. Add UI component in `setup_ui()`
2. Get value in `load_history()`
3. Add parameter to `HistoryService.get_process_history()`
4. Update endpoint selection logic

### Adding New Columns
1. Increase column count
2. Add header label
3. Set column resize mode
4. Add data extraction in `update_table()`

### Custom Endpoints
```python
# Add to HistoryService
def get_custom_history(self, custom_param):
    endpoint = f"/api/v1/custom-endpoint/{custom_param}"
    response = self.api_client.get(endpoint)
    return response
```

## Performance Considerations

### Current Limits
- Default: 100 records per query
- Maximum: 500 records (configurable)
- Table: Handles 500+ rows smoothly

### Optimization Strategies
1. **Pagination**: Load data in chunks
2. **Virtual Scrolling**: Only render visible rows
3. **Caching**: Cache recent queries
4. **Async Loading**: Background thread
5. **Progressive Loading**: Load while scrolling

## Security

### Authentication
- JWT token in APIClient
- Auto-attached to all requests
- Validated by backend

### Authorization
- Process-level access control (future)
- Role-based viewing (future)

### Data Protection
- No sensitive data cached
- Secure HTTPS connection (production)
