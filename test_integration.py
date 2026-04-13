"""
Integration Test: Top Early Trending Filter in main.py

This test verifies that the filter is properly integrated into main.py
and works correctly with the TelegramForwarder class.
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, '.')

print("=" * 70)
print("Integration Test: Top Early Trending Filter")
print("=" * 70)
print()

# Test 1: Verify import works
print("Test 1: Verify imports")
print("-" * 70)
try:
    from filters import should_forward_message
    print("✅ should_forward_message imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
print()

# Test 2: Verify main.py can import the function
print("Test 2: Verify main.py imports")
print("-" * 70)
try:
    import main
    print("✅ main.py imports successfully")
    print(f"✅ should_forward_message available in main module: {hasattr(main, 'should_forward_message')}")
except Exception as e:
    print(f"❌ Failed to import main: {e}")
    sys.exit(1)
print()

# Test 3: Verify TelegramForwarder can be instantiated
print("Test 3: Verify TelegramForwarder class")
print("-" * 70)
try:
    from main import TelegramForwarder
    print("✅ TelegramForwarder class imported successfully")
    print(f"✅ TelegramForwarder has _forward_message method: {hasattr(TelegramForwarder, '_forward_message')}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)
print()

# Test 4: Test filter function with sample messages
print("Test 4: Test filter behavior")
print("-" * 70)

# Set environment variable for testing
os.environ['SKIP_TRENDING_UPDATES'] = 'true'

from filters import should_forward_message

# Test leaderboard (should be BLOCKED)
leaderboard_msg = """
🏆 Top Early Trending 🕊️
🥇 $NEET • 500X
🥈 $BULL • 205X
BUY TRENDING 🚀
"""

result1 = should_forward_message(leaderboard_msg)
print(f"Leaderboard message should_forward={result1}")
print(f"Expected: False (blocked)")
print(f"Status: {'✅ PASS' if not result1 else '❌ FAIL'}")
print()

# Test token call (should be FORWARDED)
token_call_msg = """
🚨 NEW CALL
Token: Moonshot
CA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
Symbol: #MOON
"""

result2 = should_forward_message(token_call_msg)
print(f"Token call should_forward={result2}")
print(f"Expected: True (forwarded)")
print(f"Status: {'✅ PASS' if result2 else '❌ FAIL'}")
print()

# Test 5: Verify environment variable toggle works
print("Test 5: Test environment variable toggle")
print("-" * 70)

# Disable filter
os.environ['SKIP_TRENDING_UPDATES'] = 'false'
result3 = should_forward_message(leaderboard_msg)
print(f"Leaderboard with SKIP_TRENDING_UPDATES=false: should_forward={result3}")
print(f"Expected: True (forwarded - filter disabled)")
print(f"Status: {'✅ PASS' if result3 else '❌ FAIL'}")
print()

# Re-enable filter
os.environ['SKIP_TRENDING_UPDATES'] = 'true'
result4 = should_forward_message(leaderboard_msg)
print(f"Leaderboard with SKIP_TRENDING_UPDATES=true: should_forward={result4}")
print(f"Expected: False (blocked - filter enabled)")
print(f"Status: {'✅ PASS' if not result4 else '❌ FAIL'}")
print()

# Test 6: Verify filter logging message
print("Test 6: Verify filter integration in main.py")
print("-" * 70)
print("Checking main.py source code for filter integration...")

with open('main.py', 'r', encoding='utf-8') as f:
    main_content = f.read()

checks = {
    'Import statement': 'from filters import get_filters, MessageFilters, should_forward_message' in main_content,
    'Filter check in _forward_message': 'if message.text and not should_forward_message(message.text):' in main_content,
    'Log message for blocked': 'Message {message_id} blocked: Top Early Trending update' in main_content,
    'Filter reason logged': 'Top Early Trending leaderboard update' in main_content,
}

for check_name, check_result in checks.items():
    status = '✅ PASS' if check_result else '❌ FAIL'
    print(f"  {check_name}: {status}")

all_checks_passed = all(checks.values())
print()
print(f"Integration check: {'✅ ALL CHECKS PASSED' if all_checks_passed else '❌ SOME CHECKS FAILED'}")
print()

# Final summary
print("=" * 70)
print("Integration Test Summary")
print("=" * 70)

all_tests_passed = (
    not result1 and  # Leaderboard blocked when enabled
    result2 and      # Token call forwarded
    result3 and      # Leaderboard forwarded when disabled
    not result4 and  # Leaderboard blocked when enabled
    all_checks_passed
)

if all_tests_passed:
    print("✅ ALL INTEGRATION TESTS PASSED")
    print()
    print("The Top Early Trending filter is fully integrated into main.py!")
    print()
    print("Next steps:")
    print("  1. Ensure SKIP_TRENDING_UPDATES=true in your .env file")
    print("  2. Run: python main.py")
    print("  3. Monitor logs for 'blocked: Top Early Trending update' messages")
else:
    print("❌ SOME TESTS FAILED")
    print("Please review the failures above")

print("=" * 70)
