"""
Test script to verify the Top Early Trending filter functionality.
"""

import re
import sys

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# Test messages
leaderboard_message = """🏆 Top Early Trending

🥇 TOKEN1 - 156X
🥈 TOKEN2 - 89X
🥉 TOKEN3 - 67X

BUY TRENDING 🚀"""

token_call = """🚨 NEW CALL
Token: MOONSHOT
CA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
Symbol: #MOON

Entry: 0.01
Target: 0.10

⚠️ Trade Responsibly"""


def is_top_trending_update(text: str) -> bool:
    """
    Detect if message is a 'Top Early Trending' leaderboard update.
    Return True if it should be SKIPPED (not forwarded).
    """
    if not text:
        return False

    # Key indicators of leaderboard updates
    skip_patterns = [
        r'🏆.*Top Early Trending',           # Header with trophy emoji
        r'🥇.*\d+X',                          # Gold medal + multiplier
        r'🥈.*\d+X',                          # Silver medal + multiplier
        r'🥉.*\d+X',                          # Bronze medal + multiplier
        r'BUY TRENDING 🚀',                   # Button text
        r'ⓓ.*ⓔ.*ⓐ.*ⓛ.*ⓔ.*ⓡ.*ⓣ.*ⓡ.*ⓔ.*ⓝ.*ⓖ.*ⓘ.*ⓝ.*ⓖ',  # Circled text variant
    ]

    # Check for multiple indicators (more reliable)
    matches = sum(1 for pattern in skip_patterns if re.search(pattern, text, re.IGNORECASE))

    # Skip if 2+ indicators found (reduces false positives)
    return matches >= 2


def test_filter():
    """Test the filter with sample messages."""

    # Example 3: Another call with different format (should be FORWARDED)
    another_call = """NEW SOlANA CALL 🔥

DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263

💎 $TOKEN - 100x potential
💎 LP burnt
💰 mc: 50k

🚀 Get in now!"""

    print("=" * 70)
    print("Top Early Trending Filter Test")
    print("=" * 70)
    print()

    # Test 1: Leaderboard (should SKIP)
    result1 = is_top_trending_update(leaderboard_message)
    print(f"Test 1 - Leaderboard Update:")
    print(f"  Result: {'BLOCKED ✅' if result1 else 'FORWARDED ❌'}")
    print(f"  Expected: BLOCKED")
    print(f"  Status: {'PASS ✓' if result1 else 'FAIL ✗'}")
    print()

    # Test 2: Token call (should FORWARD)
    result2 = is_top_trending_update(token_call)
    print(f"Test 2 - Individual Token Call:")
    print(f"  Result: {'BLOCKED ❌' if result2 else 'FORWARDED ✅'}")
    print(f"  Expected: FORWARDED")
    print(f"  Status: {'PASS ✓' if not result2 else 'FAIL ✗'}")
    print()

    # Test 3: Another call (should FORWARD)
    result3 = is_top_trending_update(another_call)
    print(f"Test 3 - Another Token Call:")
    print(f"  Result: {'BLOCKED ❌' if result3 else 'FORWARDED ✅'}")
    print(f"  Expected: FORWARDED")
    print(f"  Status: {'PASS ✓' if not result3 else 'FAIL ✗'}")
    print()

    # Summary
    all_passed = (result1 and not result2 and not result3)
    print("=" * 70)
    print(f"Overall Result: {'ALL TESTS PASSED ✅' if all_passed else 'SOME TESTS FAILED ✗'}")
    print("=" * 70)

    return all_passed


def test_trending_update_filter():
    """Verify Top Early Trending updates are detected and skipped"""

    # Import here to avoid issues with module loading
    import sys
    sys.path.insert(0, '.')
    from filters import should_forward_message

    # Should SKIP this
    leaderboard_msg = """
    🏆 Top Early Trending 🕊️
    🥇 $NEET • 500X
    🥈 $BULL • 205X
    BUY TRENDING 🚀
    """
    result1 = should_forward_message(leaderboard_msg)
    assert result1 == False, f"Expected False for leaderboard, got {result1}"
    print(f"✅ Leaderboard message correctly blocked (should_forward={result1})")

    # Should FORWARD this
    token_call_msg = """
    🚀 New Call!
    Token: The Cancer Sniffer
    CA: 7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
    """
    result2 = should_forward_message(token_call_msg)
    assert result2 == True, f"Expected True for token call, got {result2}"
    print(f"✅ Token call correctly allowed (should_forward={result2})")

    print("✅ Trending update filter tests passed!")


if __name__ == '__main__':
    test_filter()

    print("\n" + "=" * 70)
    print("Testing standalone should_forward_message() function")
    print("=" * 70)
    print()

    # Import the actual function from filters module
    import sys
    import os
    sys.path.insert(0, '.')
    from filters import should_forward_message

    # Test with leaderboard (should return False = don't forward)
    result1 = should_forward_message(leaderboard_message)
    print(f"Leaderboard message: should_forward_message() = {result1}")
    print(f"Expected: False (skip message)")
    print(f"Status: {'PASS ✓' if not result1 else 'FAIL ✗'}")
    print()

    # Test with token call (should return True = forward)
    result2 = should_forward_message(token_call)
    print(f"Token call message: should_forward_message() = {result2}")
    print(f"Expected: True (forward message)")
    print(f"Status: {'PASS ✓' if result2 else 'FAIL ✗'}")
    print()

    # Run the test function from user
    print("=" * 70)
    print("Running test_trending_update_filter()")
    print("=" * 70)
    print()
    test_trending_update_filter()
    print()

    # Test with environment variable disabled
    print("=" * 70)
    print("Testing with SKIP_TRENDING_UPDATES=false")
    print("=" * 70)
    print()

    original_env = os.getenv('SKIP_TRENDING_UPDATES')
    os.environ['SKIP_TRENDING_UPDATES'] = 'false'

    result3 = should_forward_message(leaderboard_message)
    print(f"Leaderboard message (filter disabled): should_forward_message() = {result3}")
    print(f"Expected: True (forward message - filter disabled)")
    print(f"Status: {'PASS ✓' if result3 else 'FAIL ✗'}")
    print()

    # Restore original environment
    if original_env is None:
        os.environ.pop('SKIP_TRENDING_UPDATES', None)
    else:
        os.environ['SKIP_TRENDING_UPDATES'] = original_env
