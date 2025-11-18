"""REST API Client with JWT authentication support and offline mode"""

import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ConnectionError, Timeout, HTTPError
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Base API client with JWT authentication, retry logic, and offline support"""

    def __init__(self, base_url: str = "http://localhost:8000", offline_manager=None):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = self._create_session()
        self.offline_manager = offline_manager
        self._last_connection_status = True

    def _create_session(self) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def set_offline_manager(self, offline_manager):
        """Set offline manager for queue handling"""
        self.offline_manager = offline_manager

    def set_token(self, token: str):
        """Set JWT token for authenticated requests"""
        self.token = token

    def clear_token(self):
        """Clear JWT token"""
        self.token = None

    def _headers(self) -> Dict[str, str]:
        """Get headers with JWT token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _update_connection_status(self, is_online: bool):
        """Update connection status if changed"""
        if self.offline_manager and is_online != self._last_connection_status:
            self.offline_manager.set_connection_status(is_online)
            self._last_connection_status = is_online

    def _handle_request_error(self, method: str, endpoint: str, data: Optional[Dict], error: Exception):
        """Handle request errors with offline queue support"""
        logger.error(f"{method} {endpoint} failed: {error}")

        # Update connection status to offline
        self._update_connection_status(False)

        # Queue request if offline manager is available and method is not GET
        if self.offline_manager and method in ['POST', 'PUT', 'DELETE']:
            logger.info(f"Queueing {method} request: {endpoint}")
            self.offline_manager.queue_request(method, endpoint, data or {})

        # Re-raise with more context
        if isinstance(error, ConnectionError):
            raise ConnectionError(f"백엔드 서버에 연결할 수 없습니다: {self.base_url}")
        elif isinstance(error, Timeout):
            raise Timeout(f"서버 응답 시간이 초과되었습니다 (10초)")
        elif isinstance(error, HTTPError):
            status_code = error.response.status_code if hasattr(error, 'response') else None
            if status_code == 401:
                raise HTTPError("인증에 실패했습니다. 다시 로그인해주세요.")
            elif status_code == 404:
                raise HTTPError(f"요청한 리소스를 찾을 수 없습니다: {endpoint}")
            elif status_code == 422:
                raise HTTPError("입력 데이터가 올바르지 않습니다.")
            elif status_code and 500 <= status_code < 600:
                raise HTTPError(f"서버 오류가 발생했습니다 (HTTP {status_code})")
            else:
                raise error
        else:
            raise error

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """GET request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, headers=self._headers(), params=params, timeout=10)
            response.raise_for_status()
            # Success - update status to online
            self._update_connection_status(True)
            return response.json()
        except Exception as e:
            self._handle_request_error('GET', endpoint, params, e)

    def post(self, endpoint: str, data: Dict) -> Any:
        """POST request with error handling and offline queue"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, headers=self._headers(), json=data, timeout=10)
            response.raise_for_status()
            # Success - update status to online
            self._update_connection_status(True)
            return response.json()
        except Exception as e:
            self._handle_request_error('POST', endpoint, data, e)

    def put(self, endpoint: str, data: Dict) -> Any:
        """PUT request with error handling and offline queue"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, headers=self._headers(), json=data, timeout=10)
            response.raise_for_status()
            # Success - update status to online
            self._update_connection_status(True)
            return response.json()
        except Exception as e:
            self._handle_request_error('PUT', endpoint, data, e)

    def delete(self, endpoint: str) -> Any:
        """DELETE request with error handling and offline queue"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            # Success - update status to online
            self._update_connection_status(True)
            return response.json() if response.content else None
        except Exception as e:
            self._handle_request_error('DELETE', endpoint, None, e)

    def health_check(self) -> bool:
        """Check if backend is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            is_healthy = response.status_code == 200
            self._update_connection_status(is_healthy)
            return is_healthy
        except Exception:
            self._update_connection_status(False)
            return False