"""
Telegram Forwarder Bot - Core Module with Advanced Features

This module implements a Telegram bot that forwards messages from a public channel
to a private group with optional watermarking, duplicate prevention, filtering,
rate limiting, enhanced logging, and status commands.

Advanced Features:
- Message filtering (keywords, blocklist, CA detection)
- Rate limiting with random delays
- Enhanced logging with rotation
- /status command in destination chat
- Graceful shutdown with signal handling
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional, Deque

# Fix Windows terminal encoding issues
if sys.platform == 'win32':
    try:
        import locale
        import codecs
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

from telethon import TelegramClient, events
from telethon.errors import RPCError, FloodWaitError
from telethon.tl.types import (
    Message,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaWebPage,
    MessageMediaGeo,
    MessageMediaContact,
    MessageMediaPoll,
    User,
    Chat,
    Channel,
    MessageEntityTextUrl,
    MessageEntityUrl,
)

# Import custom modules
from config import get_config, Config
from filters import get_filters, MessageFilters
from logger import setup_logger, get_logger as get_forwarder_logger
from utils import (
    RateLimiter,
    Statistics,
    GracefulShutdown,
    format_timestamp,
    format_number,
)
from formatter import init_formatter, get_formatter


class TelegramForwarder:
    """
    Telegram Forwarder Bot class with advanced features.

    Handles monitoring a source channel and forwarding messages to a destination
    group with watermarking, duplicate prevention, filtering, rate limiting,
    and enhanced logging.
    """

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize the Telegram forwarder bot.

        Args:
            verbose: Enable verbose console output
        """
        # Load configuration
        self.config: Config = get_config()

        # Override verbose setting if command-line flag provided
        if verbose:
            self.config.log_verbose = True

        # Extract config values
        self.api_id: int = self.config.api_id
        self.api_hash: str = self.config.api_hash
        self.session_name: str = self.config.session_name
        self.source_channel: str = self.config.source_channel
        self.destination_group: int = self.config.destination_group
        self.watermark: str = self.config.watermark
        self.max_cache_size: int = self.config.max_cache_size

        # Setup enhanced logger
        self.logger = setup_logger(
            log_dir=self.config.log_dir,
            max_file_size=self.config.log_max_file_size,
            backup_count=self.config.log_backup_count,
            console_verbose=self.config.log_verbose or verbose
        ).get_logger()

        self.logger.info("=" * 70)
        self.logger.info("Telegram Forwarder Bot - Starting")
        self.logger.info("=" * 70)

        # Initialize filters
        self.filters: MessageFilters = get_filters()
        if self.filters.enabled:
            self.logger.info(f"Filters enabled: keywords={self.filters.keywords}, "
                          f"blocklist={self.filters.blocklist}, "
                          f"require_ca={self.filters.require_ca}")
        else:
            self.logger.info("Filters disabled")

        # Initialize enhanced formatter if enabled
        self.enhanced_formatter = None
        if self.config.enable_enhanced_formatting:
            self.enhanced_formatter = init_formatter(
                custom_watermark=self.config.custom_watermark_enhanced,
                strip_watermarks=self.config.strip_source_watermarks
            )
            self.logger.info(f"Enhanced formatting enabled for channels: {self.config.enhanced_formatting_channels}")
        else:
            self.logger.info("Enhanced formatting disabled")

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            min_delay=self.config.rate_limit_min_delay,
            max_delay=self.config.rate_limit_max_delay,
            max_per_minute=self.config.rate_limit_max_per_minute
        )
        self.logger.info(f"Rate limiting: {self.config.rate_limit_min_delay}s - "
                        f"{self.config.rate_limit_max_delay}s delay, "
                        f"max {self.config.rate_limit_max_per_minute}/min")

        # Initialize statistics
        self.stats = Statistics()

        # Initialize graceful shutdown
        self.shutdown_handler = GracefulShutdown()
        self.shutdown_handler.setup_signal_handlers()
        self.shutdown_handler.register_cleanup(self._cleanup)

        # Initialize message cache
        self.forwarded_messages: Deque[int] = deque(maxlen=self.max_cache_size)
        self._load_cache_from_disk()

        # Initialize Telegram client with session persistence
        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash
        )

        self.logger.info(f"Source channel: @{self.source_channel}")
        self.logger.info(f"Destination group: {self.destination_group}")
        self.logger.info(f"Watermark: '{self.watermark}'" if self.watermark else "Watermark disabled")
        self.logger.info(f"Max cache size: {self.max_cache_size} messages")
        self.logger.info("Initialization complete")

    @staticmethod
    def _get_timestamp() -> str:
        """Get formatted timestamp for console output."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _load_cache_from_disk(self) -> None:
        """Load previously forwarded message IDs from disk cache file."""
        cache_file = Path('forwarded_messages.txt')
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    for line in f:
                        msg_id = line.strip()
                        if msg_id.isdigit():
                            self.forwarded_messages.append(int(msg_id))
                self.logger.info(f"Loaded {len(self.forwarded_messages)} message IDs from cache")
                print(f"[INFO] {self._get_timestamp()} - Loaded {len(self.forwarded_messages)} message IDs from cache")
            except Exception as e:
                self.logger.error(f"Failed to load cache: {e}")
                print(f"[ERROR] {self._get_timestamp()} - Failed to load cache: {e}")

    def _save_cache_to_disk(self) -> None:
        """Save all message IDs from memory cache to disk."""
        try:
            with open('forwarded_messages.txt', 'w') as f:
                for msg_id in self.forwarded_messages:
                    f.write(f"{msg_id}\n")
            self.logger.info(f"Saved {len(self.forwarded_messages)} message IDs to disk")
        except Exception as e:
            self.logger.error(f"Failed to save cache to disk: {e}")

    def _save_message_to_cache(self, message_id: int) -> None:
        """Save a message ID to both memory cache and disk."""
        self.forwarded_messages.append(message_id)

        try:
            with open('forwarded_messages.txt', 'a') as f:
                f.write(f"{message_id}\n")
        except Exception as e:
            self.logger.error(f"Failed to save message {message_id} to cache: {e}")

    def _is_duplicate(self, message_id: int) -> bool:
        """Check if a message has already been forwarded."""
        return message_id in self.forwarded_messages

    def _should_use_enhanced_formatting(self) -> bool:
        """Check if enhanced formatting should be applied to current source."""
        if not self.enhanced_formatter:
            return False

        source_normalized = self.source_channel.lower().lstrip('@')
        enabled_normalized = [ch.lower().lstrip('@') for ch in self.config.enhanced_formatting_channels]

        return source_normalized in enabled_normalized

    def _add_watermark_to_text(self, text: Optional[str]) -> str:
        """Add watermark to text message (only for text-only messages)."""
        if not self.watermark:
            return text or ''

        if text:
            return f"{text}\n\n{self.watermark}"
        return self.watermark

    def _format_message_text(self, text: Optional[str]) -> str:
        """
        Format message text with either enhanced formatting or standard watermark.

        Args:
            text: Original message text

        Returns:
            Formatted text
        """
        if not text:
            return text or ''

        # Use enhanced formatting if enabled for this channel
        if self._should_use_enhanced_formatting():
            self.logger.debug("Applying enhanced formatting")
            return self.enhanced_formatter.format_solana_message(text)

        # Use standard watermark
        return self._add_watermark_to_text(text)

    async def _forward_text_only_message(self, message: Message) -> bool:
        """Forward a text-only message with watermark or enhanced formatting."""
        try:
            text = self._format_message_text(message.text)

            await self.client.send_message(
                self.destination_group,
                text,
                link_preview=bool(message.web_preview)
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to forward text message {message.id}: {e}")
            return False

    async def _forward_media_message(self, message: Message) -> bool:
        """Forward a media message (photo, video, document, etc.)."""
        try:
            if not message.media:
                return False

            caption = message.text or ''

            if isinstance(message.media, MessageMediaPhoto):
                await self.client.send_file(
                    self.destination_group,
                    message.media,
                    caption=caption,
                    parse_mode='html'
                )
            elif isinstance(message.media, MessageMediaDocument):
                await self.client.send_file(
                    self.destination_group,
                    message.media,
                    caption=caption,
                    parse_mode='html'
                )
            elif isinstance(message.media, (MessageMediaGeo, MessageMediaContact, MessageMediaPoll)):
                await self.client.send_message(
                    self.destination_group,
                    message,
                    caption=caption
                )
            elif message.media:
                await self.client.send_file(
                    self.destination_group,
                    message.media,
                    caption=caption
                )

            return True

        except Exception as e:
            self.logger.error(f"Failed to forward media message {message.id}: {e}")
            return False

    async def _forward_message(self, message: Message) -> bool:
        """
        Smart forward function with filtering, rate limiting, and logging.

        Returns:
            True if message was forwarded successfully, False otherwise
        """
        try:
            message_id = message.id

            # Check for duplicates
            if self._is_duplicate(message_id):
                self.logger.debug(f"Skipping duplicate message {message_id}")
                return False

            # Check filters if enabled
            filter_reason = None
            if self.filters.enabled:
                should_forward, reason = self.filters.should_forward(message.text)
                if not should_forward:
                    self.logger.debug(f"Message {message_id} blocked by filters: {reason}")
                    get_forwarder_logger().log_forwarded_message(
                        message_id=message_id,
                        source=self.source_channel,
                        destination=self.destination_group,
                        status='blocked',
                        has_media=bool(message.media),
                        filter_reason=reason
                    )
                    self.stats.record_blocked()
                    return False
                filter_reason = reason

            # Acquire rate limit slot
            await self.rate_limiter.acquire_slot()

            # Forward the message
            print(f"[INFO] {self._get_timestamp()} - Processing message {message_id}")
            success = False

            if message.media:
                success = await self._forward_media_message(message)
            else:
                success = await self._forward_text_only_message(message)

            if success:
                self._save_message_to_cache(message_id)
                self.stats.record_forward(message_id, success=True)

                get_forwarder_logger().log_forwarded_message(
                    message_id=message_id,
                    source=self.source_channel,
                    destination=self.destination_group,
                    status='success',
                    has_media=bool(message.media)
                )

                self.logger.info(f"Successfully forwarded message {message_id}")
                print(f"[SUCCESS] {self._get_timestamp()} - Forwarded message {message_id}")
            else:
                self.stats.record_forward(message_id, success=False)

                get_forwarder_logger().log_forwarded_message(
                    message_id=message_id,
                    source=self.source_channel,
                    destination=self.destination_group,
                    status='failed',
                    has_media=bool(message.media)
                )

                print(f"[ERROR] {self._get_timestamp()} - Failed to forward message {message_id}")

            return success

        except FloodWaitError as e:
            self.logger.warning(f"Rate limited, waiting {e.seconds} seconds")
            get_forwarder_logger().log_rate_limit(
                forwards_in_minute=self.rate_limiter.record_forward(),
                pause_seconds=e.seconds
            )
            await asyncio.sleep(e.seconds)
            return await self._forward_message(message)

        except RPCError as e:
            self.logger.error(f"RPC error forwarding message {message.id}: {e}")
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error forwarding message {message.id}: {e}")
            return False

    async def _handle_new_message(self, event: events.NewMessage.Event) -> None:
        """Event handler for new messages."""
        if self.shutdown_handler.shutdown:
            return

        try:
            message: Message = event.message
            await self._forward_message(message)

        except Exception as e:
            self.logger.error(f"Error in new message handler: {e}")

    async def _handle_edited_message(self, event: events.MessageEdited.Event) -> None:
        """Event handler for edited messages."""
        if self.shutdown_handler.shutdown:
            return

        try:
            message: Message = event.message
            self.logger.info(f"Message edited: {message.id}, forwarding update")
            await self._forward_message(message)

        except Exception as e:
            self.logger.error(f"Error in edited message handler: {e}")

    async def _handle_status_command(self, event: events.NewMessage.Event) -> None:
        """Handle /status command in destination group."""
        try:
            message: Message = event.message

            # Only respond to /status command
            if not message.text or not message.text.startswith('/status'):
                return

            # Get user info
            sender = await message.get_sender()
            user_name = getattr(sender, 'first_name', 'Unknown')
            user_id = getattr(sender, 'id', 'Unknown')

            self.logger.info(f"Status command requested by {user_name} ({user_id})")
            get_forwarder_logger().log_command('/status', user_name, user_id)

            # Get statistics
            stats = self.stats.get_stats()
            filter_stats = self.filters.get_stats() if self.filters.enabled else {}

            # Build status message
            status_msg = (
                f"📊 **Bot Status**\n\n"
                f"⏱️ **Uptime:** {stats['uptime_human']}\n"
                f"📤 **Forwarded:** {format_number(stats['messages_forwarded'])}\n"
                f"❌ **Failed:** {format_number(stats['messages_failed'])}\n"
                f"🚫 **Blocked:** {format_number(stats['messages_blocked'])}\n"
                f"📝 **Total Processed:** {format_number(stats['messages_total'])}\n"
                f"📈 **Avg/Hour:** {stats['avg_per_hour']}\n"
                f"💾 **Cache Size:** {len(self.forwarded_messages)} / {self.max_cache_size}\n"
                f"🕐 **Last Forward:** {format_timestamp(self.stats.last_forward_time)}\n"
            )

            if self.filters.enabled:
                status_msg += (
                    f"\n🔍 **Filter Stats:**\n"
                    f"  • Checked: {filter_stats.get('total_checked', 0)}\n"
                    f"  • Allowed: {filter_stats.get('allowed', 0)}\n"
                    f"  • Blocked: {filter_stats.get('blocked', 0)}\n"
                )

            status_msg += f"\n🔄 **Bot is running**"

            # Send status message
            await message.reply(status_msg, parse_mode='markdown')

        except Exception as e:
            self.logger.error(f"Error handling status command: {e}")

    async def _cleanup(self) -> None:
        """Cleanup resources before shutdown."""
        self.logger.info("Running cleanup procedures...")

        # Save cache to disk
        self._save_cache_to_disk()

        # Log final statistics
        stats = self.stats.get_stats()
        self.logger.info(f"Final stats: {format_number(stats['messages_forwarded'])} forwarded, "
                        f"{format_number(stats['messages_failed'])} failed, "
                        f"{format_number(stats['messages_blocked'])} blocked")

    async def start(self) -> None:
        """Start the Telegram forwarder bot."""
        self.logger.info("Starting Telegram forwarder bot...")

        try:
            # Connect to Telegram servers
            await self.client.connect()
            self.logger.info("Connected to Telegram servers")

            # Check if user is authorized
            if not await self.client.is_user_authorized():
                self.logger.error("Not authorized! Please run: python login.py")
                print("[ERROR] Not authorized! Please run: python login.py")
                return

            # Get authenticated user info
            me: User = await self.client.get_me()
            self.logger.info(f"Authorized as: {me.first_name} (@{me.username})")
            print(f"[INFO] {self._get_timestamp()} - Authorized as: {me.first_name} (@{me.username})")

            # Get source channel entity
            try:
                source_entity = await self.client.get_entity(self.source_channel)
                self.logger.info(f"Source channel: {source_entity.title}")
                print(f"[INFO] {self._get_timestamp()} - Source channel: {source_entity.title}")
            except Exception as e:
                self.logger.error(f"Cannot access source channel: {e}")
                print(f"[ERROR] {self._get_timestamp()} - Cannot access source channel: {e}")
                return

            # Get destination group entity
            try:
                dest_entity = await self.client.get_entity(self.destination_group)
                self.logger.info(f"Destination group: {dest_entity.title}")
                print(f"[INFO] {self._get_timestamp()} - Destination group: {dest_entity.title}")
            except Exception as e:
                self.logger.error(f"Cannot access destination group: {e}")
                print(f"[ERROR] {self._get_timestamp()} - Cannot access destination group: {e}")
                return

            # Register NewMessage event handler for source channel
            self.client.add_event_handler(
                self._handle_new_message,
                events.NewMessage(chats=self.source_channel)
            )
            self.logger.info(f"NewMessage handler registered for @{self.source_channel}")

            # Register MessageEdited event handler for source channel
            self.client.add_event_handler(
                self._handle_edited_message,
                events.MessageEdited(chats=self.source_channel)
            )
            self.logger.info(f"MessageEdited handler registered for @{self.source_channel}")

            # Register command handler for destination group
            self.client.add_event_handler(
                self._handle_status_command,
                events.NewMessage(chats=self.destination_group, incoming=True)
            )
            self.logger.info(f"Command handler registered for destination group")

            print(f"\n[SUCCESS] {self._get_timestamp()} - Bot is running and monitoring for messages...")
            print(f"[INFO] {self._get_timestamp()} - Cache contains {len(self.forwarded_messages)} message IDs")
            print(f"[INFO] {self._get_timestamp()} - Send /status in destination group for bot statistics")
            print(f"[INFO] {self._get_timestamp()} - Press Ctrl+C to stop\n")

            self.logger.info("Bot is running and monitoring for messages...")

            # Run indefinitely until disconnected or shutdown
            while not self.shutdown_handler.shutdown:
                try:
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    break

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the Telegram forwarder bot and disconnect."""
        self.logger.info("Stopping bot...")

        # Run cleanup
        await self._cleanup()

        # Disconnect from Telegram
        await self.client.disconnect()
        self.logger.info("Disconnected from Telegram")

        print(f"\n[INFO] {self._get_timestamp()} - Bot stopped gracefully")
        print(f"[INFO] {self._get_timestamp()} - Cache saved to disk")
        print(f"[INFO] {self._get_timestamp()} - Goodbye!\n")

    async def check_status(self) -> Optional[dict]:
        """Check the current status of the bot."""
        try:
            if not self.client.is_connected():
                await self.client.connect()

            me: User = await self.client.get_me()

            stats = self.stats.get_stats()

            return {
                'connected': self.client.is_connected(),
                'user': me.first_name,
                'username': me.username,
                'source_channel': self.source_channel,
                'destination_group': self.destination_group,
                'cache_size': len(self.forwarded_messages),
                'max_cache_size': self.max_cache_size,
                'watermark_enabled': bool(self.watermark),
                'watermark_text': self.watermark,
                'filters_enabled': self.filters.enabled,
                'uptime_seconds': stats['uptime_seconds'],
                'messages_forwarded': stats['messages_forwarded'],
                'messages_failed': stats['messages_failed'],
                'messages_blocked': stats['messages_blocked'],
            }

        except Exception as e:
            self.logger.error(f"Error checking status: {e}")
            return None


def parse_arguments() -> dict:
    """Parse command-line arguments."""
    args = {
        'verbose': '--verbose' in sys.argv or '-v' in sys.argv,
        'help': '--help' in sys.argv or '-h' in sys.argv,
    }

    if args['help']:
        print("""
Telegram Forwarder Bot - Advanced Features

Usage:
  python main.py [OPTIONS]

Options:
  --verbose, -v     Enable verbose console output (DEBUG level)
  --help, -h        Show this help message

Features:
  - Message filtering (keywords, blocklist, CA detection)
  - Rate limiting with random delays
  - Enhanced logging with rotation
  - /status command in destination chat
  - Graceful shutdown with cache save

Environment:
  See .env.example for all configuration options

Examples:
  python main.py              # Start with normal logging
  python main.py --verbose    # Start with verbose logging
  python main.py -v           # Same as --verbose

For more information, see README.md
""")
        sys.exit(0)

    return args


async def main() -> None:
    """Main entry point for the Telegram forwarder bot."""
    # Parse command-line arguments
    args = parse_arguments()

    forwarder = TelegramForwarder(verbose=args['verbose'])

    try:
        await forwarder.start()
    except KeyboardInterrupt:
        print(f"\n[INFO] {forwarder._get_timestamp()} - Shutdown requested by user")
    except Exception as e:
        print(f"[ERROR] {forwarder._get_timestamp()} - Fatal error in main: {e}")
    finally:
        await forwarder.stop()


if __name__ == '__main__':
    asyncio.run(main())
