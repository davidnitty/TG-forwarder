"""
Test Script for Enhanced Message Formatting

This script verifies:
1. Configuration loading
2. Enhanced formatter initialization
3. Message parsing and formatting with sample input
"""

import os
import sys

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("ENHANCED FORMATTING - CONFIGURATION VERIFICATION")
print("=" * 70)
print()

# ============================================
# STEP 1: VERIFY CONFIG LOADING
# ============================================
print("📋 STEP 1: Verifying Configuration Loading")
print("-" * 70)

# Check required environment variables
config_checks = {
    'WATERMARK': os.getenv('WATERMARK'),
    'ENABLE_ENHANCED_FORMATTING': os.getenv('ENABLE_ENHANCED_FORMATTING'),
    'STRIP_SOURCE_WATERMARKS': os.getenv('STRIP_SOURCE_WATERMARKS'),
    'CUSTOM_WATERMARK_ENHANCED': os.getenv('CUSTOM_WATERMARK_ENHANCED'),
    'ENHANCED_FORMATTING_CHANNELS': os.getenv('ENHANCED_FORMATTING_CHANNELS'),
}

all_loaded = True
for key, value in config_checks.items():
    status = "✅" if value is not None else "❌ NOT SET"
    print(f"  {status} {key}: {value}")
    if value is None:
        all_loaded = False

print()

if not all_loaded:
    print("⚠️  WARNING: Some config values are not set in .env")
    print("   Using default values from config.py")
else:
    print("✅ All configuration values loaded successfully!")
print()

# ============================================
# STEP 2: TEST FORMATTER INITIALIZATION
# ============================================
print("🔧 STEP 2: Testing Formatter Initialization")
print("-" * 70)

try:
    from formatter import init_formatter

    # Get config values with defaults
    custom_watermark = os.getenv('CUSTOM_WATERMARK_ENHANCED', '📡 via Fire intern')
    strip_watermarks = os.getenv('STRIP_SOURCE_WATERMARKS', 'true').lower() == 'true'

    # Initialize formatter
    formatter = init_formatter(
        custom_watermark=custom_watermark,
        strip_watermarks=strip_watermarks
    )

    print(f"  ✅ Formatter initialized successfully!")
    print(f"  • Custom watermark: '{formatter.custom_watermark}'")
    print(f"  • Strip watermarks: {formatter.strip_watermarks}")
    print()

except Exception as e:
    print(f"  ❌ ERROR: Failed to initialize formatter: {e}")
    sys.exit(1)

# ============================================
# STEP 3: DRY-RUN FORMAT TEST
# ============================================
print("🧪 STEP 3: Dry-Run Format Test")
print("-" * 70)
print()

# Sample input message from @solearlytrending
sample_input = """🚀 New Call!

Token: The Cancer Sniffer 📌
Symbol: #TCS

CA: 7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

Early entry! Get in now before moon! 🚀🚀🚀

───────────────────
📡 via SoEarlyTrending
Subscribe for more! t.me/solearlytrending"""

print("📥 INPUT MESSAGE:")
print("─" * 35)
print(sample_input)
print("─" * 35)
print()

# Test individual parsing functions
print("🔍 PARSING RESULTS:")
print("-" * 70)

# Test CA extraction
ca = formatter.extract_solana_ca(sample_input)
print(f"  ✅ CA Extracted: {ca}")
expected_ca = "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"
print(f"     Expected:     {expected_ca}")
print(f"     Match:        {'✅ YES' if ca == expected_ca else '❌ NO'}")
print()

# Test token info extraction
token_name, symbol = formatter.extract_token_info(sample_input)
print(f"  ✅ Token Name: {token_name}")
print(f"     Expected:   The Cancer Sniffer")
print(f"  ✅ Symbol: {symbol}")
print(f"     Expected: TCS")
print()

# Test watermark stripping
stripped_text = formatter.strip_source_watermarks(sample_input)
has_source_watermark = "via SoEarlyTrending" in stripped_text
has_subscribe = "Subscribe" in stripped_text or "t.me/solearlytrending" in stripped_text
print(f"  ✅ Watermark Stripping:")
print(f"     'via SoEarlyTrending' removed: {'✅ YES' if not has_source_watermark else '❌ NO'}")
print(f"     'Subscribe' removed:          {'✅ YES' if not has_subscribe else '❌ NO'}")
print()

# Generate formatted message
print("📤 FORMATTED OUTPUT:")
print("=" * 70)
formatted_output = formatter.format_solana_message(sample_input)
print(formatted_output)
print("=" * 70)
print()

# Verification checklist
print("✅ VERIFICATION CHECKLIST:")
print("-" * 70)

checklist = [
    ('Header contains "🚨 NEW Solana CALL ⦿"', "🚨 NEW Solana CALL" in formatted_output),
    ('CA extracted and in backticks', f"`{ca}`" in formatted_output),
    ('Token name included', token_name and "Token:" in formatted_output),
    ('Symbol included', symbol and "#" in formatted_output or "Symbol:" in formatted_output),
    ('Pump.fun link generated', f"https://pump.fun/{ca}" in formatted_output),
    ('DexScreener link generated', f"https://dexscreener.com/solana/{ca}" in formatted_output),
    ('Source watermark stripped', "via SoEarlyTrending" not in formatted_output and "Subscribe" not in formatted_output),
    ('Custom watermark appended', formatter.custom_watermark in formatted_output),
    ('Timestamp included', "⏰" in formatted_output and "UTC" in formatted_output),
    ('Trade responsibly warning', "⚠️ Trade Responsibly" in formatted_output or "⚠️" in formatted_output),
]

all_passed = True
for check, result in checklist:
    status = "✅" if result else "❌"
    print(f"  {status} {check}")
    if not result:
        all_passed = False

print()

if all_passed:
    print("🎉 SUCCESS! All checks passed!")
    print()
    print("📋 NEXT STEPS:")
    print("  1. Review the formatted output above")
    print("  2. If satisfied, proceed to live test:")
    print("     - Run: python main.py")
    print("     - Monitor @solearlytrending for new messages")
    print("     - Check your destination group for formatted output")
else:
    print("⚠️  WARNING: Some checks failed. Review the issues above.")
    print("   See troubleshooting section below.")
    print()

# ============================================
# STEP 4: TROUBLESHOOTING INFO
# ============================================
print("🔧 TROUBLESHOOTING:")
print("-" * 70)
print()
print("If issues occurred, check the following:")
print()
print("1. CA NOT EXTRACTED:")
print("   • Check if message contains valid Solana address (32-44 chars)")
print("   • Verify regex pattern in formatter.py: SOLANA_CA_PATTERN")
print()
print("2. TOKEN INFO NOT PARSED:")
print("   • Ensure message has 'Token:' or 'Name:' label")
print("   • Check for 'Symbol:', '$TICKER', or '#TICKER' patterns")
print()
print("3. WATERMARK NOT STRIPPED:")
print("   • Verify STRIP_SOURCE_WATERMARKS=true in .env")
print("   • Check WATERMARK_PATTERNS in formatter.py")
print("   • May need to add new pattern for different watermark style")
print()
print("4. LINKS BROKEN:")
print("   • Verify CA extraction worked (see #1)")
print("   • Check URL construction in format_solana_message()")
print()
print("5. FORMATTING NOT APPLIED:")
print("   • Ensure ENABLE_ENHANCED_FORMATTING=true in .env")
print("   • Check ENHANCED_FORMATTING_CHANNELS includes source")
print("   • Verify main.py logs show 'Applying enhanced formatting'")
print()

print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
