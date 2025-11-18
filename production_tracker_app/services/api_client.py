"""
Simplified REST API Client with JWT authentication support.
"""
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ConnectionError, Timeout, HTTPError
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Simplified API client with JWT authentication and retry logic."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry strategy."""
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

    def set_token(self, token: str):
        """Set JWT token for authenticated requests."""
        self.token = token

    def clear_token(self):
        """Clear JWT token."""
        self.token = None

    def _headers(self) -> Dict[str, str]:
        """Get headers with JWT token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """GET request with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, headers=self._headers(), params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"백엔드 서버에 연결할 수 없습니다: {self.base_url}")
        except Timeout as e:
            logger.error(f"Timeout error: {e}")
            raise Timeout("서버 응답 시간이 초과되었습니다 (10초)")
        except HTTPError as e:
            logger.error(f"HTTP error: {e}")
            self._handle_http_error(e, endpoint)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def post(self, endpoint: str, data: Dict) -> Any:
        """POST request with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, headers=self._headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"백엔드 서버에 연결할 수 없습니다: {self.base_url}")
        except Timeout as e:
            logger.error(f"Timeout error: {e}")
            raise Timeout("서버 응답 시간이 초과되었습니다 (10초)")
        except HTTPError as e:
            logger.error(f"HTTP error: {e}")
            self._handle_http_error(e, endpoint)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def _handle_http_error(self, error: HTTPError, endpoint: str):
        """Handle HTTP errors with friendly messages."""
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
