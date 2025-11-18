# Quick Start: Work History Dialog

## For Developers

### File Locations

```
pyside_process_app/
├── services/
│   └── history_service.py          # NEW: History data service
├── views/
│   ├── history_dialog.py           # NEW: History dialog UI
│   └── main_window.py              # MODIFIED: Added menu item
└── main.py                         # MODIFIED: Initialize service
```

### Integration Steps

**1. Service is already initialized in main.py:**
```python
history_service = HistoryService(api_client)
```

**2. MainWindow receives it:**
```python
main_window = MainWindow(main_viewmodel, config, app_state, history_service)
```

**3. Open dialog from menu or shortcut:**
- Menu: View → 작업 이력
- Keyboard: `Ctrl+H`

### Quick Code Reference

**Open dialog programmatically:**
```python
from views.history_dialog import HistoryDialog

dialog = HistoryDialog(history_service, config, app_state, parent=self)
dialog.exec()
```

**Use service directly:**
```python
from services.history_service import HistoryService

# Get last 7 days of process 1
history = history_service.get_process_history(
    process_id=1,
    start_date=date.today() - timedelta(days=7),
    end_date=date.today(),
    limit=100
)

# Get LOT history
lot_history = history_service.get_lot_history(lot_id=123)

# Get serial history
serial_history = history_service.get_serial_history(serial_id=456)
```

## For Users

### How to View Work History

1. **Launch the application**
   - Run `python main.py`
   - Login with your credentials

2. **Open Work History Dialog**
   - **Option 1**: Click menu → View → 작업 이력
   - **Option 2**: Press `Ctrl+H` on keyboard

3. **Filter the data**
   - **기간** (Period): Select start and end dates
   - **결과** (Result): Choose ALL, PASS, FAIL, or REWORK
   - Click **🔍 조회** (Search) button

4. **View results**
   - Click column headers to sort
   - Results show:
     - Date/time of work
     - LOT and Serial numbers
     - Process name
     - Operator name
     - Duration
     - Result (color-coded)
     - Measurements
     - Notes

5. **Export (Coming Soon)**
   - Click **📊 Excel 내보내기** button
   - (Feature under development)

### Color Coding

- 🟢 **Green** = PASS (합격)
- 🔴 **Red** = FAIL (불합격)
- 🔵 **Blue** = REWORK (재작업)

## Backend Requirements

### Required API Endpoints

Your FastAPI backend must implement these endpoints:

```python
# Main endpoint with pagination
GET /api/v1/process-data?skip=0&limit=100

# Filter by process
GET /api/v1/process-data/process/{process_id}

# Filter by result
GET /api/v1/process-data/result/{result}  # PASS, FAIL, REWORK

# Filter by operator
GET /api/v1/process-data/operator/{operator_id}

# Filter by date range
GET /api/v1/process-data/date-range?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z

# LOT history
GET /api/v1/process-data/lot/{lot_id}

# Serial history
GET /api/v1/process-data/serial/{serial_id}
```

### Expected Response

Each endpoint should return a list of process data:

```json
[
  {
    "id": 1,
    "lot_id": 1,
    "serial_id": 1,
    "process_id": 1,
    "operator_id": 1,
    "data_level": "SERIAL",
    "result": "PASS",
    "started_at": "2024-01-15T09:30:00Z",
    "completed_at": "2024-01-15T09:45:00Z",
    "duration_seconds": 900,
    "measurements": {"temp": 25.5, "pressure": 101.3},
    "notes": "Normal operation",
    "lot": {"lot_number": "LOT-2024-001"},
    "serial": {"serial_number": "SN-12345"},
    "process": {"process_name_ko": "검사"},
    "operator": {"username": "operator1", "full_name": "김작업"}
  }
]
```

## Troubleshooting

### Dialog doesn't open
- Check if HistoryService is initialized in main.py
- Verify MainWindow receives history_service parameter
- Check console for import errors

### No data displayed
- Verify backend is running (http://localhost:8000)
- Check backend logs for API errors
- Try different date range or filters
- Look for error message dialog

### Table shows dashes (-)
- Backend is not returning nested objects (lot, serial, process, operator)
- Check backend endpoint responses include related entities
- Verify database relationships are properly loaded

### Import errors
```bash
# Install dependencies
cd pyside_process_app
pip install -r requirements.txt
```

### Network errors
- Check API_BASE_URL in config
- Ensure backend is running
- Test with: `curl http://localhost:8000/health`

## Testing Checklist

Before deployment:

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run import test: `python test_history_imports.py`
- [ ] Start backend server
- [ ] Launch application: `python main.py`
- [ ] Login successfully
- [ ] Open history dialog (Ctrl+H)
- [ ] Test date range filter
- [ ] Test result filter (PASS/FAIL/REWORK)
- [ ] Verify data displays correctly
- [ ] Test column sorting
- [ ] Check color coding
- [ ] Verify error handling (disconnect backend)

## Next Steps

1. **Test with real backend data**
2. **Implement Excel export**
3. **Add detail view on row double-click**
4. **Add pagination for large datasets**
5. **Implement chart/analytics view**

## Support

For issues or questions:
1. Check `HISTORY_DIALOG_IMPLEMENTATION.md` for detailed documentation
2. Review code comments in `history_service.py` and `history_dialog.py`
3. Check application logs in `logs/` directory
4. Verify backend API responses with Postman or curl
