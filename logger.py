#!/usr/bin/env python3
"""
Centralized logging utility for Angel Cloud / LogiBot
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config import config


class LogiLogger:
    """Custom logger for LogiBot system"""

    _instances = {}

    @classmethod
    def get_logger(cls, name: str = "logibot") -> logging.Logger:
        """Get or create logger instance"""
        if name in cls._instances:
            return cls._instances[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

        # Remove existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # File handler
        log_path = Path(config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        cls._instances[name] = logger
        return logger


def log_execution(func):
    """Decorator for logging function execution"""
    def wrapper(*args, **kwargs):
        logger = LogiLogger.get_logger()
        logger.info(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper


def log_sync_event(event_type: str, details: dict):
    """Log synchronization events"""
    logger = LogiLogger.get_logger("sync")
    logger.info(f"SYNC_EVENT: {event_type} - {details}")


def log_haul_rate_calculation(driver: str, rtm: float, rate: float):
    """Log haul rate calculations for audit trail"""
    logger = LogiLogger.get_logger("haul_rate")
    logger.info(f"HAUL_RATE: Driver={driver}, RTM={rtm}, Rate=${rate:.2f}")


# Create default logger instance
logger = LogiLogger.get_logger()
