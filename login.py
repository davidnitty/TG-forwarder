"""
Telegram Authentication Script

This script handles first-time authentication with Telegram.
Run this once to create a session file before starting the bot.

SECURITY WARNING:
- Session files (*.session) contain authentication credentials
- NEVER share session files with anyone
- NEVER commit session files to version control
- Session files are as sensitive as your password!
"""

import asyncio
import sys
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from config import get_config

# Fix Windows terminal encoding issues
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def get_timestamp() -> str:
    """Get formatted timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_security_warning() -> None:
    """Print important security warnings about session files."""
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


async def login() -> None:
    """Login to Telegram and create session file."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "TELEGRAM AUTHENTICATION" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")

    # Print security warning
    print_security_warning()

    # Load configuration
    try:
        config = get_config()
        print(f"[INFO] {get_timestamp()} - Configuration loaded successfully")
        print(f"[INFO] {get_timestamp()} - Session name: {config.session_name}.session")
        print()
    except Exception as e:
        print(f"[ERROR] {get_timestamp()} - Failed to load configuration: {e}")
        print("[INFO] Please make sure .env file exists and is properly configured")
        print("[INFO] Required fields: API_ID, API_HASH")
        return

    # Get phone number from .env if available
    phone = os.getenv('PHONE')
    if phone:
        print(f"[INFO] {get_timestamp()} - Using phone from .env: {phone}")
        print()

    # Create client
    client = TelegramClient(config.session_name, config.api_id, config.api_hash)

    try:
        # Connect and start authentication
        print(f"[INFO] {get_timestamp()} - Connecting to Telegram...")
        print()

        # Start the client with phone from .env if available
        if phone:
            await client.start(phone=phone)
        else:
            await client.start()

        print()

        # Check if authorization was successful
        if await client.is_user_authorized():
            me = await client.get_me()

            print("╔" + "═" * 68 + "╗")
            print("║" + " " * 22 + "✅ LOGIN SUCCESSFUL ✅" + " " * 26 + "║")
            print("╚" + "═" * 68 + "╝")
            print()
            print(f"Account:         {me.first_name} {me.last_name or ''}")
            print(f"Username:        @{me.username}")
            print(f"Phone:           {me.phone}")
            print(f"User ID:         {me.id}")
            print()
            print(f"Session file:    {config.session_name}.session")
            print(f"Location:        {config.session_name}.session")
            print()
            print("⚠️  IMPORTANT SECURITY NOTES:")
            print("   1. Your session file has been created in the current directory")
            print("   2. Keep this file safe and secure - it contains your credentials")
            print("   3. Do NOT share this file with anyone")
            print("   4. Do NOT commit this file to version control")
            print("   5. You can now run: python main.py")
            print()

        else:
            print("[ERROR] Login failed. Please try again.")
            print("[INFO] Make sure you entered the correct phone number and verification code")

    except SessionPasswordNeededError:
        print("[ERROR] Two-factor authentication enabled but no password provided")
        print("[INFO] Please run the script again and enter your password when prompted")

    except KeyboardInterrupt:
        print(f"\n[INFO] {get_timestamp()} - Login cancelled by user")

    except Exception as e:
        print(f"[ERROR] {get_timestamp()} - An error occurred during login: {e}")
        print("[INFO] Please check your configuration and try again")

    finally:
        # Always disconnect
        await client.disconnect()
        print(f"[INFO] {get_timestamp()} - Disconnected from Telegram")
        print()


if __name__ == '__main__':
    try:
        asyncio.run(login())
    except KeyboardInterrupt:
        print(f"\n[INFO] {get_timestamp()} - Script interrupted")
