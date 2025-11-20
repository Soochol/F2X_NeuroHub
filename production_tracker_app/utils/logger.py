"""
Logging configuration for Production Tracker App.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "ProductionTracker", log_dir: str = "logs") -> logging.Logger:
    """
    Setup application logger with file and console handlers.

    Args:
        name: Logger name
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Configure root logger to capture all module loggers (services, utils, etc.)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Create named logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers from both loggers
    root_logger.handlers.clear()
    logger.handlers.clear()

    # File handler (daily rotation)
    log_file = log_path / f"tracker_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Console handler (DEBUG level for API request debugging)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to root logger (captures all module loggers)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logger
