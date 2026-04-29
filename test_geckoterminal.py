"""
Test GeckoTerminal URL CA extraction
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

def test_geckoterminal_extraction():
    """Test GeckoTerminal URL CA extraction."""

    formatter = EnhancedFormatter()

    # Test 1: GeckoTerminal tokens URL
    test1 = """
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

https://www.geckoterminal.com/solana/tokens/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
"""
    ca1 = formatter.extract_solana_ca(test1)
    print(f"Test 1 - GeckoTerminal tokens URL: {ca1}")
    assert ca1 == "3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5"

    # Test 2: GeckoTerminal pools URL
    test2 = """
New pool launched!

Check: https://geckoterminal.com/solana/pools/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
"""
    ca2 = formatter.extract_solana_ca(test2)
    print(f"Test 2 - GeckoTerminal pools URL: {ca2}")
    assert ca2 == "3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5"

    # Test 3: Mixed URLs (GeckoTerminal + DexScreener)
    test3 = """
Multiple links:

https://www.geckoterminal.com/solana/tokens/ABC123DEF456ABC123DEF456ABC123DEF456ABC
https://dexscreener.com/solana/XYZ789XYZ789XYZ789XYZ789XYZ789XYZ789XYZ789
"""
    ca3 = formatter.extract_solana_ca(test3)
    print(f"Test 3 - Mixed URLs (first CA wins): {ca3}")
    # Should extract first CA found (GeckoTerminal)
    assert ca3 == "ABC123DEF456ABC123DEF456ABC123DEF456ABC"

    # Test 4: www.geckoterminal.com without www
    test4 = "https://geckoterminal.com/solana/tokens/TESTCA123456789TESTCA123456789TESTCA"
    ca4 = formatter.extract_solana_ca(test4)
    print(f"Test 4 - Without www prefix: {ca4}")
    assert ca4 == "TESTCA123456789TESTCA123456789TESTCA"

    print("\n" + "="*60)
    print("All GeckoTerminal tests passed!")
    print("="*60)
    print("\nSupported URL patterns:")
    print("  - geckoterminal.com/solana/tokens/{CA}")
    print("  - geckoterminal.com/solana/pools/{CA}")
    print("  - www.geckoterminal.com/solana/tokens/{CA}")
    print("  - www.geckoterminal.com/solana/pools/{CA}")
    print("\nOrder of precedence:")
    print("  1. GeckoTerminal (checked first)")
    print("  2. DexScreener")
    print("  3. Pump.fun")
    print("  4. Solscan")

if __name__ == '__main__':
    test_geckoterminal_extraction()
