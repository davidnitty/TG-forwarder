# GeckoTerminal URL Support - Complete

## What Was Added

✅ **GeckoTerminal URL extraction** - Now extracts Solana CA from GeckoTerminal links used by @solearlytrending

### URL Patterns Supported

**GeckoTerminal (NEW - Checked First):**
- `https://www.geckoterminal.com/solana/tokens/{CA}`
- `https://geckoterminal.com/solana/tokens/{CA}`
- `https://www.geckoterminal.com/solana/pools/{CA}`
- `https://geckoterminal.com/solana/pools/{CA}`

**Other Supported URLs:**
- `https://dexscreener.com/solana/{CA}`
- `https://pump.fun/{CA}`
- `https://solscan.io/token/{CA}`

## Why This Matters

@solearlytrending posts messages like this:
```
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

https://www.geckoterminal.com/solana/tokens/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
```

**Before Fix:** CA not extracted ❌
**After Fix:** CA extracted and formatted ✅

## Code Changes

**File: `formatter.py`**

Updated `extract_ca_from_url()` method:

```python
def extract_ca_from_url(self, text: str) -> Optional[str]:
    """Extract Solana CA from various URL types."""

    # Pattern for Solana CA in URLs (32-44 base58 chars)
    url_patterns = [
        # GeckoTerminal (check FIRST - @solearlytrending uses this!)
        r'geckoterminal\.com/solana/tokens/([1-9A-HJ-NP-Za-km-z]{32,44})',
        r'geckoterminal\.com/solana/pools/([1-9A-HJ-NP-Za-km-z]{32,44})',
        # DexScreener
        r'dexscreener\.com/solana/([1-9A-HJ-NP-Za-km-z]{32,44})',
        # Pump.fun
        r'pump\.fun/([1-9A-HJ-NP-Za-km-z]{32,44})',
        # Solscan
        r'solscan\.io/token/([1-9A-HJ-NP-Za-km-z]{32,44})',
    ]

    for pattern in url_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None
```

## Test Results

All tests pass:
```
✅ Test 1 - CA in text
✅ Test 2 - CA in GeckoTerminal URL (NEW!)
✅ Test 3 - CA in DexScreener URL
✅ Test 4 - CA in Pump.fun URL
✅ Test 5 - Direct URL extraction (DexScreener)
✅ Test 6 - Direct URL extraction (GeckoTerminal)
✅ Test 7 - No CA handling
```

## Priority Order

The bot checks URLs in this order (first match wins):

1. **GeckoTerminal tokens** - `geckoterminal.com/solana/tokens/{CA}`
2. **GeckoTerminal pools** - `geckoterminal.com/solana/pools/{CA}`
3. **DexScreener** - `dexscreener.com/solana/{CA}`
4. **Pump.fun** - `pump.fun/{CA}`
5. **Solscan** - `solscan.io/token/{CA}`

GeckoTerminal is checked **first** because @solearlytrending uses it!

## Example Output

**Input:**
```
🔥 Tweet to Earn New Trending
Age: 10m | Security: 🚨
MC: $23,103 • $45.8K
Liq: $12.1K
Vol: 1h: $68.5K

https://www.geckoterminal.com/solana/tokens/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
```

**Output:**
```
🚨 NEW Solana CALL ⦿
───────────────────────────

📌 CA: `3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5`

📝 Signal:

🔗 Quick Links:
🔗 Pump.fun: https://pump.fun/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
📊 DexScreener: https://dexscreener.com/solana/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5

⚠️ Trade Responsibly
⏰ UTC time
━━━━━━━━━━━━━━━━━━━━
📡 via Fire intern
```

## Files Modified

1. `formatter.py` - Added GeckoTerminal URL patterns
2. `test_ca_extraction.py` - Added GeckoTerminal tests
3. `test_geckoterminal.py` - Created comprehensive GeckoTerminal tests

## Summary

✅ GeckoTerminal URLs now supported
✅ Tested with both `/tokens/` and `/pools/` paths
✅ Works with or without `www.` prefix
✅ Checked before other URL services (priority)
✅ All existing tests still pass

The bot now fully supports @solearlytrending's GeckoTerminal links! 🚀
