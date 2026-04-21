"""
Test script to verify market cap formatting
"""

from formatter import EnhancedFormatter


def test_market_cap_formatting():
    """Test the market cap formatting function"""

    formatter = EnhancedFormatter()

    test_cases = [
        (500, "$500"),
        (1500, "$1.5K"),
        (10500, "$10.5K"),
        (1500000, "$1.5M"),
        (1200000, "$1.2M"),
        (3400000000, "$3.4B"),
        (1500000000, "$1.5B"),
    ]

    print("Testing market cap formatting:")
    print("=" * 50)
    for market_cap, expected in test_cases:
        result = formatter.format_market_cap(market_cap)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: {market_cap:,} -> {result} (expected: {expected})")
    print("=" * 50)


if __name__ == "__main__":
    test_market_cap_formatting()
