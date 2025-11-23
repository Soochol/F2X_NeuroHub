"""
Monitoring Configuration Module

This module provides configuration settings and utilities for the performance
monitoring system, including environment-based configuration and defaults.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QueryMonitoringConfig:
    """Configuration for database query monitoring."""
    enabled: bool = True
    slow_query_threshold_ms: float = 100.0
    max_query_log_size: int = 10000
    log_slow_queries: bool = True
    export_interval_minutes: int = 60
    enable_sqlalchemy_events: bool = True


@dataclass
class PerformanceMonitoringConfig:
    """Configuration for API performance monitoring."""
    enabled: bool = True
    response_time_alert_ms: float = 1000.0
    max_metrics_log_size: int = 10000
    track_memory_usage: bool = True
    track_cpu_usage: bool = True
    export_interval_minutes: int = 60


@dataclass
class ResourceMonitoringConfig:
    """Configuration for system resource monitoring."""
    enabled: bool = True
    interval_seconds: int = 60
    memory_alert_percent: float = 80.0
    cpu_alert_percent: float = 80.0
    disk_alert_percent: float = 90.0
    track_network_io: bool = True
    track_disk_io: bool = True


@dataclass
class AlertingConfig:
    """Configuration for monitoring alerts."""
    enabled: bool = True
    error_rate_alert_percent: float = 5.0
    slow_endpoint_percent: float = 10.0
    failed_query_percent: float = 1.0
    alert_cooldown_minutes: int = 15
    alert_channels: list = None  # ['log', 'email', 'slack']


@dataclass
class ExportConfig:
    """Configuration for metrics export."""
    enabled: bool = True
    export_format: str = "json"  # json, csv, prometheus
    export_path: str = "logs/monitoring"
    retention_days: int = 30
    compress_exports: bool = True
    auto_export: bool = True


class MonitoringConfig:
    """
    Main configuration class for the monitoring system.

    This class loads configuration from environment variables and provides
    defaults for all monitoring settings.
    """

    def __init__(self):
        """Initialize monitoring configuration from environment."""
        self.query_monitoring = self._load_query_config()
        self.performance_monitoring = self._load_performance_config()
        self.resource_monitoring = self._load_resource_config()
        self.alerting = self._load_alerting_config()
        self.export = self._load_export_config()

        # Global settings
        self.enabled = self._get_bool_env("MONITORING_ENABLED", True)
        self.debug = self._get_bool_env("MONITORING_DEBUG", False)
        self.log_level = os.getenv("MONITORING_LOG_LEVEL", "INFO")

        # Create necessary directories
        self._setup_directories()

    def _load_query_config(self) -> QueryMonitoringConfig:
        """Load query monitoring configuration from environment."""
        return QueryMonitoringConfig(
            enabled=self._get_bool_env("ENABLE_QUERY_MONITORING", True),
            slow_query_threshold_ms=self._get_float_env("SLOW_QUERY_THRESHOLD_MS", 100.0),
            max_query_log_size=self._get_int_env("MAX_QUERY_LOG_SIZE", 10000),
            log_slow_queries=self._get_bool_env("LOG_SLOW_QUERIES", True),
            export_interval_minutes=self._get_int_env("QUERY_EXPORT_INTERVAL_MINUTES", 60),
            enable_sqlalchemy_events=self._get_bool_env("ENABLE_SQLALCHEMY_EVENTS", True),
        )

    def _load_performance_config(self) -> PerformanceMonitoringConfig:
        """Load performance monitoring configuration from environment."""
        return PerformanceMonitoringConfig(
            enabled=self._get_bool_env("ENABLE_PERFORMANCE_MONITORING", True),
            response_time_alert_ms=self._get_float_env("RESPONSE_TIME_ALERT_MS", 1000.0),
            max_metrics_log_size=self._get_int_env("MAX_METRICS_LOG_SIZE", 10000),
            track_memory_usage=self._get_bool_env("TRACK_MEMORY_USAGE", True),
            track_cpu_usage=self._get_bool_env("TRACK_CPU_USAGE", True),
            export_interval_minutes=self._get_int_env("METRICS_EXPORT_INTERVAL_MINUTES", 60),
        )

    def _load_resource_config(self) -> ResourceMonitoringConfig:
        """Load resource monitoring configuration from environment."""
        return ResourceMonitoringConfig(
            enabled=self._get_bool_env("ENABLE_RESOURCE_MONITORING", True),
            interval_seconds=self._get_int_env("RESOURCE_MONITORING_INTERVAL", 60),
            memory_alert_percent=self._get_float_env("MEMORY_ALERT_PERCENT", 80.0),
            cpu_alert_percent=self._get_float_env("CPU_ALERT_PERCENT", 80.0),
            disk_alert_percent=self._get_float_env("DISK_ALERT_PERCENT", 90.0),
            track_network_io=self._get_bool_env("TRACK_NETWORK_IO", True),
            track_disk_io=self._get_bool_env("TRACK_DISK_IO", True),
        )

    def _load_alerting_config(self) -> AlertingConfig:
        """Load alerting configuration from environment."""
        alert_channels = os.getenv("ALERT_CHANNELS", "log").split(",")
        return AlertingConfig(
            enabled=self._get_bool_env("ENABLE_ALERTS", True),
            error_rate_alert_percent=self._get_float_env("ERROR_RATE_ALERT_PERCENT", 5.0),
            slow_endpoint_percent=self._get_float_env("SLOW_ENDPOINT_PERCENT", 10.0),
            failed_query_percent=self._get_float_env("FAILED_QUERY_PERCENT", 1.0),
            alert_cooldown_minutes=self._get_int_env("ALERT_COOLDOWN_MINUTES", 15),
            alert_channels=alert_channels,
        )

    def _load_export_config(self) -> ExportConfig:
        """Load export configuration from environment."""
        return ExportConfig(
            enabled=self._get_bool_env("ENABLE_METRICS_EXPORT", True),
            export_format=os.getenv("METRICS_EXPORT_FORMAT", "json"),
            export_path=os.getenv("METRICS_EXPORT_PATH", "logs/monitoring"),
            retention_days=self._get_int_env("METRICS_RETENTION_DAYS", 30),
            compress_exports=self._get_bool_env("COMPRESS_METRICS_EXPORTS", True),
            auto_export=self._get_bool_env("AUTO_EXPORT_METRICS", True),
        )

    def _setup_directories(self):
        """Create necessary directories for monitoring."""
        paths = [
            Path(self.export.export_path),
            Path("logs/monitoring"),
            Path("logs/monitoring/archives"),
        ]

        for path in paths:
            path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_bool_env(key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    @staticmethod
    def _get_int_env(key: str, default: int) -> int:
        """Get integer value from environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default

    @staticmethod
    def _get_float_env(key: str, default: float) -> float:
        """Get float value from environment variable."""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enabled": self.enabled,
            "debug": self.debug,
            "log_level": self.log_level,
            "query_monitoring": {
                "enabled": self.query_monitoring.enabled,
                "slow_query_threshold_ms": self.query_monitoring.slow_query_threshold_ms,
                "max_query_log_size": self.query_monitoring.max_query_log_size,
                "log_slow_queries": self.query_monitoring.log_slow_queries,
                "export_interval_minutes": self.query_monitoring.export_interval_minutes,
                "enable_sqlalchemy_events": self.query_monitoring.enable_sqlalchemy_events,
            },
            "performance_monitoring": {
                "enabled": self.performance_monitoring.enabled,
                "response_time_alert_ms": self.performance_monitoring.response_time_alert_ms,
                "max_metrics_log_size": self.performance_monitoring.max_metrics_log_size,
                "track_memory_usage": self.performance_monitoring.track_memory_usage,
                "track_cpu_usage": self.performance_monitoring.track_cpu_usage,
                "export_interval_minutes": self.performance_monitoring.export_interval_minutes,
            },
            "resource_monitoring": {
                "enabled": self.resource_monitoring.enabled,
                "interval_seconds": self.resource_monitoring.interval_seconds,
                "memory_alert_percent": self.resource_monitoring.memory_alert_percent,
                "cpu_alert_percent": self.resource_monitoring.cpu_alert_percent,
                "disk_alert_percent": self.resource_monitoring.disk_alert_percent,
                "track_network_io": self.resource_monitoring.track_network_io,
                "track_disk_io": self.resource_monitoring.track_disk_io,
            },
            "alerting": {
                "enabled": self.alerting.enabled,
                "error_rate_alert_percent": self.alerting.error_rate_alert_percent,
                "slow_endpoint_percent": self.alerting.slow_endpoint_percent,
                "failed_query_percent": self.alerting.failed_query_percent,
                "alert_cooldown_minutes": self.alerting.alert_cooldown_minutes,
                "alert_channels": self.alerting.alert_channels,
            },
            "export": {
                "enabled": self.export.enabled,
                "export_format": self.export.export_format,
                "export_path": self.export.export_path,
                "retention_days": self.export.retention_days,
                "compress_exports": self.export.compress_exports,
                "auto_export": self.export.auto_export,
            },
        }

    def validate(self) -> bool:
        """
        Validate configuration settings.

        Returns:
            True if configuration is valid, False otherwise.
        """
        errors = []

        # Validate thresholds
        if self.query_monitoring.slow_query_threshold_ms <= 0:
            errors.append("Slow query threshold must be positive")

        if self.performance_monitoring.response_time_alert_ms <= 0:
            errors.append("Response time alert threshold must be positive")

        if not (0 < self.resource_monitoring.memory_alert_percent <= 100):
            errors.append("Memory alert percent must be between 0 and 100")

        if not (0 < self.resource_monitoring.cpu_alert_percent <= 100):
            errors.append("CPU alert percent must be between 0 and 100")

        # Validate export settings
        valid_formats = ["json", "csv", "prometheus"]
        if self.export.export_format not in valid_formats:
            errors.append(f"Export format must be one of {valid_formats}")

        # Log errors if any
        if errors:
            import logging
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False

        return True


# Global configuration instance
_config: Optional[MonitoringConfig] = None


def get_config() -> MonitoringConfig:
    """
    Get the global monitoring configuration instance.

    Returns:
        MonitoringConfig: Global configuration instance
    """
    global _config
    if _config is None:
        _config = MonitoringConfig()
        _config.validate()
    return _config


def reload_config() -> MonitoringConfig:
    """
    Reload configuration from environment.

    Returns:
        MonitoringConfig: New configuration instance
    """
    global _config
    _config = MonitoringConfig()
    _config.validate()
    return _config


# Preset configurations for different environments
class MonitoringPresets:
    """Preset configurations for different environments."""

    @staticmethod
    def development() -> Dict[str, str]:
        """Development environment configuration."""
        return {
            "MONITORING_ENABLED": "true",
            "MONITORING_DEBUG": "true",
            "MONITORING_LOG_LEVEL": "DEBUG",
            "ENABLE_QUERY_MONITORING": "true",
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "ENABLE_RESOURCE_MONITORING": "false",
            "SLOW_QUERY_THRESHOLD_MS": "50",
            "RESPONSE_TIME_ALERT_MS": "2000",
            "ENABLE_ALERTS": "false",
        }

    @staticmethod
    def staging() -> Dict[str, str]:
        """Staging environment configuration."""
        return {
            "MONITORING_ENABLED": "true",
            "MONITORING_DEBUG": "false",
            "MONITORING_LOG_LEVEL": "INFO",
            "ENABLE_QUERY_MONITORING": "true",
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "ENABLE_RESOURCE_MONITORING": "true",
            "SLOW_QUERY_THRESHOLD_MS": "100",
            "RESPONSE_TIME_ALERT_MS": "1500",
            "ENABLE_ALERTS": "true",
            "RESOURCE_MONITORING_INTERVAL": "120",
        }

    @staticmethod
    def production() -> Dict[str, str]:
        """Production environment configuration."""
        return {
            "MONITORING_ENABLED": "true",
            "MONITORING_DEBUG": "false",
            "MONITORING_LOG_LEVEL": "WARNING",
            "ENABLE_QUERY_MONITORING": "true",
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "ENABLE_RESOURCE_MONITORING": "true",
            "SLOW_QUERY_THRESHOLD_MS": "100",
            "RESPONSE_TIME_ALERT_MS": "1000",
            "MEMORY_ALERT_PERCENT": "80",
            "CPU_ALERT_PERCENT": "80",
            "ERROR_RATE_ALERT_PERCENT": "5",
            "ENABLE_ALERTS": "true",
            "ALERT_CHANNELS": "log,email,slack",
            "AUTO_EXPORT_METRICS": "true",
            "COMPRESS_METRICS_EXPORTS": "true",
            "METRICS_RETENTION_DAYS": "90",
        }

    @staticmethod
    def minimal() -> Dict[str, str]:
        """Minimal monitoring configuration."""
        return {
            "MONITORING_ENABLED": "true",
            "ENABLE_QUERY_MONITORING": "false",
            "ENABLE_PERFORMANCE_MONITORING": "true",
            "ENABLE_RESOURCE_MONITORING": "false",
            "ENABLE_ALERTS": "false",
            "AUTO_EXPORT_METRICS": "false",
        }

    @staticmethod
    def apply_preset(preset_name: str) -> None:
        """
        Apply a preset configuration.

        Args:
            preset_name: Name of the preset ('development', 'staging', 'production', 'minimal')
        """
        presets = {
            "development": MonitoringPresets.development,
            "staging": MonitoringPresets.staging,
            "production": MonitoringPresets.production,
            "minimal": MonitoringPresets.minimal,
        }

        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(presets.keys())}")

        preset_config = presets[preset_name]()
        for key, value in preset_config.items():
            os.environ[key] = value

        # Reload configuration
        reload_config()