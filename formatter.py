"""
Enhanced Message Formatter Module

Provides advanced message formatting for cryptocurrency trading signals.
Automatically extracts contract addresses, token information, and generates
tracking links for Pump.fun and DexScreener.
"""

import re
import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple


class EnhancedFormatter:
    """
    Enhanced message formatter for crypto trading signals.

    Features:
    - Extract Solana contract addresses
    - Parse token name and symbol
    - Generate Pump.fun and DexScreener links
    - Format messages with structured layout
    - Strip source watermarks
    - Add custom branding
    """

    # Regex patterns for parsing crypto messages
    SOLANA_CA_PATTERN = re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b')
    TOKEN_SYMBOL_PATTERN = re.compile(r'[#$]([A-Z0-9]{2,10})\b')
    TICKER_PATTERN = re.compile(r'(?:Symbol|Ticker)[:\s]*([# $]*[A-Z]{2,10})', re.IGNORECASE)
    TOKEN_NAME_PATTERN = re.compile(r'(?:Token|Name|Coin)[:\s]*([^\n#]{3,30})', re.IGNORECASE)

    # Common watermark patterns to strip
    WATERMARK_PATTERNS = [
        re.compile(r'\n?─{10,}.*$', re.DOTALL),
        re.compile(r'\n?\|{10,}.*$', re.DOTALL),
        re.compile(r'\n?=+$.*$', re.DOTALL),
        re.compile(r'\n?📱.*via.*$', re.DOTALL | re.IGNORECASE),
        re.compile(r'\n?🔔.*channel.*$', re.DOTALL | re.IGNORECASE),
        re.compile(r'\n?📡.*forwarded.*$', re.DOTALL | re.IGNORECASE),
        re.compile(r'\n?Subscribe.*$', re.DOTALL | re.IGNORECASE),
        re.compile(r'\n?t\.me/.*$', re.DOTALL),
    ]

    def __init__(
        self,
        custom_watermark: str = "📡 via Fire intern",
        strip_watermarks: bool = True
    ):
        """
        Initialize the enhanced formatter.

        Args:
            custom_watermark: Custom watermark text to append
            strip_watermarks: Whether to strip source watermarks
        """
        self.custom_watermark = custom_watermark
        self.strip_watermarks = strip_watermarks
        self._http_session: Optional[aiohttp.ClientSession] = None

    async def _get_http_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for API requests."""
        if self._http_session is None or self._http_session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._http_session = aiohttp.ClientSession(timeout=timeout)
        return self._http_session

    async def close(self):
        """Close HTTP session if exists."""
        if self._http_session and not self._http_session.closed:
            await self._http_session.close()

    async def fetch_market_cap_from_pumpfun(self, ca: str) -> Optional[float]:
        """
        Fetch market cap from pump.fun API for a given contract address.

        Args:
            ca: Solana contract address

        Returns:
            Market cap in USD or None if not available
        """
        try:
            session = await self._get_http_session()
            url = f"https://api.pump.fun/coins/{ca}"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # pump.fun API returns market_cap in the response
                    if 'market_cap' in data:
                        return float(data['market_cap'])
                    # Alternative: calculate from fdv if available
                    if 'fdv' in data:
                        return float(data['fdv'])
        except Exception:
            pass

        return None

    async def fetch_market_cap_from_dexscreener(self, ca: str) -> Optional[float]:
        """
        Fetch market cap from DexScreener API for a given contract address.

        Args:
            ca: Solana contract address

        Returns:
            Market cap in USD or None if not available
        """
        try:
            session = await self._get_http_session()
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'pairs' in data and len(data['pairs']) > 0:
                        # Get the first pair (usually the most liquid)
                        pair = data['pairs'][0]
                        if 'fdv' in pair:
                            return float(pair['fdv'])
                        if 'marketCap' in pair:
                            return float(pair['marketCap'])
        except Exception:
            pass

        return None

    async def fetch_market_cap(self, ca: str) -> Optional[float]:
        """
        Fetch market cap from pump.fun or DexScreener API.

        Tries pump.fun first, then falls back to DexScreener.

        Args:
            ca: Solana contract address

        Returns:
            Market cap in USD or None if not available
        """
        # Try pump.fun first
        market_cap = await self.fetch_market_cap_from_pumpfun(ca)
        if market_cap:
            return market_cap

        # Fallback to DexScreener
        market_cap = await self.fetch_market_cap_from_dexscreener(ca)
        if market_cap:
            return market_cap

        return None

    @staticmethod
    def format_market_cap(market_cap: float) -> str:
        """
        Format market cap in human-readable form.

        Args:
            market_cap: Market cap in USD

        Returns:
            Formatted string (e.g., "10.5K", "1.2M", "3.4B")
        """
        if market_cap >= 1_000_000_000:
            return f"${market_cap / 1_000_000_000:.1f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap / 1_000_000:.1f}M"
        elif market_cap >= 1_000:
            return f"${market_cap / 1_000:.1f}K"
        else:
            return f"${market_cap:.0f}"

    def extract_ca_from_url(self, text: str) -> Optional[str]:
        """
        Extract Solana CA from various URL types in message.

        Supports:
        - GeckoTerminal: https://www.geckoterminal.com/solana/tokens/CA
        - DexScreener: https://dexscreener.com/solana/CA
        - Pump.fun: https://pump.fun/CA
        - Solscan: https://solscan.io/token/CA

        Examples:
        - https://www.geckoterminal.com/solana/tokens/3uSuWER7XQnnBtU9AGCiRi1W5sYFUk8WmKj5AqyBZtd5
        - https://dexscreener.com/solana/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr
        - https://pump.fun/7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr

        Args:
            text: Message text containing URLs

        Returns:
            Solana CA extracted from URL or None
        """
        if not text:
            return None

        # Pattern for Solana CA in URLs (32-44 base58 chars)
        url_patterns = [
            # GeckoTerminal (check first - most common in @solearlytrending)
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

    def extract_solana_ca(self, text: str) -> Optional[str]:
        """
        Extract Solana contract address from message text or URLs.

        Tries to extract CA from text first using regex pattern,
        then falls back to extracting from DexScreener/Pump.fun URLs.

        Args:
            text: Message text to search

        Returns:
            First Solana CA found or None
        """
        if not text:
            return None

        # Try extracting from text first
        matches = self.SOLANA_CA_PATTERN.findall(text)
        if matches:
            # Return the first match (usually the CA)
            return matches[0]

        # Fallback: extract from URLs
        ca = self.extract_ca_from_url(text)
        if ca:
            return ca

        return None

    def generate_solana_links(self, ca: str) -> str:
        """
        Generate trading links for a Solana contract address.

        Args:
            ca: Solana contract address

        Returns:
            Formatted string with all trading links
        """
        return (
            f"[PUMP](https://pump.fun/{ca}) • "
            f"[DEX](https://dexscreener.com/solana/{ca}) • "
            f"[GT](https://www.geckoterminal.com/solana/tokens/{ca}) • "
            f"[SOL](https://solscan.io/token/{ca})"
        )

    def extract_token_info(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract token name and symbol from message text.

        Args:
            text: Message text to parse

        Returns:
            Tuple of (token_name, symbol)
        """
        token_name = None
        symbol = None

        # Try to find token name
        name_match = self.TOKEN_NAME_PATTERN.search(text)
        if name_match:
            token_name = name_match.group(1).strip()
        else:
            # Look for patterns like "Token: XYZ" or "Name: XYZ"
            lines = text.split('\n')
            for line in lines:
                if 'token' in line.lower() or 'name' in line.lower():
                    parts = line.split(':')
                    if len(parts) > 1:
                        potential_name = parts[-1].strip().strip('📌*').strip()
                        if 3 <= len(potential_name) <= 30:
                            token_name = potential_name
                            break

        # Try to find symbol/ticker
        symbol_match = self.TICKER_PATTERN.search(text)
        if symbol_match:
            symbol = symbol_match.group(1).strip().strip('#$').strip()
        else:
            # Look for hashtags like $TICKER or #TICKER
            hashtag_matches = self.TOKEN_SYMBOL_PATTERN.findall(text)
            if hashtag_matches:
                symbol = hashtag_matches[0]

        return token_name, symbol

    def strip_source_watermarks(self, text: str) -> str:
        """
        Strip source channel watermarks from message text.

        Args:
            text: Original message text

        Returns:
            Text with watermarks removed
        """
        if not self.strip_watermarks:
            return text

        cleaned_text = text
        for pattern in self.WATERMARK_PATTERNS:
            cleaned_text = pattern.sub('', cleaned_text)

        # Clean up any trailing whitespace
        cleaned_text = cleaned_text.strip()

        return cleaned_text

    def extract_signal_description(self, text: str) -> str:
        """
        Extract the main signal description from the message.

        Args:
            text: Message text

        Returns:
            Cleaned signal description
        """
        # Remove common headers
        lines = text.split('\n')
        signal_lines = []

        skip_patterns = ['🚨', 'NEW', 'CALL', '⦿', '─']

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip if it's just a header
            if any(pattern in line for pattern in skip_patterns):
                if len(line) < 20:  # Short lines are likely headers
                    continue

            # Skip lines that look like metadata
            if 'CA:' in line or 'Symbol:' in line or 'Token:' in line:
                continue

            signal_lines.append(line)

        # Join and limit length
        signal = '\n'.join(signal_lines[:5])  # Max 5 lines
        return signal[:200]  # Max 200 chars

    async def format_solana_message(self, original_text: str) -> str:
        """
        Format a Solana trading signal message with enhanced layout.

        Args:
            original_text: Original message text from source

        Returns:
            Formatted message with links and structure
        """
        # Extract information
        ca = self.extract_solana_ca(original_text)

        if not ca:
            # No CA found, return basic formatting
            return self._format_basic_message(original_text)

        token_name, symbol = self.extract_token_info(original_text)
        signal_desc = self.extract_signal_description(original_text)

        # Fetch market cap from API
        market_cap = None
        market_cap_formatted = "N/A"
        try:
            market_cap_value = await self.fetch_market_cap(ca)
            if market_cap_value:
                market_cap_formatted = self.format_market_cap(market_cap_value)
        except Exception:
            pass

        # Strip source watermarks
        clean_text = self.strip_source_watermarks(original_text)

        # Build formatted message
        formatted_parts = []

        # Header
        formatted_parts.append("🚨 NEW Fire Intern CALL ⦿")
        formatted_parts.append("─" * 35)
        formatted_parts.append("")

        # Signal section
        formatted_parts.append("📝 Signal:")

        if token_name:
            formatted_parts.append(f"Token Name: {token_name}")

        formatted_parts.append("")

        # Market Cap section
        formatted_parts.append("🏦 Market Cap:")
        formatted_parts.append(market_cap_formatted)
        formatted_parts.append("")

        # CA section - standalone code block for easy copying
        formatted_parts.append("📌 CA:")
        formatted_parts.append(f"`{ca}`")
        formatted_parts.append("")

        # Links section - inline with abbreviated labels
        formatted_parts.append("🔗 " + self.generate_solana_links(ca))
        formatted_parts.append("")

        # Warning
        formatted_parts.append("⚠️ Trade Responsibly")

        # Timestamp
        utc_time = datetime.now(timezone.utc).strftime("%H:%M:%S")
        formatted_parts.append(f"⏰ {utc_time} UTC")

        # Divider
        formatted_parts.append("━" * 30)

        # Custom watermark
        formatted_parts.append(self.custom_watermark)

        return '\n'.join(formatted_parts)

    def _format_basic_message(self, original_text: str) -> str:
        """
        Format a message without CA - forward as-is with watermark only.

        Args:
            original_text: Original message text

        Returns:
            Original text with watermark appended
        """
        # Strip source watermarks first
        clean_text = self.strip_source_watermarks(original_text)

        # Add custom watermark if configured
        if self.custom_watermark:
            return f"{clean_text}\n\n{'━' * 30}\n{self.custom_watermark}"

        return clean_text

    def should_format(self, source_channel: str, enabled_channels: List[str]) -> bool:
        """
        Check if a source channel should use enhanced formatting.

        Args:
            source_channel: Channel username or ID
            enabled_channels: List of channels to apply formatting to

        Returns:
            True if formatting should be applied
        """
        source_normalized = source_channel.lower().lstrip('@')
        enabled_normalized = [ch.lower().lstrip('@') for ch in enabled_channels]

        return source_normalized in enabled_normalized


# Global formatter instance (will be initialized with config)
_formatter: Optional[EnhancedFormatter] = None


def get_formatter() -> Optional[EnhancedFormatter]:
    """Get the global formatter instance."""
    return _formatter


def init_formatter(
    custom_watermark: str = "📡 via Fire intern",
    strip_watermarks: bool = True
) -> EnhancedFormatter:
    """
    Initialize the global formatter instance.

    Args:
        custom_watermark: Custom watermark text
        strip_watermarks: Whether to strip source watermarks

    Returns:
        Initialized formatter instance
    """
    global _formatter
    _formatter = EnhancedFormatter(
        custom_watermark=custom_watermark,
        strip_watermarks=strip_watermarks
    )
    return _formatter
