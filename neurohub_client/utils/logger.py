"""
Logging configuration for Production Tracker App.
"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """콘솔용 컬러 로그 포맷터"""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m',
        'TIME': '\033[90m',
        'MODULE': '\033[34m',
    }

    def format(self, record):
        c = self.COLORS
        formatted_time = self.formatTime(record, self.datefmt)
        level_color = c.get(record.levelname, '')
        return (
            f"{c['TIME']}{formatted_time}{c['RESET']} - "
            f"{c['MODULE']}{record.name}{c['RESET']} - "
            f"{level_color}{record.levelname}{c['RESET']} - "
            f"{record.getMessage()}"
        )


def setup_logger(name: str = "ProductionTracker", log_dir: str = "logs") -> logging.Logger:
    """
    Setup application logger with file and console handlers.

    Args:
        name: Logger name
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    # Windows ANSI 색상 지원 활성화
    if sys.platform == 'win32':
        os.system('')

    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Create named logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    root_logger.handlers.clear()
    logger.handlers.clear()

    # File handler (색상 없이)
    log_file = log_path / f"tracker_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler (컬러 포맷터 적용)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logger
