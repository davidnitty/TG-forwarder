"""
Enhanced Logging Module

Provides structured logging with file rotation and configurable verbosity.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class ForwarderLogger:
    """
    Enhanced logging system for the Telegram forwarder.

    Features:
    - Console logging with configurable verbosity
    - File logging with rotation
    - Structured log format
    - Separate log levels for console and file
    """

    def __init__(
        self,
        name: str = "telegram-forwarder",
        log_dir: str = "logs",
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        console_verbose: bool = False
    ) -> None:
        """
        Initialize the logger.

        Args:
            name: Logger name
            log_dir: Directory for log files
            max_file_size: Maximum size of each log file before rotation
            backup_count: Number of backup files to keep
            console_verbose: Enable DEBUG level on console
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.console_verbose = console_verbose

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Capture all levels

        # Clear existing handlers
        self.logger.handlers.clear()

        # Prevent propagation to root logger
        self.logger.propagate = False

        # Setup handlers
        self._setup_file_handler()
        self._setup_console_handler()

    def _setup_file_handler(self) -> None:
        """Setup rotating file handler for persistent logging."""
        log_file = self.log_dir / "forwarder.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file

        # Detailed format for file
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        self.logger.addHandler(file_handler)

    def _setup_console_handler(self) -> None:
        """Setup console handler with configurable verbosity."""
        console_handler = logging.StreamHandler(sys.stdout)

        if self.console_verbose:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)

        # Simpler format for console
        console_format = logging.Formatter(
            '[%(levelname)s] %(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)

        self.logger.addHandler(console_handler)

    def log_forwarded_message(
        self,
        message_id: int,
        source: str,
        destination: int,
        status: str,
        has_media: bool = False,
        filter_reason: Optional[str] = None
    ) -> None:
        """
        Log a forwarded message with structured data.

        Args:
            message_id: Telegram message ID
            source: Source channel username
            destination: Destination group ID
            status: Status (success, failed, blocked, etc.)
            has_media: Whether message contains media
            filter_reason: Reason if blocked by filters
        """
        log_data = {
            'message_id': message_id,
            'source': source,
            'destination': destination,
            'status': status,
            'has_media': has_media,
        }

        if filter_reason:
            log_data['filter_reason'] = filter_reason

        # Format as structured log
        log_message = (
            f"MSG_ID={message_id} | "
            f"SRC={source} | "
            f"DST={destination} | "
            f"STATUS={status} | "
            f"MEDIA={'yes' if has_media else 'no'}"
        )

        if filter_reason:
            log_message += f" | REASON={filter_reason}"

        if status == 'success':
            self.logger.info(log_message)
        elif status == 'blocked':
            self.logger.debug(log_message)
        elif status == 'failed':
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)

    def log_rate_limit(self, forwards_in_minute: int, pause_seconds: int) -> None:
        """Log rate limiting event."""
        self.logger.warning(
            f"RATE_LIMIT | Forwarded {forwards_in_minute} messages in last minute | "
            f"Pausing for {pause_seconds} seconds"
        )

    def log_command(self, command: str, user: str, user_id: int) -> None:
        """Log a command received in destination chat."""
        self.logger.info(
            f"COMMAND | cmd={command} | user={user} | user_id={user_id}"
        )

    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self.logger


# Global logger instance (initialized later with config)
_logger_instance: Optional[ForwarderLogger] = None


def setup_logger(
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    console_verbose: bool = False
) -> ForwarderLogger:
    """
    Setup and initialize the global logger.

    Args:
        log_dir: Directory for log files
        max_file_size: Maximum size of each log file
        backup_count: Number of backup files to keep
        console_verbose: Enable verbose console output

    Returns:
        Configured ForwarderLogger instance
    """
    global _logger_instance

    _logger_instance = ForwarderLogger(
        log_dir=log_dir,
        max_file_size=max_file_size,
        backup_count=backup_count,
        console_verbose=console_verbose
    )

    return _logger_instance


def get_logger() -> Optional[ForwarderLogger]:
    """
    Get the global logger instance.

    Returns:
        ForwarderLogger instance or None if not initialized
    """
    return _logger_instance
