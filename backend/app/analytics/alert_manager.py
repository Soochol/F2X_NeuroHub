import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.analytics.metrics_aggregator import MetricsAggregator
from app.models.equipment import Equipment

# Configure logger
logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manages system alerts and notifications.
    Checks for anomalies and triggers notifications.
    """

    def __init__(self, db: Session):
        self.db = db

    def check_process_failure_rate(self, process_id: int, threshold: float = 0.10) -> Optional[dict]:
        """
        Check if process failure rate exceeds threshold in the last hour.
        Returns alert dict if threshold exceeded, else None.
        """
        metrics = MetricsAggregator.aggregate_process_success_rate(self.db, process_id, time_window_hours=1)
        failure_rate = 1.0 - metrics["success_rate"]
        
        # Only alert if there's significant volume (e.g., > 5 runs) to avoid noise
        if metrics["total_runs"] > 5 and failure_rate > threshold:
            alert = {
                "type": "PROCESS_FAILURE_RATE_HIGH",
                "severity": "HIGH" if failure_rate > 0.20 else "MEDIUM",
                "message": f"Process {process_id} failure rate is {failure_rate*100:.1f}% (Threshold: {threshold*100}%)",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": metrics
            }
            self.send_alert(alert)
            return alert
        return None

    def check_equipment_downtime(self, equipment_id: int, max_downtime_minutes: int = 120) -> Optional[dict]:
        """
        Check if equipment has been in a non-productive state for too long.
        """
        equipment = self.db.query(Equipment).get(equipment_id)
        if not equipment:
            return None
            
        # If equipment is in a down state
        if equipment.status in ["MAINTENANCE", "OUT_OF_SERVICE", "ERROR"]:
            # Calculate how long it's been in this state
            # Assuming updated_at reflects the last status change
            status_duration = datetime.now(timezone.utc) - equipment.updated_at
            minutes_down = status_duration.total_seconds() / 60
            
            if minutes_down > max_downtime_minutes:
                alert = {
                    "type": "EQUIPMENT_DOWNTIME_LONG",
                    "severity": "HIGH",
                    "message": f"Equipment {equipment.equipment_code} has been {equipment.status} for {int(minutes_down)} minutes",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {
                        "equipment_id": equipment_id,
                        "status": equipment.status,
                        "minutes_down": minutes_down
                    }
                }
                self.send_alert(alert)
                return alert
        return None

    def send_alert(self, alert_data: dict):
        """
        Dispatch alert to configured channels.
        Currently logs to application logger.
        """
        # In the future, this would integrate with Email/Slack/SMS services
        logger.warning(f"ALERT TRIGGERED: [{alert_data['severity']}] {alert_data['message']}")
        # Could also save to an Alerts table in DB
