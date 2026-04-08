"""
Get Chat IDs Helper Script

This script helps you find the IDs of your Telegram chats, groups, and channels.
Use it to identify the DESTINATION_GROUP ID for your .env configuration.

SECURITY WARNING:
- Session files (*.session) contain authentication credentials
- NEVER share session files with anyone
- NEVER commit session files to version control
- Session files are as sensitive as your password!

Usage:
    python get_chat_ids.py
"""

import asyncio
from datetime import datetime
from typing import List, Dict

from telethon import TelegramClient
from telethon.tl.types import Chat, Channel, User
from config import get_config


def get_timestamp() -> str:
    """Get formatted timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_security_warning() -> None:
    """Print important security warnings."""
    print("\n" + "=" * 70)
    print("⚠️  SECURITY WARNING - READ CAREFULLY ⚠️")
    print("=" * 70)
    print()
    print("Session files (*.session) contain your Telegram authentication keys.")
    print("Treat them like PASSWORDS - keep them SAFE and PRIVATE!")
    print()
    print("❌ NEVER:")
    print("   - Share session files with anyone")
    print("   - Upload session files to GitHub, GitLab, or any public repository")
    print("   - Send session files via email, chat, or messaging apps")
    print("   - Store session files in cloud storage (Google Drive, Dropbox, etc.)")
    print()
    print("✅ ALWAYS:")
    print("   - Keep session files only on your secure local machine")
    print("   - Add *.session to .gitignore (already done in this project)")
    print("   - Delete old session files when no longer needed")
    print("   - Use different session names for different Telegram accounts")
    print()
    print("=" * 70)
    print()


async def get_all_chats(client: TelegramClient) -> List[Dict]:
    """
    Get all dialogs (chats, groups, channels) the user has access to.

    Args:
        client: Authenticated TelegramClient instance

    Returns:
        List of dictionaries containing chat information
    """
    print(f"[INFO] {get_timestamp()} - Fetching all chats...")

    chats = []

    # Get all dialogs
    async for dialog in client.iter_dialogs():
        chat_info = {
            'id': dialog.id,
            'name': dialog.name,
            'type': None,
            'username': getattr(dialog.entity, 'username', None),
        }

        # Determine chat type
        if isinstance(dialog.entity, Channel):
            if dialog.entity.megagroup:
                chat_info['type'] = 'Supergroup'
            else:
                chat_info['type'] = 'Channel'
        elif isinstance(dialog.entity, Chat):
            chat_info['type'] = 'Group'
        elif isinstance(dialog.entity, User):
            chat_info['type'] = 'Private Chat'
        else:
            chat_info['type'] = 'Unknown'

        chats.append(chat_info)

    print(f"[INFO] {get_timestamp()} - Found {len(chats)} chats")
    return chats


def display_chats(chats: List[Dict]) -> None:
    """
    Display all chats in a formatted table.

    Args:
        chats: List of chat dictionaries
    """
    print("\n" + "=" * 100)
    print("YOUR TELEGRAM CHATS, GROUPS, AND CHANNELS")
    print("=" * 100)
    print()

    # Group chats by type
    groups_channels = [c for c in chats if c['type'] in ['Group', 'Supergroup', 'Channel']]
    private_chats = [c for c in chats if c['type'] == 'Private Chat']

    # Display groups and channels first (most relevant for forwarding)
    if groups_channels:
        print("📢 GROUPS AND CHANNELS (use these IDs for DESTINATION_GROUP):")
        print("-" * 100)
        print(f"{'TYPE':<12} {'ID':<20} {'USERNAME':<25} {'NAME'}")
        print("-" * 100)

        for chat in sorted(groups_channels, key=lambda x: x['name'].lower()):
            username_display = f"@{chat['username']}" if chat['username'] else "(no username)"
            print(f"{chat['type']:<12} {chat['id']:<20} {username_display:<25} {chat['name']}")

        print()

    # Display private chats (less relevant but shown for completeness)
    if private_chats:
        print("💬 PRIVATE CHATS:")
        print("-" * 100)
        print(f"{'TYPE':<12} {'ID':<20} {'USERNAME':<25} {'NAME'}")
        print("-" * 100)

        for chat in sorted(private_chats, key=lambda x: x['name'].lower())[:20]:  # Limit to 20
            username_display = f"@{chat['username']}" if chat['username'] else "(no username)"
            print(f"{chat['type']:<12} {chat['id']:<20} {username_display:<25} {chat['name']}")

        if len(private_chats) > 20:
            print(f"... and {len(private_chats) - 20} more private chats")

    print()
    print("=" * 100)
    print()


def print_usage_instructions(chats: List[Dict]) -> None:
    """Print instructions on how to use the chat IDs."""
    print("📖 HOW TO USE THESE IDs:")
    print()
    print("1. Find your destination group in the list above")
    print("2. Copy the ID number (e.g., -1001234567890)")
    print("3. Add it to your .env file:")
    print()
    print("   DESTINATION_GROUP=-1001234567890")
    print()
    print("4. The ID should start with -100 for groups/channels")
    print()
    print("💡 TIP: Your destination group is most likely a 'Supergroup' or 'Group'")
    print()


async def main() -> None:
    """Main function to get and display all chat IDs."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TELEGRAM CHAT ID FINDER" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")

    # Print security warning
    print_security_warning()

    # Load configuration
    try:
        config = get_config()
        print(f"[INFO] {get_timestamp()} - Configuration loaded successfully")
    except Exception as e:
        print(f"[ERROR] {get_timestamp()} - Failed to load configuration: {e}")
        print("[INFO] Please make sure .env file exists and is properly configured")
        return

    # Create client
    client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    try:
        # Connect to Telegram
        print(f"[INFO] {get_timestamp()} - Connecting to Telegram...")
        await client.connect()

        # Check if authorized
        if not await client.is_user_authorized():
            print("[ERROR] You are not authorized!")
            print("[INFO] Please run: python login.py")
            print("[INFO] Then try this script again")
            return

        # Get user info
        me = await client.get_me()
        print(f"[SUCCESS] {get_timestamp()} - Connected as: {me.first_name} (@{me.username})")
        print()

        # Get all chats
        chats = await get_all_chats(client)

        # Display chats
        display_chats(chats)

        # Print usage instructions
        print_usage_instructions(chats)

        print("[SUCCESS] Chat ID retrieval completed!")
        print()
        print("Next steps:")
        print("1. Copy the group ID you want to use as DESTINATION_GROUP")
        print("2. Update your .env file with the ID")
        print("3. Run: python main.py")
        print()

    except KeyboardInterrupt:
        print(f"\n[INFO] {get_timestamp()} - Interrupted by user")
    except Exception as e:
        print(f"[ERROR] {get_timestamp()} - An error occurred: {e}")
    finally:
        # Disconnect
        await client.disconnect()
        print(f"[INFO] {get_timestamp()} - Disconnected from Telegram")
        print()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n[INFO] {get_timestamp()} - Script interrupted")
