"""
Check if bot has access to source channels
"""

import sys
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

async def check_channels():
    """Check if bot can read from source channels."""

    config = get_config()

    print("="*70)
    print("Checking Channel Access")
    print("="*70)
    print()

    client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("❌ NOT AUTHORIZED!")
            return

        print("✅ Connected to Telegram")
        print()

        # Check each source channel
        for channel in config.source_channels:
            print(f"Checking @{channel}...")

            try:
                entity = await client.get_entity(channel)
                print(f"  ✅ HAVE ACCESS")
                print(f"     Title: {entity.title}")
                print(f"     Members: {getattr(entity, 'participants_count', 'N/A')}")
                print()

                # Try to get last message
                print(f"  Getting last message from @{channel}...")
                try:
                    async for message in client.iter_messages(entity, limit=1):
                        if message:
                            print(f"  ✅ Last message ID: {message.id}")
                            print(f"     Date: {message.date}")
                            print(f"     Text: {message.text[:100] if message.text else '(media)'}...")
                        break
                except Exception as e:
                    print(f"  ❌ Error reading messages: {e}")

            except Exception as e:
                print(f"  ❌ NO ACCESS: {e}")
                print()
                print(f"  ⚠️  SOLUTION:")
                print(f"     1. Open Telegram")
                print(f"     2. Go to @{channel}")
                print(f"     3. JOIN the channel")

            print()

        print("="*70)
        print("If all channels show ✅ HAVE ACCESS, the bot should work!")
        print("Send a test message to a channel and watch for logs.")
        print("="*70)

    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(check_channels())
