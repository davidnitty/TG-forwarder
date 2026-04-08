"""
Telegram Forwarder Bot - Status Checker

This module provides a command-line utility to check the bot's status,
configuration, and statistics.
"""

import asyncio
from datetime import datetime
from main import TelegramForwarder


def get_timestamp() -> str:
    """Get formatted timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def show_status() -> None:
    """Show the current status of the forwarder bot."""
    print(f"[INFO] {get_timestamp()} - Checking bot status...\n")

    forwarder = TelegramForwarder()

    try:
        # Connect to Telegram to check status
        await forwarder.client.connect()

        # Get status dictionary
        status = await forwarder.check_status()

        if status:
            # Display formatted status
            print("=" * 60)
            print("TELEGRAM FORWARDER BOT STATUS")
            print("=" * 60)
            print(f"Connection Status:      {'✅ Connected' if status['connected'] else '❌ Disconnected'}")
            print(f"Authenticated User:     {status['user']} (@{status['username']})")
            print(f"Source Channel:         @{status['source_channel']}")
            print(f"Destination Group:      {status['destination_group']}")
            print(f"Cache Size:             {status['cache_size']} / {status['max_cache_size']} messages")
            print(f"Watermark:              {'✅ Enabled' if status['watermark_enabled'] else '❌ Disabled'}")
            if status['watermark_enabled']:
                print(f"Watermark Text:         '{status['watermark_text']}'")
            print("=" * 60)
            print()

            # Additional info
            if status['cache_size'] > 0:
                cache_usage = (status['cache_size'] / status['max_cache_size']) * 100
                print(f"[INFO] Cache usage: {cache_usage:.1f}%")

                if cache_usage >= 90:
                    print(f"[WARN] Cache is almost full! Consider cleaning old entries.")
                elif cache_usage >= 50:
                    print(f"[INFO] Cache is half full. Old entries will be auto-removed.")

            print(f"[INFO] Status check completed successfully")

        else:
            print("[ERROR] Could not retrieve status.")
            print("[INFO] Please check your configuration in .env file")
            print("[INFO] Make sure you've run: python login.py")

    except FileNotFoundError:
        print("[ERROR] .env file not found!")
        print("[INFO] Please copy .env.example to .env and fill in your credentials")
        print("[INFO] Run: cp .env.example .env")

    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        print("[INFO] Please check your .env file for invalid values")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        print("[INFO] Check that .env is configured correctly")

    finally:
        # Always disconnect
        await forwarder.client.disconnect()
        print()


if __name__ == '__main__':
    try:
        asyncio.run(show_status())
    except KeyboardInterrupt:
        print(f"\n[INFO] {get_timestamp()} - Status check interrupted by user")
    except Exception as e:
        print(f"[ERROR] {get_timestamp()} - Fatal error: {e}")
