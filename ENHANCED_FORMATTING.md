# Enhanced Message Formatting Feature

## Overview
This feature adds advanced message formatting capabilities for cryptocurrency trading signals, specifically designed for channels like @solearlytrending.

## Features

### 1. Automatic CA Extraction
- Detects Solana contract addresses (32-44 character base58 strings)
- Extracts token name and symbol from message text
- Supports multiple patterns: `$TICKER`, `#TICKER`, `Symbol:`, `Token:`

### 2. Quick Links Generation
- **Pump.fun**: Direct link to token page
- **DexScreener**: Live price and trading data

### 3. Structured Layout
```
🚨 NEW Solana CALL ⦿
───────────────────────────────────

📌 CA: `7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr`

📝 Signal:
Token: The Cancer Sniffer 📌
Symbol: #TCS

🔗 Quick Links:
🔗 Pump.fun: https://pump.fun/...
📊 DexScreener: https://dexscreener.com/solana/...

⚠️ Trade Responsibly
⏰ 17:14:23 UTC

━━━━━━━━━━━━━━━━━━━━
📡 via Fire intern
```

### 4. Watermark Stripping
Automatically removes common source channel watermarks:
- Divider lines (`────`, `──────`)
- "via @channel" patterns
- "Subscribe" messages
- Channel branding text

### 5. Custom Branding
Append your own watermark to all reformatted messages.

## Configuration

### Environment Variables

```bash
# Enable enhanced formatting
ENABLE_ENHANCED_FORMATTING=true

# Channels to apply formatting to (comma-separated)
ENHANCED_FORMATTING_CHANNELS=solearlytrending,cryptoalerts

# Strip source watermarks
STRIP_SOURCE_WATERMARKS=true

# Your custom watermark
CUSTOM_WATERMARK_ENHANCED=📡 via Fire intern
```

### Setup Instructions

1. **Update your `.env` file:**
   ```bash
   # Enable the feature
   ENABLE_ENHANCED_FORMATTING=true

   # Set channels to apply formatting to
   ENHANCED_FORMATTING_CHANNELS=solearlytrending

   # Customize your watermark
   CUSTOM_WATERMARK_ENHANCED=📡 via Fire intern
   ```

2. **Restart the bot:**
   ```bash
   python main.py
   ```

3. **Verify configuration:**
   ```bash
   python config.py
   ```
   This will display all configuration including enhanced formatting settings.

## How It Works

### Message Processing Flow

1. **Receive Message** from source channel
2. **Check Channel** - Is it in `ENHANCED_FORMATTING_CHANNELS`?
3. **Extract CA** - Find Solana contract address
4. **Parse Token Info** - Extract name and symbol
5. **Strip Watermarks** - Remove original branding
6. **Build Format** - Create structured layout
7. **Add Links** - Generate Pump.fun and DexScreener URLs
8. **Append Branding** - Add your custom watermark
9. **Forward** - Send to destination group

### Parser Details

**Solana CA Pattern:**
- Regex: `\b[1-9A-HJ-NP-Za-km-z]{32,44}\b`
- Matches: Base58 encoded strings 32-44 characters
- Example: `7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr`

**Token Symbol Patterns:**
- Hashtag: `$TICKER` or `#TICKER`
- Label: `Symbol: TICKER` or `Ticker: $TICKER`

**Token Name Patterns:**
- Label: `Token: Name` or `Name: Description`

## Examples

### Input Message (from @solearlytrending)
```
🚨 NEW CALL

Token: MoonShot 🚀
Symbol: $MOON

CA: 7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

Early entry! Get in now!

───────────────────
📡 via @solearlytrending
```

### Output Message (Forwarded)
```
🚨 NEW Solana CALL ⦿
───────────────────────────────────

📌 CA: `7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr`

📝 Signal:
Token: MoonShot 📌
Symbol: MOON

🔗 Quick Links:
🔗 Pump.fun: https://pump.fun/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
📊 DexScreener: https://dexscreener.com/solana/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

⚠️ Trade Responsibly
⏰ 17:14:23 UTC

━━━━━━━━━━━━━━━━━━━━
📡 via Fire intern
```

## Troubleshooting

### Messages Not Being Formatted

1. **Check if feature is enabled:**
   ```bash
   python config.py
   ```
   Look for: `Enhanced Formatting: ✅ Yes`

2. **Verify channel list:**
   - Ensure source channel is in `ENHANCED_FORMATTING_CHANNELS`
   - Don't include `@` symbol in channel names
   - Use lowercase: `solearlytrending` not `SOLEARLYTRENDING`

3. **Check logs:**
   ```bash
   tail -f logs/forwarder.log
   ```
   Look for: `Applying enhanced formatting`

### CA Not Being Extracted

- Ensure message contains a valid Solana address
- Solana addresses are 32-44 character base58 strings
- Check the message text is being received correctly

### Links Not Working

- Verify CA extraction is working
- Check network connectivity to Pump.fun and DexScreener
- Ensure links are not being truncated by Telegram

## Technical Details

### Files Modified

1. **`formatter.py`** (NEW)
   - Core formatting logic
   - CA extraction and parsing
   - Link generation

2. **`config.py`** (MODIFIED)
   - Added `ENABLE_ENHANCED_FORMATTING`
   - Added `ENHANCED_FORMATTING_CHANNELS`
   - Added `STRIP_SOURCE_WATERMARKS`
   - Added `CUSTOM_WATERMARK_ENHANCED`

3. **`main.py`** (MODIFIED)
   - Integrated formatter
   - Channel-based formatting selection
   - Preserved backward compatibility

4. **`.env.example`** (MODIFIED)
   - Added configuration documentation

### Backward Compatibility

The feature is **opt-in** and **backward compatible**:
- Default: `ENABLE_ENHANCED_FORMATTING=false`
- Existing functionality unchanged when disabled
- Standard watermark still applied to non-matching channels
- Media messages unaffected

## Future Enhancements

Potential improvements:
- [ ] Support for Ethereum/BSC tokens
- [ ] Custom formatting templates
- [ ] Multi-language support
- [ ] Price tracking integration
- [ ] Automated trading alerts
- [ ] Token analysis and scoring

## Support

For issues or questions:
1. Check logs: `logs/forwarder.log`
2. Verify configuration: `python config.py`
3. Test with verbose mode: `python main.py --verbose`
