"""
Test script to verify basic message formatting (no CA)
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

sys.path.insert(0, '.')

from formatter import EnhancedFormatter

def test_basic_formatting():
    """Test that messages without CA are forwarded as-is with watermark."""

    formatter = EnhancedFormatter(
        custom_watermark="📡 via Fire intern",
        strip_watermarks=True
    )

    # Test 1: Message without CA
    test1 = """🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

https://dexscreener.com/solana/INVALIDCA"""

    result1 = formatter._format_basic_message(test1)

    print("="*60)
    print("Test 1: Message without CA (should be forwarded as-is)")
    print("="*60)
    print(result1)
    print()

    # Verify watermark is added
    assert "📡 via Fire intern" in result1, "Watermark missing!"
    assert "━━━━━━━━━━━━━━━━━━━━" in result1, "Divider missing!"

    # Test 2: Message with existing watermark to strip
    test2 = """Some message text

──────────────
via @otherchannel"""

    result2 = formatter._format_basic_message(test2)

    print("="*60)
    print("Test 2: Message with watermark (should be stripped + new watermark)")
    print("="*60)
    print(result2)
    print()

    # Verify original watermark stripped
    assert "via @otherchannel" not in result2, "Original watermark not stripped!"
    assert "📡 via Fire intern" in result2, "New watermark missing!"

    # Test 3: Empty watermark
    formatter_no_watermark = EnhancedFormatter(
        custom_watermark="",
        strip_watermarks=True
    )

    test3 = "Plain message without CA"
    result3 = formatter_no_watermark._format_basic_message(test3)

    print("="*60)
    print("Test 3: No watermark configured (should return as-is)")
    print("="*60)
    print(result3)
    print()

    # Verify no watermark added
    assert result3 == "Plain message without CA", f"Unexpected: {result3}"

    print("="*60)
    print("✅ All basic formatting tests passed!")
    print("="*60)
    print()
    print("Summary:")
    print("  1. Messages without CA forwarded as-is")
    print("  2. Original watermarks stripped")
    print("  3. Custom watermark added")
    print("  4. Works correctly when watermark disabled")

if __name__ == '__main__':
    test_basic_formatting()
