# Multi-Source Channel Update

## Summary

Updated the Telegram Forwarder Bot to support monitoring **multiple source channels** simultaneously while maintaining backward compatibility with single-channel configurations.

## What Changed

### 1. Configuration (`config.py`)
- Added support for `SOURCE_CHANNELS` environment variable (comma-separated list)
- Maintains backward compatibility with `SOURCE_CHANNEL` (single channel)
- Configuration now includes:
  - `self.source_channels`: List of all source channels
  - `self.source_channel`: First channel (for backward compatibility)

### 2. Environment Variables (`.env.example`)
```env
# NEW FORMAT - Multiple channels (recommended)
SOURCE_CHANNELS=solearlytrending,solhousesignal

# OLD FORMAT - Single channel (still supported)
# SOURCE_CHANNEL=solearlytrending
```

### 3. Core Forwarder (`main.py`)
- Updated to track which source channel each message originated from
- Event handlers now extract source channel from incoming messages
- All forwarded messages include source channel tracking
- Enhanced formatting works consistently across all channels
- Rate limiting, filtering, and duplicate prevention work across all channels

## Features

### ✅ Same Enhanced Formatting for All Channels
Both `@solearlytrending` and `@solhousesignal` will:
- Extract Solana contract addresses
- Generate Pump.fun + DexScreener links
- Apply structured message layout
- Strip source watermarks
- Add custom watermark

### ✅ Same Filters for All Channels
Both channels will:
- Skip "Top Early Trending" updates
- Apply keyword/blocklist filters (if enabled)
- Check crypto address requirements (if enabled)

### ✅ Unified Destination
All messages from all sources forward to the same destination group.

### ✅ Source Channel Tracking
The bot tracks which channel each message came from for logging and statistics.

## Configuration Example

```env
# Source channels (comma-separated, no @ symbol)
SOURCE_CHANNELS=solearlytrending,solhousesignal

# Destination
DESTINATION_GROUP=-1001234567890

# Enhanced formatting (enabled for both channels)
ENABLE_ENHANCED_FORMATTING=true
ENHANCED_FORMATTING_CHANNELS=solearlytrending,solhousesignal
STRIP_SOURCE_WATERMARKS=true
CUSTOM_WATERMARK_ENHANCED=📡 via Fire intern

# Skip trending updates (applies to all channels)
SKIP_TRENDING_UPDATES=true
```

## How It Works

### Message Flow
```
@solearlytrending ──┐
                   ├──▶ [Filter] ──▶ [Format] ──▶ [Forward] ──▶ Your Group
@solhousesignal ───┘
```

### Processing Steps
1. **Receive**: Bot monitors all configured source channels
2. **Identify**: Extract source channel from incoming message
3. **Filter**: Apply Top Early Trending filter + custom filters
4. **Format**: Apply enhanced formatting if enabled for that channel
5. **Forward**: Send to destination group
6. **Log**: Track source channel in logs and statistics

## Startup Output

When running with multiple channels:
```
[INFO] - Source channels: @solearlytrending, @solhousesignal
[INFO] - Total sources: 2 channels
[INFO] - NewMessage handler registered for 2 channels: @solearlytrending, @solhousesignal
[INFO] - MessageEdited handler registered for 2 channels: @solearlytrending, @solhousesignal
[SUCCESS] - Bot is running and monitoring for messages...
[INFO] - Monitoring 2 source channels: @solearlytrending, @solhousesignal
```

## Adding More Channels

Simply add more channels to the comma-separated list:
```env
SOURCE_CHANNELS=solearlytrending,solhousesignal,cryptoalerts,tokenwhale
```

And update enhanced formatting channels if needed:
```env
ENHANCED_FORMATTING_CHANNELS=solearlytrending,solhousesignal,cryptoalerts,tokenwhale
```

## Backward Compatibility

- Old `.env` files with `SOURCE_CHANNEL` will continue to work
- Single-channel setups show simplified output
- All existing features work unchanged

## Testing

To test the multi-channel setup:
1. Update your `.env` file with multiple channels
2. Run `python main.py`
3. Verify startup messages show all channels
4. Send test messages to each source channel
5. Verify messages arrive in destination with proper formatting

## Status Command

The `/status` command now shows:
- Total messages forwarded
- Messages from each source channel (in logs)
- Filter statistics
- Uptime and cache information
