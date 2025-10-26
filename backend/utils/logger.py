"""
Logging Utility Module
Configures structured logging for the ParallelDev application.
Author: DBBuilder
Date: 2025-10-25
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    console_enabled: bool = True,
    file_enabled: bool = True,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configure application logging with console and file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None to skip file logging)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        console_enabled: Enable console logging
        file_enabled: Enable file logging
        log_format: Custom log format string
    
    Returns:
        Configured logger instance
    """
    # Default log format with timestamp, logger name, level, and message
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_enabled and log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        except Exception as e:
            logger.error(f"Failed to create file handler: {e}")
    
    logger.info(f"Logging configured: level={log_level}, console={console_enabled}, file={file_enabled}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.
    
    Args:
        name: Name of the module (typically __name__)
    
    Returns:
        Logger instance for the module
    """
    return logging.getLogger(name)
