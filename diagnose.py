"""
Diagnostic script to check bot configuration and permissions
"""

import sys
import os
import asyncio

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

sys.path.insert(0, '.')

from config import get_config
from telethon import TelegramClient

async def diagnose():
    """Check bot configuration and permissions."""

    print("="*70)
    print("TG-Forwarder Diagnostic Tool")
    print("="*70)
    print()

    # Load config
    try:
        config = get_config()
        print("✅ Configuration loaded successfully")
        print()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return

    # Show config
    print("Current Configuration:")
    print(f"  Session: {config.session_name}")
    print(f"  API ID: {config.api_id}")
    print(f"  Source Channels: {config.source_channels}")
    print(f"  Destination: {config.destination_group}")
    print(f"  Enhanced Formatting: {config.enable_enhanced_formatting}")
    print(f"  Enhanced Channels: {config.enhanced_formatting_channels}")
    print()

    # Connect to Telegram
    print("Connecting to Telegram...")
    client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("❌ NOT AUTHORIZED! Please run: python login.py")
            return

        print("✅ Authorized and connected")
        print()

        # Get user info
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username})")
        print(f"Phone: {me.phone}")
        print()

        # Check source channels
        print("Checking source channels...")
        for channel in config.source_channels:
            try:
                # Try to get channel entity
                entity = await client.get_entity(channel)
                print(f"  ✅ @{channel} - Access granted")
                print(f"     Title: {entity.title}")
                print(f"     ID: {entity.id}")
            except Exception as e:
                print(f"  ❌ @{channel} - Error: {e}")
                print(f"     You need to JOIN this channel first!")
        print()

        # Check destination group
        print("Checking destination group...")
        try:
            dest_entity = await client.get_entity(config.destination_group)
            print(f"  ✅ Destination group - Access granted")
            print(f"     Title: {dest_entity.title}")
            print(f"     ID: {dest_entity.id}")
        except Exception as e:
            print(f"  ❌ Destination group - Error: {e}")
            print(f"     You need to ADD THE BOT to this group!")
        print()

        print("="*70)
        print("Diagnostic Complete")
        print("="*70)
        print()
        print("Next Steps:")
        print("1. If channels show errors - JOIN them in Telegram")
        print("2. If destination shows error - ADD BOT to the group")
        print("3. Then run: python main.py")

    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(diagnose())
