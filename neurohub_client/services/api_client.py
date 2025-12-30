"""
Simplified REST API Client with JWT authentication support.
"""
import logging
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout, HTTPError
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIClient:
    """Simplified API client with JWT authentication and retry logic."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self._base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = self._create_session()

    def get_base_url(self) -> str:
        """Get the API base URL."""
        return self._base_url

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

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET request with error handling."""
        url = f"{self._base_url}{endpoint}"

        # Debug logging - request details
        logger.debug(f"=== API GET Request ===")
        logger.debug(f"URL: {url}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Headers: {self._headers()}")

        try:
            response = self.session.get(url, headers=self._headers(), params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Response Status: {response.status_code}")
            logger.debug(f"Response Data: {result}")
            return result
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"백엔드 서버에 연결할 수 없습니다: {self._base_url}")
        except Timeout as e:
            logger.error(f"Timeout error: {e}")
            raise Timeout("서버 응답 시간이 초과되었습니다 (10초)")
        except HTTPError as e:
            logger.error(f"HTTP error: {e}")
            self._handle_http_error(e, endpoint)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """POST request with error handling."""
        url = f"{self._base_url}{endpoint}"

        # Debug logging - request details
        logger.debug(f"=== API POST Request ===")
        logger.debug(f"URL: {url}")
        logger.debug(f"Data: {data}")
        logger.debug(f"Headers: {self._headers()}")

        try:
            response = self.session.post(url, json=data, headers=self._headers(), timeout=10)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Response Status: {response.status_code}")
            logger.debug(f"Response Data: {result}")
            return result
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"백엔드 서버에 연결할 수 없습니다: {self._base_url}")
        except Timeout as e:
            logger.error(f"Timeout error: {e}")
            raise Timeout("서버 응답 시간이 초과되었습니다 (10초)")
        except HTTPError as e:
            logger.error(f"HTTP error: {e}")
            self._handle_http_error(e, endpoint)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def _extract_error_detail(self, error: HTTPError) -> str:
        """
        Extract detailed error message from HTTP error response.

        Tries to parse StandardErrorResponse or FastAPI HTTPException format.
        Falls back to response text if JSON parsing fails.
        """
        if not hasattr(error, 'response'):
            return str(error)

        try:
            error_json = error.response.json()

            # StandardErrorResponse format (backend global handler)
            if 'message' in error_json:
                detail_msg = error_json['message']
                # Add details if available
                if 'details' in error_json and error_json['details']:
                    details = error_json['details']
                    if isinstance(details, list) and details:
                        # Format field errors
                        field_errors = [f"{d.get('field', '?')}: {d.get('message', '?')}" for d in details[:3]]
                        detail_msg += f" ({', '.join(field_errors)})"
                return detail_msg

            # FastAPI HTTPException format
            if 'detail' in error_json:
                return error_json['detail']
        except Exception as parse_err:
            logger.debug(f"Failed to parse error response JSON: {parse_err}")

        # Fallback to response text (truncated)
        try:
            return error.response.text[:200]
        except Exception:
            return str(error)

    def _handle_http_error(self, error: HTTPError, endpoint: str):
        """Handle HTTP errors with friendly messages."""
        status_code = error.response.status_code if hasattr(error, 'response') else None

        # Extract detailed error message from response
        error_detail = self._extract_error_detail(error)

        # Log the full error for debugging
        logger.error(f"HTTP {status_code} on {endpoint}: {error_detail}")

        # Map status codes to user-friendly messages
        if status_code == 400:
            user_msg = f"요청이 올바르지 않습니다: {error_detail}"
        elif status_code == 401:
            user_msg = "인증에 실패했습니다. 다시 로그인해주세요."
        elif status_code == 404:
            user_msg = f"요청한 리소스를 찾을 수 없습니다: {error_detail}"
        elif status_code == 409:
            user_msg = f"이미 처리된 작업입니다: {error_detail}"
        elif status_code == 422:
            user_msg = f"입력 데이터가 올바르지 않습니다: {error_detail}"
        elif status_code and 500 <= status_code < 600:
            user_msg = f"서버 오류가 발생했습니다 (HTTP {status_code}): {error_detail}"
        else:
            user_msg = f"{error_detail}"

        raise HTTPError(user_msg)

    # Production Line & Equipment API methods
    def get_production_lines(self) -> List[Dict[str, Any]]:
        """
        Get list of active production lines.

        Returns:
            list: List of active production line dictionaries with keys:
                - id, line_code, line_name, description, cycle_time_sec,
                  location, is_active, created_at, updated_at
        """
        return self.get("/api/v1/production-lines/active")

    def get_equipment(self) -> List[Dict[str, Any]]:
        """
        Get list of active equipment.

        Returns:
            list: List of active equipment dictionaries with keys:
                - id, equipment_code, equipment_name, equipment_type,
                  process_id, production_line_id, location, manufacturer,
                  model_number, serial_number, is_active, etc.
        """
        return self.get("/api/v1/equipment/active")

    def get_processes(self) -> List[Dict[str, Any]]:
        """
        Get list of active processes.

        Returns:
            list: List of active process dictionaries with keys:
                - id, process_number, process_code, process_name_ko,
                  process_name_en, description, estimated_duration_seconds,
                  quality_criteria, is_active, sort_order, created_at, updated_at
        """
        return self.get("/api/v1/processes/active")

    # LOT API methods
    def get_lots(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of LOTs.

        Args:
            status: Filter by status (CREATED, IN_PROGRESS, COMPLETED, etc.)

        Returns:
            list: List of LOT dictionaries
        """
        params = {"status": status} if status else None
        return self.get("/api/v1/lots", params=params)

    def get_lot(self, lot_id: int) -> Dict[str, Any]:
        """
        Get LOT details by ID.

        Args:
            lot_id: LOT database ID

        Returns:
            dict: LOT details
        """
        return self.get(f"/api/v1/lots/{lot_id}")

    def start_wip_generation(self, lot_id: int) -> Dict[str, Any]:
        """
        Start WIP generation for a LOT.

        Args:
            lot_id: LOT database ID

        Returns:
            dict: WIP generation result with generated serials
        """
        return self.post(f"/api/v1/lots/{lot_id}/start-wip-generation", {})

    # WIP (Serial) API methods
    def scan_wip(self, wip_id: str) -> Dict[str, Any]:
        """
        Scan WIP barcode to retrieve WIP information.

        Args:
            wip_id: WIP serial number

        Returns:
            dict: WIP information (LOT, product, process status)
        """
        return self.post(f"/api/v1/wip-items/{wip_id}/scan", {})

    def start_process(self, wip_id: str, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start process for WIP item.

        Args:
            wip_id: WIP serial number
            process_data: Process start data
                - process_id: Process ID
                - worker_id: Worker ID
                - equipment_id: Equipment ID (optional)
                - start_time: Start timestamp (ISO format)

        Returns:
            dict: Process start result
        """
        return self.post(f"/api/v1/wip-items/{wip_id}/start-process", process_data)

    def complete_process(self, wip_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete process for WIP item.

        Args:
            wip_id: WIP serial number
            completion_data: Process completion data
                - process_id: Process ID
                - worker_id: Worker ID
                - result: PASS or FAIL
                - complete_time: Completion timestamp (ISO format)
                - measurements: Process measurements (optional)
                - defect_type: Defect type if FAIL (optional)
                - defect_description: Defect description if FAIL (optional)

        Returns:
            dict: Process completion result
        """
        return self.post(f"/api/v1/wip-items/{wip_id}/complete-process", completion_data)

    def get_wip_statistics(self) -> Dict[str, Any]:
        """
        Get WIP statistics for dashboard.

        Returns:
            dict: Statistics including:
                - total_wip: Total WIP count
                - by_process: WIP count by process
                - by_status: WIP count by status
                - by_lot: WIP progress by LOT
                - alerts: Problem WIPs (long waiting time, etc.)
        """
        return self.get("/api/v1/wip-items/statistics")
