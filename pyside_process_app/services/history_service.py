"""History Service - Process history data retrieval"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from .api_client import APIClient

logger = logging.getLogger(__name__)


class HistoryService:
    """작업 이력 조회 서비스"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def get_process_history(
        self,
        process_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        result_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        공정 이력 조회 with filters

        Args:
            process_id: Filter by process ID
            operator_id: Filter by operator ID
            start_date: Start date for filtering
            end_date: End date for filtering
            result_filter: Filter by result (PASS, FAIL, REWORK)
            skip: Pagination offset
            limit: Maximum records to return

        Returns:
            List of process history records
        """
        try:
            endpoint = "/api/v1/process-data"
            params = {"skip": skip, "limit": limit}

            # Apply filters based on priority
            if process_id:
                endpoint = f"/api/v1/process-data/process/{process_id}"
            elif result_filter:
                endpoint = f"/api/v1/process-data/result/{result_filter}"
            elif operator_id:
                endpoint = f"/api/v1/process-data/operator/{operator_id}"
            elif start_date and end_date:
                endpoint = "/api/v1/process-data/date-range"
                params['start_date'] = start_date.isoformat() + "T00:00:00Z"
                params['end_date'] = end_date.isoformat() + "T23:59:59Z"

            response = self.api_client.get(endpoint, params=params)
            logger.info(f"Retrieved {len(response)} history records")
            return response

        except Exception as e:
            logger.error(f"Failed to get process history: {e}")
            raise

    def get_lot_history(self, lot_id: int) -> List[Dict[str, Any]]:
        """
        LOT 전체 이력 조회

        Args:
            lot_id: LOT ID to retrieve history for

        Returns:
            List of process history records for the LOT
        """
        try:
            endpoint = f"/api/v1/process-data/lot/{lot_id}"
            response = self.api_client.get(endpoint, params={"limit": 1000})
            logger.info(f"Retrieved history for LOT {lot_id}: {len(response)} records")
            return response
        except Exception as e:
            logger.error(f"Failed to get lot history: {e}")
            raise

    def get_serial_history(self, serial_id: int) -> List[Dict[str, Any]]:
        """
        Serial 전체 이력 조회

        Args:
            serial_id: Serial ID to retrieve history for

        Returns:
            List of process history records for the serial
        """
        try:
            endpoint = f"/api/v1/process-data/serial/{serial_id}"
            response = self.api_client.get(endpoint, params={"limit": 100})
            logger.info(f"Retrieved history for Serial {serial_id}: {len(response)} records")
            return response
        except Exception as e:
            logger.error(f"Failed to get serial history: {e}")
            raise
