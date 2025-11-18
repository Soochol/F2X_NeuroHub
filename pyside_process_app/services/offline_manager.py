"""Offline Manager - Manages offline mode and request queuing"""

from PySide6.QtCore import QObject, Signal, QTimer
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OfflineManager(QObject):
    """오프라인 모드 관리 - 네트워크 연결 실패 시 로컬 큐에 저장"""

    connection_status_changed = Signal(bool)  # True=online, False=offline
    offline_queue_changed = Signal(int)  # Queue size

    def __init__(self, queue_path: str = "offline_queue"):
        super().__init__()
        self.queue_dir = Path(queue_path)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.is_online = True

        # Health check timer
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self._check_connection)
        self.health_check_timer.start(30000)  # Check every 30 seconds

        logger.info(f"OfflineManager initialized: {self.queue_dir}")

        # Emit initial queue size
        self._update_queue_size()

    def queue_request(self, request_type: str, endpoint: str, data: Dict[str, Any]):
        """네트워크 실패 시 요청을 큐에 저장"""
        queue_item = {
            "type": request_type,
            "endpoint": endpoint,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "retry_count": 0
        }

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        filepath = self.queue_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(queue_item, f, ensure_ascii=False, indent=2)

            logger.info(f"Queued offline request: {filename}")
            self._update_queue_size()
        except Exception as e:
            logger.error(f"Failed to queue request: {e}")

    def get_queued_requests(self) -> List[Dict]:
        """큐에 저장된 요청 목록 조회"""
        queued = []
        for file in sorted(self.queue_dir.glob("*.json")):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_filename'] = file.name
                    queued.append(data)
            except Exception as e:
                logger.error(f"Failed to read queued file {file}: {e}")
        return queued

    def remove_from_queue(self, filename: str):
        """큐에서 요청 제거 (성공적으로 처리됨)"""
        filepath = self.queue_dir / filename
        try:
            filepath.unlink()
            logger.info(f"Removed from queue: {filename}")
            self._update_queue_size()
        except Exception as e:
            logger.error(f"Failed to remove from queue: {e}")

    def increment_retry_count(self, filename: str):
        """재시도 횟수 증가"""
        filepath = self.queue_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data['retry_count'] = data.get('retry_count', 0) + 1
            data['last_retry'] = datetime.now().isoformat()

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Incremented retry count for {filename}: {data['retry_count']}")
        except Exception as e:
            logger.error(f"Failed to increment retry count: {e}")

    def set_connection_status(self, is_online: bool):
        """연결 상태 변경"""
        if self.is_online != is_online:
            self.is_online = is_online
            self.connection_status_changed.emit(is_online)
            status = "ONLINE" if is_online else "OFFLINE"
            logger.info(f"Connection status changed: {status}")

    def _check_connection(self):
        """연결 상태 확인 (placeholder - APIClient에서 호출됨)"""
        # This will be called by APIClient after each request
        pass

    def _update_queue_size(self):
        """큐 크기 업데이트"""
        size = len(list(self.queue_dir.glob("*.json")))
        self.offline_queue_changed.emit(size)

    def get_queue_size(self) -> int:
        """현재 큐 크기 반환"""
        return len(list(self.queue_dir.glob("*.json")))

    def clear_old_requests(self, max_age_hours: int = 72):
        """오래된 큐 요청 정리 (72시간 이상)"""
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)
        removed_count = 0

        for file in self.queue_dir.glob("*.json"):
            try:
                if file.stat().st_mtime < cutoff:
                    file.unlink()
                    removed_count += 1
                    logger.info(f"Removed old queued request: {file.name}")
            except Exception as e:
                logger.error(f"Failed to remove old request {file}: {e}")

        if removed_count > 0:
            self._update_queue_size()
            logger.info(f"Cleaned up {removed_count} old queued requests")
