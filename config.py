"""
Configuration module for Telegram Forwarder Bot.

Handles loading environment variables, validation, and providing defaults.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for the Telegram forwarder bot.

    Loads settings from environment variables with validation and defaults.
    """

    # Default values
    DEFAULT_SESSION_NAME = "forwarder_session"
    DEFAULT_SOURCE_CHANNEL = "solearlytrending"
    DEFAULT_WATERMARK = ""
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_RECONNECT_TIMEOUT = 10
    DEFAULT_MAX_RECONNECT_ATTEMPTS = 5
    DEFAULT_MAX_CACHE_SIZE = 1000

    def __init__(self) -> None:
        """Initialize configuration by loading and validating environment variables."""
        # Required fields
        self.api_id: int = self._load_api_id()
        self.api_hash: str = self._load_api_hash()

        # Optional fields with defaults
        self.session_name: str = os.getenv('SESSION_NAME', self.DEFAULT_SESSION_NAME)
        self.source_channel: str = os.getenv('SOURCE_CHANNEL', self.DEFAULT_SOURCE_CHANNEL)
        self.destination_group: int = self._load_destination_group()
        self.watermark: str = os.getenv('WATERMARK', self.DEFAULT_WATERMARK)
        self.log_level: str = os.getenv('LOG_LEVEL', self.DEFAULT_LOG_LEVEL).upper()
        self.reconnect_timeout: int = int(os.getenv('RECONNECT_TIMEOUT', str(self.DEFAULT_RECONNECT_TIMEOUT)))
        self.max_reconnect_attempts: int = int(os.getenv('MAX_RECONNECT_ATTEMPTS', str(self.DEFAULT_MAX_RECONNECT_ATTEMPTS)))
        self.max_cache_size: int = int(os.getenv('MAX_CACHE_SIZE', str(self.DEFAULT_MAX_CACHE_SIZE)))

        # Filter settings
        self.enable_filters: bool = os.getenv('ENABLE_FILTERS', 'false').lower() == 'true'
        self.filter_keywords: str = os.getenv('FILTER_KEYWORDS', '')
        self.filter_blocklist: str = os.getenv('FILTER_BLOCKLIST', '')
        self.detect_crypto_addresses: bool = os.getenv('DETECT_CRYPTO_ADDRESSES', 'false').lower() == 'true'
        self.require_crypto_address: bool = os.getenv('REQUIRE_CRYPTO_ADDRESS', 'false').lower() == 'true'

        # Rate limiting settings
        self.rate_limit_min_delay: float = float(os.getenv('RATE_LIMIT_MIN_DELAY', '0.5'))
        self.rate_limit_max_delay: float = float(os.getenv('RATE_LIMIT_MAX_DELAY', '2.0'))
        self.rate_limit_max_per_minute: int = int(os.getenv('RATE_LIMIT_MAX_PER_MINUTE', '30'))

        # Logging settings
        self.log_dir: str = os.getenv('LOG_DIR', 'logs')
        self.log_max_file_size: int = int(os.getenv('LOG_MAX_FILE_SIZE', '10')) * 1024 * 1024  # Convert MB to bytes
        self.log_backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        self.log_verbose: bool = os.getenv('LOG_VERBOSE', 'false').lower() == 'true'

        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}. Must be one of: {valid_log_levels}")

        # Validate rate limiting settings
        if self.rate_limit_min_delay < 0 or self.rate_limit_max_delay < 0:
            raise ValueError("Rate limit delays must be positive numbers")
        if self.rate_limit_min_delay > self.rate_limit_max_delay:
            raise ValueError("RATE_LIMIT_MIN_DELAY cannot be greater than RATE_LIMIT_MAX_DELAY")

    def _load_api_id(self) -> int:
        """Load and validate API_ID."""
        api_id_str = os.getenv('API_ID')
        if not api_id_str:
            raise ValueError(
                "API_ID is required! Please set it in .env file.\n"
                "Get it from: https://my.telegram.org/apps"
            )

        try:
            return int(api_id_str)
        except ValueError:
            raise ValueError(f"API_ID must be a number, got: {api_id_str}")

    def _load_api_hash(self) -> str:
        """Load and validate API_HASH."""
        api_hash = os.getenv('API_HASH')
        if not api_hash:
            raise ValueError(
                "API_HASH is required! Please set it in .env file.\n"
                "Get it from: https://my.telegram.org/apps"
            )

        if len(api_hash) < 32:
            raise ValueError(f"API_HASH seems invalid (too short). Length: {len(api_hash)}")

        return api_hash

    def _load_destination_group(self) -> int:
        """Load and validate DESTINATION_GROUP."""
        dest_group_str = os.getenv('DESTINATION_GROUP')
        if not dest_group_str:
            raise ValueError(
                "DESTINATION_GROUP is required! Please set it in .env file.\n"
                "Use @getidsbot in your group to get the ID.\n"
                "Example: DESTINATION_GROUP=-1001234567890"
            )

        try:
            group_id = int(dest_group_str)
            if group_id >= 0:
                raise ValueError(
                    f"DESTINATION_GROUP must be negative (starts with -100), got: {group_id}\n"
                    "Use @getidsbot to get the correct group ID"
                )
            return group_id
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(
                    f"DESTINATION_GROUP must be a number, got: {dest_group_str}\n"
                    "Example: DESTINATION_GROUP=-1001234567890"
                )
            raise

    def print_config(self) -> None:
        """
        Print configuration for debugging (without exposing secrets).

        Safe to call in production - masks sensitive values.
        """
        print("\n" + "=" * 70)
        print("TELEGRAM FORWARDER BOT - CONFIGURATION")
        print("=" * 70)

        # Basic configuration
        print("\n📋 BASIC SETTINGS:")
        print(f"  Session Name:         {self.session_name}")
        print(f"  Source Channel:       @{self.source_channel}")
        print(f"  Destination Group:    {self._mask_group_id(self.destination_group)}")
        print(f"  Watermark:            {self._mask_watermark()}")
        print(f"  Max Cache Size:       {self.max_cache_size} messages")

        # Filter configuration
        print("\n🔍 FILTER SETTINGS:")
        print(f"  Filters Enabled:      {'✅ Yes' if self.enable_filters else '❌ No'}")
        if self.enable_filters or self.filter_keywords or self.filter_blocklist:
            print(f"  Keywords:             {self.filter_keywords or '(none)'}")
            print(f"  Blocklist:            {self.filter_blocklist or '(none)'}")
            print(f"  Detect CA:            {'✅ Yes' if self.detect_crypto_addresses else '❌ No'}")
            print(f"  Require CA:           {'✅ Yes' if self.require_crypto_address else '❌ No'}")

        # Rate limiting configuration
        print("\n⏱️  RATE LIMITING:")
        print(f"  Min Delay:            {self.rate_limit_min_delay}s")
        print(f"  Max Delay:            {self.rate_limit_max_delay}s")
        print(f"  Max Per Minute:       {self.rate_limit_max_per_minute} messages")

        # Logging configuration
        print("\n📝 LOGGING:")
        print(f"  Log Directory:        {self.log_dir}/")
        print(f"  Max File Size:        {self.log_max_file_size // (1024*1024)} MB")
        print(f"  Backup Count:         {self.log_backup_count}")
        print(f"  Verbose Console:      {'✅ Yes' if self.log_verbose else '❌ No'}")

        # Masked sensitive fields
        print("\n🔐 API CREDENTIALS:")
        print(f"  API ID:               {self.api_id} (✓ valid)")
        print(f"  API Hash:             {self._mask_api_hash()} (length: {len(self.api_hash)})")

        print("\n" + "=" * 70 + "\n")

    def _mask_api_hash(self) -> str:
        """Mask API hash for display (show first 8 and last 4 chars)."""
        if len(self.api_hash) <= 12:
            return "****"
        return f"{self.api_hash[:8]}...{self.api_hash[-4:]}"

    def _mask_group_id(self, group_id: int) -> str:
        """Mask group ID for display (show last 10 digits only)."""
        group_str = str(group_id)
        if len(group_str) <= 10:
            return group_str
        return f"...{group_str[-10:]}"

    def _mask_watermark(self) -> str:
        """Show watermark status without full text."""
        if not self.watermark:
            return "❌ Disabled"
        # Show watermark but limit length
        if len(self.watermark) > 30:
            return f"✅ Enabled ({self.watermark[:20]}...)"
        return f"✅ Enabled ('{self.watermark}')"


# Global config instance
config = Config()


def print_config() -> None:
    """Print current configuration for debugging."""
    config.print_config()


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config: The loaded configuration object
    """
    return config


# Allow running config.py directly to test configuration
if __name__ == '__main__':
    try:
        print("[INFO] Loading configuration from .env...")
        config.print_config()
        print("[SUCCESS] Configuration is valid!")
    except ValueError as e:
        print(f"[ERROR] Configuration error:\n{e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
