"""Process Data Service for 착공/완공 operations"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from requests.exceptions import ConnectionError, Timeout, HTTPError
import logging
from .api_client import APIClient

logger = logging.getLogger(__name__)


class ProcessService:
    """Service for process data operations"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def start_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """착공 등록 (Start process) - with offline queue support"""
        try:
            response = self.api_client.post('/api/v1/process-data', data)
            return response
        except (ConnectionError, Timeout, HTTPError) as e:
            # Error is already logged and queued by APIClient
            logger.warning(f"start_process failed, request queued: {e}")
            # Return a placeholder response for offline mode
            return {
                "id": -1,
                "status": "queued",
                "message": "요청이 오프라인 큐에 저장되었습니다"
            }

    def complete_process(self, process_data_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """완공 등록 (Complete process) - with offline queue support"""
        try:
            response = self.api_client.put(f'/api/v1/process-data/{process_data_id}', data)
            return response
        except (ConnectionError, Timeout, HTTPError) as e:
            # Error is already logged and queued by APIClient
            logger.warning(f"complete_process failed, request queued: {e}")
            # Return a placeholder response for offline mode
            return {
                "id": process_data_id,
                "status": "queued",
                "message": "요청이 오프라인 큐에 저장되었습니다"
            }

    def get_incomplete_processes(self) -> List[Dict[str, Any]]:
        """Get in-progress processes"""
        response = self.api_client.get('/api/v1/process-data/incomplete')
        return response

    def get_lot_by_number(self, lot_number: str) -> Optional[Dict[str, Any]]:
        """Get LOT by number"""
        try:
            response = self.api_client.get(f'/api/v1/lots/number/{lot_number}')
            return response
        except Exception:
            return None

    def get_lot_by_id(self, lot_id: int) -> Optional[Dict[str, Any]]:
        """Get LOT by ID"""
        try:
            response = self.api_client.get(f'/api/v1/lots/{lot_id}')
            return response
        except Exception:
            return None

    def get_daily_stats(self, process_id: int) -> Dict[str, Any]:
        """Get daily statistics for a process"""
        # This would call analytics endpoint
        # For now, return mock data structure
        return {
            'today_started': 0,
            'today_completed': 0,
            'today_passed': 0,
            'today_failed': 0,
            'in_progress': 0
        }

    def get_processes(self) -> List[Dict[str, Any]]:
        """Get all processes (1-8)"""
        response = self.api_client.get('/api/v1/processes/sequence')
        return response
