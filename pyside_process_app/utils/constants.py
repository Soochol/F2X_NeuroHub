"""Application constants"""

from enum import Enum

# Process IDs
class ProcessID(str, Enum):
    LASER_MARKING = "PROC-001"
    LMA_ASSEMBLY = "PROC-002"
    SENSOR_INSPECTION = "PROC-003"
    FIRMWARE_UPLOAD = "PROC-004"
    ROBOT_ASSEMBLY = "PROC-005"
    PERFORMANCE_TEST = "PROC-006"
    LABEL_PRINTING = "PROC-007"
    PACKAGING = "PROC-008"

# Process Names (Korean)
PROCESS_NAMES_KO = {
    1: "레이저 마킹",
    2: "LMA 조립",
    3: "센서 검사",
    4: "펌웨어 업로드",
    5: "로봇 조립",
    6: "성능검사",
    7: "라벨 프린팅",
    8: "포장+외관검사"
}

# Process Names (English)
PROCESS_NAMES_EN = {
    1: "Laser Marking",
    2: "LMA Assembly",
    3: "Sensor Inspection",
    4: "Firmware Upload",
    5: "Robot Assembly",
    6: "Performance Test",
    7: "Label Printing",
    8: "Packaging"
}

# API Endpoints
API_VERSION = "v1"
API_BASE = f"/api/{API_VERSION}"

# File Paths
DEFAULT_JSON_WATCH_PATH = "C:/neurohub_work"
PENDING_FOLDER = "pending"
COMPLETED_FOLDER = "completed"
ERROR_FOLDER = "error"

# UI Constants
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
REFRESH_INTERVAL_MS = 30000  # 30 seconds

# LOT Number Regex
LOT_NUMBER_PATTERN = r'^WF-KR-\d{6}[DN]-\d{3}$'

# Error Messages
ERROR_MESSAGES = {
    'connection_error': '🔴 백엔드 서버에 연결할 수 없습니다.\n오프라인 모드로 전환되었습니다.',
    'timeout_error': '⏱️ 서버 응답 시간이 초과되었습니다.\n잠시 후 다시 시도해주세요.',
    'authentication_error': '🔐 인증에 실패했습니다.\n다시 로그인해주세요.',
    'validation_error': '⚠️ 입력 데이터가 올바르지 않습니다.',
    'not_found_error': '🔍 요청한 데이터를 찾을 수 없습니다.',
    'server_error': '❌ 서버 오류가 발생했습니다.\n관리자에게 문의하세요.',
    'offline_mode': '📴 오프라인 모드입니다.\n데이터가 로컬에 저장되었습니다.',
    'queue_saved': '💾 요청이 큐에 저장되었습니다.\n연결 복구 시 자동으로 처리됩니다.',
}

# Connection Status Messages
CONNECTION_STATUS = {
    'online': '🟢 온라인',
    'offline': '🔴 오프라인',
    'connecting': '🟡 연결 중...',
}

# Offline Queue Settings
OFFLINE_QUEUE_MAX_AGE_HOURS = 72  # 72 hours
OFFLINE_QUEUE_MAX_RETRIES = 3
OFFLINE_QUEUE_RETRY_INTERVAL_MS = 30000  # 30 seconds
