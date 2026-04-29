# Enhanced Formatting Flow - Complete Logic

## Message Processing Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Message Received from Source Channel                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Check Filters                                            │
│    - Skip trending updates? (SKIP_TRENDING_UPDATES)         │
│    - Duplicate check?                                       │
│    - Keyword/blocklist filters? (ENABLE_FILTERS)            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Format Message Text                                      │
│                                                             │
│    Is enhanced formatting enabled for this channel?        │
│    ┌──────────────────────────────────────┐               │
│    │ Check:                                │               │
│    │ - ENABLE_ENHANCED_FORMATTING=true     │               │
│    │ - Channel in ENHANCED_FORMATTING_     │               │
│    │   CHANNELS list                       │               │
│    └──────────────┬───────────────────────┘               │
│                   │                                          │
│         ┌─────────┴─────────┐                              │
│         │                   │                              │
│        YES                 NO                              │
│         │                   │                              │
│         ▼                   ▼                              │
│  ┌──────────────┐   ┌──────────────┐                     │
│  │   Enhanced   │   │   Standard    │                     │
│  │ Formatting   │   │   Watermark   │                     │
│  └──────┬───────┘   └──────┬───────┘                     │
│         │                   │                              │
└─────────┴───────────────────┴──────────────────────────────┘
          │
          ▼
```

## Enhanced Formatting Branch (YES)

```
┌─────────────────────────────────────────────────────────────┐
│ Try to extract Solana CA                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
        CA Found           No CA
         │                   │
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│ Enhanced Format  │  │  Basic Format    │
│                  │  │                  │
│ - Header         │  │ - Original text  │
│ - CA section     │  │ - Strip source   │
│ - Token info     │  │   watermarks     │
│ - Pump.fun link  │  │ - Add custom     │
│ - DexScreener    │  │   watermark      │
│   link           │  │                  │
│ - Warning        │  │  Example:        │
│ - Timestamp      │  │  Original msg    │
│ - Custom WM      │  │  ━━━━━━━━━━━━   │
│                  │  │  📡 via Fire...  │
└──────────────────┘  └──────────────────┘
```

## Standard Watermark Branch (NO)

```
┌─────────────────────────────────────────────────────────────┐
│ Just add watermark to original text                        │
└─────────────────────────────────────────────────────────────┘

    Original Message
    ━━━━━━━━━━━━━━━━━
    📡 via Fire intern
```

## Code Reference

### Main Entry Point: `main.py:_format_message_text()`

```python
def _format_message_text(self, text: str, source_channel: str) -> str:
    """Format message text with watermark or enhanced formatting."""
    if not text:
        return text or ''

    # Use enhanced formatting if enabled for this channel
    if self._should_use_enhanced_formatting(source_channel):
        self.logger.debug("Applying enhanced formatting")
        return self.enhanced_formatter.format_solana_message(text)

    # Use standard watermark
    return self._add_watermark_to_text(text)
```

### Enhanced Formatter: `formatter.py:format_solana_message()`

```python
def format_solana_message(self, original_text: str) -> str:
    # Extract CA (tries text, then URLs)
    ca = self.extract_solana_ca(original_text)

    if not ca:
        # No CA - forward as-is with watermark
        return self._format_basic_message(original_text)

    # CA found - full enhanced formatting
    token_name, symbol = self.extract_token_info(original_text)
    # ... build formatted message with links
```

## Examples

### Example 1: CA in Text

**Input:**
```
🚨 NEW CALL
CA: 7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
Symbol: $TEST
```

**Output:**
```
🚨 NEW Solana CALL ⦿
───────────────────────────

📌 CA: `7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr`

📝 Signal:
Symbol: #TEST

🔗 Quick Links:
🔗 Pump.fun: https://pump.fun/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
📊 DexScreener: https://dexscreener.com/solana/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

⚠️ Trade Responsibly
⏰ 20:59:07 UTC
━━━━━━━━━━━━━━━━━━━━
📡 via Fire intern
```

### Example 2: CA in DexScreener URL (NEW!)

**Input:**
```
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

https://dexscreener.com/solana/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
```

**Output:** (Same as Example 1 - extracts CA from URL!)

### Example 3: No CA Found

**Input:**
```
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

──────────────────
via @otherchannel
```

**Output:**
```
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

━━━━━━━━━━━━━━━━━━━━
📡 via Fire intern
```

(Note: Original watermark stripped, custom watermark added)

### Example 4: Enhanced Formatting Disabled

**Input:** Any message

**Output:**
```
[Original message text]

━━━━━━━━━━━━━━━━━━━━
📡 via Fire intern
```

(Simple watermark without any modifications)

## Configuration Controls

```env
# Enable enhanced formatting globally
ENABLE_ENHANCED_FORMATTING=true

# Which channels to apply it to
ENHANCED_FORMATTING_CHANNELS=solearlytrending,solhousesignal

# Custom watermark text
WATERMARK=📡 via Fire intern

# Strip original watermarks
STRIP_SOURCE_WATERMARKS=true
```

## Summary

✅ **CA in text** → Full enhanced formatting with links
✅ **CA in URL** → Full enhanced formatting with links (NEW!)
✅ **No CA** → Forward as-is with watermark
✅ **Enhanced disabled** → Just add watermark
✅ **Original watermarks** → Always stripped when enhanced formatting enabled
