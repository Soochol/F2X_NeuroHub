"""Logging configuration for the application"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "pyside_process_app", log_dir: str = "logs") -> logging.Logger:
    """Setup application logger"""

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler (always available)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (with error handling)
    try:
        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True, parents=True)

        # Daily rotation
        today = datetime.now().strftime("%Y%m%d")
        file_handler = logging.FileHandler(
            log_path / f"app_{today}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        logger.warning(f"Could not create file logger: {e}. Logging to console only.")

    return logger


# Create default logger instance
logger = setup_logger()
