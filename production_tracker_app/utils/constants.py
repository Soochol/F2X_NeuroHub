"""
Constants for Production Tracker App.
"""

# API Endpoints
API_LOGIN = "/api/v1/auth/login"
API_ME = "/api/v1/auth/me"
API_PROCESS_START = "/api/v1/process/start"
API_PROCESS_COMPLETE = "/api/v1/process/complete"
API_ANALYTICS_DAILY = "/api/v1/analytics/daily"

# File Watcher
WATCH_SCAN_INTERVAL_MS = 3000  # 3 seconds
FILE_PATTERN = "*.json"

# UI Constants
WINDOW_MIN_WIDTH = 400
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 400
WINDOW_DEFAULT_HEIGHT = 600

# Stats Refresh
STATS_REFRESH_INTERVAL_MS = 5000  # 5 seconds

# LOT Number Pattern
LOT_PATTERN = r'^[A-Z]{2}-[A-Z]{2}-\d{6}[DN]-\d{3}$'

# Colors
COLOR_SUCCESS = "#22c55e"
COLOR_ERROR = "#ef4444"
COLOR_WARNING = "#f59e0b"
COLOR_INFO = "#3b82f6"
COLOR_ONLINE = "#10b981"
COLOR_OFFLINE = "#ef4444"

# Status Messages
MSG_WAITING_BARCODE = "바코드 스캔 대기중..."
MSG_PROCESSING = "처리 중..."
MSG_WORK_STARTED = "착공 등록 완료"
MSG_WORK_COMPLETED = "완공 처리 완료"
MSG_CONNECTION_ONLINE = "🟢 온라인"
MSG_CONNECTION_OFFLINE = "🔴 오프라인"
