"""
Test full message formatting with all 4 trading links
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

def test_full_formatting():
    """Test that all 4 links appear in formatted messages."""

    formatter = EnhancedFormatter(
        custom_watermark="📡 via Fire intern",
        strip_watermarks=True
    )

    # Test message with GeckoTerminal URL
    test_message = """
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

https://www.geckoterminal.com/solana/tokens/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
"""

    formatted = formatter.format_solana_message(test_message)

    print("="*70)
    print("FULL FORMATTED MESSAGE:")
    print("="*70)
    print(formatted)
    print("="*70)
    print()

    # Verify all links are present
    expected_domains = [
        'pump.fun',
        'dexscreener.com',
        'geckoterminal.com',
        'solscan.io'
    ]

    missing = []
    for domain in expected_domains:
        if domain not in formatted.lower():
            missing.append(domain)

    if missing:
        print(f"ERROR: Missing links for: {', '.join(missing)}")
        return False
    else:
        print("SUCCESS: All 4 trading links present!")
        print()
        print("Generated links:")
        print("  ✅ Pump.fun")
        print("  ✅ DexScreener")
        print("  ✅ GeckoTerminal")
        print("  ✅ Solscan")
        print()
        print("The bot now provides comprehensive trading links for all")
        print("major Solana analytics platforms!")
        return True

if __name__ == '__main__':
    success = test_full_formatting()
    sys.exit(0 if success else 1)
