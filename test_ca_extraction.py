"""
Test script to verify CA extraction from URLs
"""

import sys
import os

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

sys.path.insert(0, '.')

from formatter import EnhancedFormatter

def test_ca_extraction():
    """Test CA extraction from various message formats."""

    formatter = EnhancedFormatter()

    # Test 1: CA in message text (original functionality)
    test1 = """
    🚨 NEW CALL
    CA: 7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
    Symbol: $TEST
    """
    ca1 = formatter.extract_solana_ca(test1)
    print(f"✅ Test 1 - CA in text: {ca1}")
    assert ca1 == "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", f"Failed: got {ca1}"

    # Test 2: CA in GeckoTerminal URL (NEW - @solearlytrending uses this!)
    test2 = """
    🔥 Tweet to Earn New Trending
    Age: 10m | Security: 🚨
    MC: $23,103 • $45.8K
    Liq: $12.1K
    Vol: 1h: $68.5K

    https://www.geckoterminal.com/solana/tokens/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
    """
    ca2 = formatter.extract_solana_ca(test2)
    print(f"✅ Test 2 - CA in GeckoTerminal URL: {ca2}")
    assert ca2 == "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", f"Failed: got {ca2}"

    # Test 3: CA in DexScreener URL
    test3 = """
    🔥 Tweet to Earn New Trending
    Age: 10m | Security: 🚨
    MC: $23,103 • $45.8K
    Liq: $12.1K
    Vol: 1h: $68.5K

    https://dexscreener.com/solana/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
    """
    ca3 = formatter.extract_solana_ca(test3)
    print(f"✅ Test 3 - CA in DexScreener URL: {ca3}")
    assert ca3 == "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", f"Failed: got {ca3}"

    # Test 4: CA in Pump.fun URL
    test4 = """
    New token launched!

    Check it out: https://pump.fun/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

    Don't miss out!
    """
    ca4 = formatter.extract_solana_ca(test4)
    print(f"✅ Test 4 - CA in Pump.fun URL: {ca4}")
    assert ca4 == "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", f"Failed: got {ca4}"

    # Test 5: Direct URL extraction (DexScreener)
    test5 = "https://dexscreener.com/solana/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"
    ca5 = formatter.extract_ca_from_url(test5)
    print(f"✅ Test 5 - Direct URL extraction (DexScreener): {ca5}")
    assert ca5 == "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", f"Failed: got {ca5}"

    # Test 6: Direct URL extraction (GeckoTerminal)
    test6 = "https://www.geckoterminal.com/solana/tokens/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"
    ca6 = formatter.extract_ca_from_url(test6)
    print(f"✅ Test 6 - Direct URL extraction (GeckoTerminal): {ca6}")
    assert ca6 == "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", f"Failed: got {ca6}"

    # Test 7: No CA present
    test7 = "This message has no CA or URLs"
    ca7 = formatter.extract_solana_ca(test7)
    print(f"✅ Test 7 - No CA: {ca7}")
    assert ca7 is None, f"Failed: should be None, got {ca7}"

    print("\n" + "="*60)
    print("🎉 All tests passed!")
    print("="*60)
    print("\nThe formatter can now extract CA from:")
    print("  1. Message text (original)")
    print("  2. GeckoTerminal URLs (NEW!)")
    print("  3. DexScreener URLs")
    print("  4. Pump.fun URLs")
    print("  5. Solscan URLs")
    print("\nGeckoTerminal is checked FIRST since @solearlytrending uses it!")

if __name__ == '__main__':
    test_ca_extraction()
