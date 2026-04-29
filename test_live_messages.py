"""
Test live message monitoring - This will show if the bot receives messages
"""

import sys
import asyncio
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

sys.path.insert(0, '.')

from telethon import TelegramClient, events
from config import get_config

async def test_live_monitoring():
    """Test if we can receive messages from source channels."""

    config = get_config()

    print("="*70)
    print("LIVE MESSAGE MONITORING TEST")
    print("="*70)
    print()
    print("This will listen for 60 seconds for messages from your channels.")
    print("If you see messages here, the bot CAN receive them.")
    print()
    print(f"Monitoring: {', '.join(['@' + ch for ch in config.source_channels])}")
    print()
    print("Waiting for messages...")
    print("(Press Ctrl+C to stop early)")
    print("="*70)
    print()

    client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    # Connect FIRST before accessing channels
    await client.connect()

    if not await client.is_user_authorized():
        print("❌ NOT AUTHORIZED! Please run: python login.py")
        return

    # Get channel entities
    source_entities = []
    for channel in config.source_channels:
        try:
            entity = await client.get_entity(channel)
            source_entities.append(entity)
            print(f"✅ Found @{channel}: {entity.title}")
        except Exception as e:
            print(f"❌ Error accessing @{channel}: {e}")

    if not source_entities:
        print("\n❌ Cannot access any channels! You need to JOIN them in Telegram.")
        return

    print()
    print("="*70)
    print("LISTENING FOR MESSAGES (60 seconds)...")
    print("="*70)
    print()

    message_count = 0

    @client.on(events.NewMessage(chats=source_entities))
    async def handler(event):
        nonlocal message_count
        message_count += 1
        chat = await event.get_chat()
        source = getattr(chat, 'username', None) or getattr(chat, 'title', 'Unknown')

        print()
        print("🎉 MESSAGE RECEIVED!")
        print(f"   From: @{source}")
        print(f"   ID: {event.message.id}")
        print(f"   Text: {event.message.text[:100] if event.message.text else '(media)'}...")
        print()

    try:
        print("✅ Connected and listening...")
        print()

        # Wait for 60 seconds
        await asyncio.sleep(60)

    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        await client.disconnect()

    print()
    print("="*70)
    if message_count > 0:
        print(f"✅ SUCCESS! Received {message_count} message(s)")
        print("The bot CAN receive messages. The issue is elsewhere.")
    else:
        print("❌ NO MESSAGES RECEIVED")
        print("Either:")
        print("  1. No new messages were posted in the last 60 seconds, OR")
        print("  2. The bot cannot access the channels (try rejoining them)")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(test_live_monitoring())
