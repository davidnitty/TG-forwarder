"""
Utility Functions Module

Provides helper functions for rate limiting, graceful shutdown,
statistics tracking, and time utilities.
"""

import asyncio
import signal
import random
from datetime import datetime, timedelta
from typing import Deque, Optional
from collections import deque
from threading import Lock


class RateLimiter:
    """
    Rate limiter to avoid Telegram API limits.

    Features:
    - Random delay between forwards (0.5-2 seconds)
    - Track forwards per minute
    - Auto-pause if exceeding threshold
    """

    def __init__(
        self,
        min_delay: float = 0.5,
        max_delay: float = 2.0,
        max_per_minute: int = 30
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
            max_per_minute: Maximum messages per minute before pausing
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_per_minute = max_per_minute

        # Track forward timestamps (within last 60 seconds)
        self.forward_timestamps: Deque[datetime] = deque(maxlen=100)
        self.lock = Lock()

    async def wait_before_forward(self) -> None:
        """
        Wait a random amount of time before forwarding.

        Call this before each forward to avoid rate limits.
        """
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)

    def record_forward(self) -> int:
        """
        Record a forward event and check if we should pause.

        Returns:
            Number of forwards in last minute
        """
        with self.lock:
            now = datetime.now()
            self.forward_timestamps.append(now)

            # Remove timestamps older than 1 minute
            cutoff = now - timedelta(seconds=60)
            while self.forward_timestamps and self.forward_timestamps[0] < cutoff:
                self.forward_timestamps.popleft()

            return len(self.forward_timestamps)

    async def check_rate_limit(self) -> bool:
        """
        Check if rate limit is approaching and pause if needed.

        Returns:
            True if pause was needed, False otherwise
        """
        count = self.record_forward()

        if count >= self.max_per_minute:
            pause_duration = 60 / self.max_per_minute
            return True

        return False

    async def acquire_slot(self) -> None:
        """
        Acquire a forwarding slot with rate limiting.

        This combines wait_before_forward() and check_rate_limit().
        """
        await self.wait_before_forward()

        # Check if we need to pause
        count = self.record_forward()
        if count >= self.max_per_minute:
            pause_time = random.uniform(5, 10)
            await asyncio.sleep(pause_time)


class Statistics:
    """Track bot statistics."""

    def __init__(self) -> None:
        """Initialize statistics."""
        self.start_time: datetime = datetime.now()
        self.messages_forwarded: int = 0
        self.messages_failed: int = 0
        self.messages_blocked: int = 0
        self.last_forward_time: Optional[datetime] = None
        self.last_message_id: Optional[int] = None

    def record_forward(self, message_id: int, success: bool = True) -> None:
        """
        Record a forwarded message.

        Args:
            message_id: Telegram message ID
            success: Whether the forward was successful
        """
        if success:
            self.messages_forwarded += 1
            self.last_forward_time = datetime.now()
        else:
            self.messages_failed += 1

        self.last_message_id = message_id

    def record_blocked(self) -> None:
        """Record a blocked message."""
        self.messages_blocked += 1

    def get_uptime(self) -> timedelta:
        """Get bot uptime."""
        return datetime.now() - self.start_time

    def get_stats(self) -> dict:
        """
        Get current statistics.

        Returns:
            Dictionary with all statistics
        """
        uptime = self.get_uptime()

        stats = {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime).split('.')[0],  # Remove microseconds
            'messages_forwarded': self.messages_forwarded,
            'messages_failed': self.messages_failed,
            'messages_blocked': self.messages_blocked,
            'messages_total': self.messages_forwarded + self.messages_failed + self.messages_blocked,
            'last_forward_time': self.last_forward_time.isoformat() if self.last_forward_time else None,
            'last_message_id': self.last_message_id,
        }

        # Calculate forwards in last 24 hours
        if self.messages_forwarded > 0:
            stats['avg_per_hour'] = round(self.messages_forwarded / max(uptime.total_seconds() / 3600, 1), 2)
        else:
            stats['avg_per_hour'] = 0

        return stats

    def reset(self) -> None:
        """Reset all statistics."""
        self.__init__()


class GracefulShutdown:
    """
    Handle graceful shutdown with signal handlers.

    Ensures:
    - Cache is saved to disk
    - Client is properly disconnected
    - Resources are cleaned up
    """

    def __init__(self) -> None:
        """Initialize shutdown handler."""
        self.shutdown = False
        self._cleanup_callbacks = []

    def register_cleanup(self, callback) -> None:
        """
        Register a cleanup callback to run on shutdown.

        Args:
            callback: Async function to call during shutdown
        """
        self._cleanup_callbacks.append(callback)

    def signal_handler(self, signum, frame) -> None:
        """
        Handle signal interrupts.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_names = {
            signal.SIGINT: 'SIGINT',
            signal.SIGTERM: 'SIGTERM',
        }
        signal_name = signal_names.get(signum, f'SIGNAL({signum})')

        print(f"\n[INFO] Received {signal_name}, initiating graceful shutdown...")
        self.shutdown = True

    async def run_cleanup(self) -> None:
        """Run all registered cleanup callbacks."""
        for callback in self._cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                print(f"[ERROR] Error during cleanup: {e}")

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)


def format_timestamp(dt: Optional[datetime]) -> str:
    """
    Format datetime for display.

    Args:
        dt: DateTime object or None

    Returns:
        Formatted string or "Never"
    """
    if not dt:
        return "Never"

    # Show relative time for recent events
    now = datetime.now()
    if dt > now - timedelta(minutes=1):
        seconds = int((now - dt).total_seconds())
        return f"{seconds} seconds ago"
    elif dt > now - timedelta(hours=1):
        minutes = int((now - dt).total_seconds() / 60)
        return f"{minutes} minutes ago"
    elif dt > now - timedelta(days=1):
        hours = int((now - dt).total_seconds() / 3600)
        return f"{hours} hours ago"
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_number(num: int) -> str:
    """
    Format number with thousands separator.

    Args:
        num: Number to format

    Returns:
        Formatted string
    """
    return f"{num:,}"


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate string to max length with ellipsis.

    Args:
        text: String to truncate
        max_length: Maximum length

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
