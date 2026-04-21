"""
Test script to verify the complete message format with market cap
"""

import asyncio
import sys
from formatter import EnhancedFormatter


async def test_message_format():
    """Test the complete message format with market cap"""

    formatter = EnhancedFormatter()

    # Mock message with token info and CA
    test_message = """
    🚨 NEW CALL

    Token: Pepe Meme Coin
    Symbol: $PEPE

    CA: 7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

    https://pump.fun/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
    """

    # Redirect stdout to file with UTF-8 encoding
    original_stdout = sys.stdout
    with open('test_format_output.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f

        print("Testing complete message format:")
        print("=" * 70)

        # Test with market cap fetching disabled (will show N/A)
        formatted = await formatter.format_solana_message(test_message)

        print("\nFormatted Message:")
        print(formatted)
        print("\n" + "=" * 70)

        # Expected format check
        expected_elements = [
            "🚨 NEW Fire Intern CALL ⦿",
            "─────────",
            "📝 Signal:",
            "Token Name:",
            "🏦 Market Cap:",
            "📌 CA:",
            "`",  # CA should be wrapped in backticks
            "🔗",
            "[PUMP]",
            "[DEX]",
            "[GT]",
            "[SOL]",
            "⚠️ Trade Responsibly",
            "⏰",
            "UTC",
            "━━━━━━━━━━━━",
            "📡 via Fire intern",
        ]

        print("\nChecking expected elements:")
        all_present = True
        for element in expected_elements:
            if element in formatted:
                print(f"  OK: '{element}' found")
            else:
                print(f"  MISSING: '{element}' NOT found")
                all_present = False

        print("\n" + "=" * 70)
        if all_present:
            print("SUCCESS: All expected format elements are present!")
        else:
            print("WARNING: Some format elements are missing!")

    # Restore stdout
    sys.stdout = original_stdout

    # Print to console with ASCII-safe output
    print("Test complete. Results written to test_format_output.txt")
    with open('test_format_output.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        # Print ASCII-safe summary
        if "SUCCESS" in content:
            print("Status: SUCCESS - All format elements present!")
        else:
            print("Status: Check test_format_output.txt for details")

    # Close formatter
    await formatter.close()


if __name__ == "__main__":
    asyncio.run(test_message_format())
