#!/usr/bin/env python3
"""
Telegram Forwarder Bot - Setup Test Script

This script validates that your .env file is properly configured and tests
the Telegram connection by sending a test message to your destination group.

USAGE:
    python test_setup.py

WHAT IT DOES:
    1. Loads and validates .env configuration
    2. Connects to Telegram using your credentials
    3. Verifies destination group access
    4. Sends a test message: "Forwarder setup test!"
    5. Reports success/failure with clear output

SECURITY:
    - Never prints or logs actual credential values
    - Only confirms presence/absence of required fields
"""

import os
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict

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

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    from telethon import TelegramClient
    from telethon.errors import RPCError, SessionPasswordNeededError
except ImportError as e:
    print(f"\n[ERROR] Missing required dependency: {e}")
    print("\nPlease install dependencies first:")
    print("   pip install -r requirements.txt\n")
    sys.exit(1)


# ANSI color codes for terminal output
class Colors:
    """Terminal color codes for better readability."""
    GREEN = '\033[92m'   # ✅ Success
    RED = '\033[91m'     # ❌ Error
    YELLOW = '\033[93m'  # ⚠️  Warning
    BLUE = '\033[94m'    # ℹ️  Info
    MAGENTA = '\033[95m' # 🔧 Config
    CYAN = '\033[96m'    # 📋 Section
    RESET = '\033[0m'    # Reset


def print_success(message: str) -> None:
    """Print success message with green checkmark."""
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print error message with red X."""
    print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print warning message with yellow triangle."""
    print(f"{Colors.YELLOW}[WARNING] {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print info message with blue i."""
    print(f"{Colors.BLUE}[INFO] {message}{Colors.RESET}")


def print_header(message: str) -> None:
    """Print section header."""
    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.CYAN}{message}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")


def print_subheader(message: str) -> None:
    """Print subsection header."""
    print(f"\n{Colors.MAGENTA}>> {message}{Colors.RESET}")


def check_env_file() -> Path:
    """Check if .env file exists and load it."""
    print_subheader("Checking for .env file...")

    env_path = Path('.env')

    if not env_path.exists():
        print_error("No .env file found!")
        print("\nPlease create a .env file:")
        print("   cp .env.example .env")
        print("\nThen edit .env with your Telegram credentials.\n")
        sys.exit(1)

    print_success(".env file found")
    return env_path


def validate_env_variables() -> Tuple[bool, Dict[str, Optional[str]]]:
    """
    Validate that all required environment variables are present.

    Returns:
        Tuple of (is_valid, dict_of_values)
        Note: Values are masked for security - we only check presence
    """
    print_subheader("Validating environment variables...")

    required_vars = {
        'API_ID': 'Numeric API ID from my.telegram.org',
        'API_HASH': 'API hash string from my.telegram.org',
        'DESTINATION_GROUP': 'Target group ID (e.g., -1001234567890)',
    }

    optional_vars = {
        'SESSION_NAME': 'forwarder_session',
        'SOURCE_CHANNEL': 'solearlytrending',
        'WATERMARK': '',
        'LOG_LEVEL': 'INFO',
    }

    missing_vars = []
    present_vars = {}

    # Check required variables
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            present_vars[var_name] = value
            # Mask the value for display
            if var_name == 'API_ID':
                print_success(f"{var_name}: ***{value[-2:]} (present)")
            elif var_name == 'API_HASH':
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
                print_success(f"{var_name}: {masked} (present)")
            else:
                print_success(f"{var_name}: Set")
        else:
            missing_vars.append(var_name)
            print_error(f"{var_name}: NOT FOUND - {description}")

    # Check optional variables
    print_info("\nOptional variables (will use defaults if not set):")
    for var_name, default_value in optional_vars.items():
        value = os.getenv(var_name)
        if value:
            print(f"   - {var_name}: Set (will use custom value)")
        else:
            print(f"   - {var_name}: Not set (will use: '{default_value}')")

    if missing_vars:
        print_error(f"\nMissing {len(missing_vars)} required variable(s)")
        print("\nPlease add these to your .env file:")
        for var in missing_vars:
            print(f"   {var}=<your_value>")
        print()

        return False, present_vars

    print_success("\nAll required environment variables are set!")
    return True, present_vars


def validate_api_id(api_id_str: str) -> Optional[int]:
    """Validate and convert API_ID to integer."""
    print_subheader("Validating API_ID format...")

    try:
        api_id = int(api_id_str)
        print_success(f"API_ID is a valid number: {api_id}")
        return api_id
    except ValueError:
        print_error("API_ID must be a numeric value")
        print("\nExample: API_ID=12345678")
        return None


def validate_api_hash(api_hash: str) -> bool:
    """Validate API_HASH format."""
    print_subheader("Validating API_HASH format...")

    if len(api_hash) < 32:
        print_error(f"API_HASH seems too short ({len(api_hash)} chars)")
        print("   API_HASH should be a long string (usually 32+ characters)")
        return False

    print_success(f"API_HASH length looks valid ({len(api_hash)} chars)")
    return True


def validate_destination_group(dest_str: str) -> Optional[int]:
    """Validate DESTINATION_GROUP format."""
    print_subheader("Validating DESTINATION_GROUP format...")

    try:
        group_id = int(dest_str)

        if group_id >= 0:
            print_error("DESTINATION_GROUP must be negative (starts with -100)")
            print("\nExample: DESTINATION_GROUP=-1001234567890")
            print("\nTo get your group ID:")
            print("   1. Add @getidsbot to your group")
            print("   2. Send /groupid command")
            print("   3. Copy the number (e.g., -1001234567890)")
            return None

        print_success(f"DESTINATION_GROUP format is valid: {group_id}")
        return group_id

    except ValueError:
        print_error("DESTINATION_GROUP must be a number")
        print("\nExample: DESTINATION_GROUP=-1001234567890")
        return None


async def test_telegram_connection(
    api_id: int,
    api_hash: str,
    session_name: str,
    destination_group: int
) -> bool:
    """
    Test Telegram connection and send test message.

    Returns:
        True if test successful, False otherwise
    """
    print_header("TESTING TELEGRAM CONNECTION")

    print_subheader("Initializing Telegram client...")
    print(f"   Session: {session_name}")
    print(f"   Target: {destination_group}")

    client = TelegramClient(session_name, api_id, api_hash)

    try:
        # Connect to Telegram
        print("\n[INFO] Connecting to Telegram servers...")
        await client.connect()

        if not await client.is_user_authorized():
            print_error("Not authorized! Please run login.py first")
            print("\nTo authenticate:")
            print("   python login.py")
            print("\n   Then:")
            print("   1. Enter your phone number with country code (+1...)")
            print("   2. Enter the confirmation code sent to Telegram")
            print("   3. If you have 2FA, enter your password")
            return False

        # Get user info
        me = await client.get_me()
        print_success(f"Connected as: {me.first_name} (@{me.username})")

        # Test destination group access
        print_subheader("Verifying destination group access...")
        try:
            dest_entity = await client.get_entity(destination_group)
            print_success(f"Destination group found: {dest_entity.title}")
        except RPCError as e:
            print_error(f"Cannot access destination group: {e}")
            print("\nMake sure:")
            print("   - You've added your bot account to the group")
            print("   - The group ID is correct")
            print("   - You have permission to send messages")
            return False

        # Send test message
        print_subheader("Sending test message...")
        test_message = "Forwarder setup test!"

        await client.send_message(destination_group, test_message)
        print_success(f"Test message sent to: {dest_entity.title}")
        print(f"   Message: \"{test_message}\"")

        print_info("\nCheck your destination group for the test message!")
        print_success("\nAll tests passed! Your setup is working correctly.")

        return True

    except SessionPasswordNeededError:
        print_error("Two-factor authentication enabled")
        print("\nPlease run: python login.py")
        print("   and enter your 2FA password when prompted")
        return False

    except RPCError as e:
        print_error(f"Telegram API error: {e}")
        print("\nCommon issues:")
        print("   - Invalid API credentials")
        print("   - Account doesn't exist in destination group")
        print("   - Network connection problems")
        return False

    except Exception as e:
        print_error(f"Unexpected error: {type(e).__name__}: {e}")
        return False

    finally:
        # Always disconnect
        await client.disconnect()
        print_info("\nDisconnected from Telegram")


def print_summary() -> None:
    """Print summary and next steps."""
    print_header("SUMMARY & NEXT STEPS")

    print("If all tests passed:")
    print("   1. Your .env file is configured correctly")
    print("   2. Telegram connection is working")
    print("   3. Destination group is accessible")
    print("   4. Test message was sent successfully")
    print()
    print("   You can now start the bot:")
    print("      python main.py")
    print()

    print("If tests failed:")
    print("   1. Review the error messages above")
    print("   2. Fix the issues in your .env file")
    print("   3. Make sure you've run: python login.py")
    print("   4. Run this test script again: python test_setup.py")
    print()

    print("For help, see: README.md")


async def main() -> None:
    """Main test flow."""
    print_header("TELEGRAM FORWARDER SETUP TEST")
    print_info("This script will test your configuration and Telegram connection")

    # Load environment variables
    load_dotenv()

    # Step 1: Check .env file exists
    check_env_file()

    # Step 2: Validate environment variables
    is_valid, env_vars = validate_env_variables()
    if not is_valid:
        sys.exit(1)

    # Step 3: Validate individual variables
    api_id = validate_api_id(env_vars.get('API_ID', ''))
    if not api_id:
        sys.exit(1)

    if not validate_api_hash(env_vars.get('API_HASH', '')):
        sys.exit(1)

    destination_group = validate_destination_group(env_vars.get('DESTINATION_GROUP', ''))
    if not destination_group:
        sys.exit(1)

    # Step 4: Test Telegram connection
    session_name = os.getenv('SESSION_NAME', 'forwarder_session')
    success = await test_telegram_connection(
        api_id=api_id,
        api_hash=env_vars.get('API_HASH', ''),
        session_name=session_name,
        destination_group=destination_group
    )

    # Step 5: Print summary
    print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"\nFatal error: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
