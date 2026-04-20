"""
Message Filtering Module

Provides keyword filtering, blocklist, and regex pattern matching for
detecting cryptocurrency addresses and other content.
"""

import re
import os
from typing import List, Optional, Pattern
from config import get_config


class MessageFilters:
    """
    Message filtering system for the Telegram forwarder.

    Supports:
    - Keyword whitelist (only forward if contains these)
    - Keyword blocklist (skip if contains these)
    - Regex pattern matching (CA addresses, etc.)
    """

    # Solana address pattern (32-44 characters, base58)
    SOLANA_CA_PATTERN = re.compile(
        r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
    )

    # Ethereum/BSC address pattern (0x followed by 40 hex chars)
    ETH_ADDRESS_PATTERN = re.compile(
        r'\b0x[a-fA-F0-9]{40}\b'
    )

    # Other common CA patterns (can be extended)
    HEX_PATTERN = re.compile(
        r'\b[a-fA-F0-9]{32,}\b'
    )

    def __init__(self) -> None:
        """Initialize filters from configuration."""
        config = get_config()

        # Load filter settings from environment
        self.enabled: bool = os.getenv('ENABLE_FILTERS', 'false').lower() == 'true'
        self.keywords: List[str] = self._parse_list(os.getenv('FILTER_KEYWORDS', ''))
        self.blocklist: List[str] = self._parse_list(os.getenv('FILTER_BLOCKLIST', ''))
        self.detect_ca: bool = os.getenv('DETECT_CRYPTO_ADDRESSES', 'false').lower() == 'true'
        self.require_ca: bool = os.getenv('REQUIRE_CRYPTO_ADDRESS', 'false').lower() == 'true'

        # Track statistics
        self.stats = {
            'total_checked': 0,
            'allowed': 0,
            'blocked': 0,
            'blocked_by_keywords': 0,
            'blocked_by_blocklist': 0,
            'blocked_by_ca_requirement': 0,
            'blocked_by_milestone': 0,
            'blocked_by_paid_alerts': 0,
        }

    @staticmethod
    def _parse_list(env_value: str) -> List[str]:
        """
        Parse comma-separated list from environment variable.

        Args:
            env_value: Comma-separated string

        Returns:
            List of trimmed strings
        """
        if not env_value:
            return []
        return [item.strip().lower() for item in env_value.split(',') if item.strip()]

    def is_top_trending_update(self, text: str) -> bool:
        """
        Detect if message is a 'Top Early Trending' leaderboard update.
        Return True if it should be SKIPPED (not forwarded).

        Args:
            text: Message text to check

        Returns:
            True if message is a leaderboard update that should be skipped
        """
        if not text:
            return False

        # Key indicators of leaderboard updates
        skip_patterns = [
            r'🏆.*Top Early Trending',           # Header with trophy emoji
            r'🥇.*\d+X',                          # Gold medal + multiplier
            r'🥈.*\d+X',                          # Silver medal + multiplier
            r'🥉.*\d+X',                          # Bronze medal + multiplier
            r'BUY TRENDING 🚀',                   # Button text
            r'ⓓ.*ⓔ.*ⓐ.*ⓛ.*ⓔ.*ⓡ.*ⓣ.*ⓡ.*ⓔ.*ⓝ.*ⓖ.*ⓘ.*ⓝ.*ⓖ',  # Circled text variant
        ]

        # Check for multiple indicators (more reliable)
        matches = sum(1 for pattern in skip_patterns if re.search(pattern, text, re.IGNORECASE))

        # Skip if 2+ indicators found (reduces false positives)
        return matches >= 2

    def is_milestone_alert(self, text: str) -> bool:
        """
        Detect if message is a milestone/multiplier price alert.
        Return True if it should be SKIPPED (not forwarded).

        Blocks messages like:
        - "Coin reached 2x from entry!"
        - "5x milestone hit!"
        - "Token has done 10x from call price"

        Args:
            text: Message text to check

        Returns:
            True if message is a milestone alert that should be skipped
        """
        if not text:
            return False

        # Patterns indicating milestone/multiplier alerts
        milestone_patterns = [
            # Multiplier + milestone language
            r'\b\d+x\s+(from|since|reached|hit|milestone|alert)',
            r'(reached|hit)\s+\d+x',
            r'(milestone|alert)\s*:.*\d+x',
            r'\d+x\s+(milestone|alert)',

            # Entry/call price references with multiples
            r'(from|since)\s+(entry|call|launch|ipo)',
            r'(entry|call|launch)\s+price.*\d+x',

            # Common milestone phrases
            r'we\s+(hit|reached)\s+\d+x',
            r'has\s+(hit|reached|done)\s+\d+x',
            r'token\s+(hit|reached|done)\s+\d+x',

            # Specific milestone numbers with context
            r'(hit|reached)\s+(2x|3x|4x|5x|10x|20x|50x|100x)',
        ]

        text_lower = text.lower()

        # Check if any milestone pattern matches
        for pattern in milestone_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def is_dexscreener_paid_alert(self, text: str) -> bool:
        """
        Detect if message is a DexScreener PAID/payment alert.
        Return True if it should be SKIPPED (not forwarded).

        Blocks messages like:
        - "PAID: Profile payment approved"
        - "DexScreener payment received"
        - "Profile boost activated - PAID"

        Args:
            text: Message text to check

        Returns:
            True if message is a DexScreener paid alert that should be skipped
        """
        if not text:
            return False

        # Patterns indicating DexScreener PAID alerts
        paid_patterns = [
            # DexScreener specific payment language
            r'dexscreener.*\b(paid|payment|boost|profile|approval)\b',
            r'\b(paid|payment).*dexscreener',
            r'profile.*payment.*approved',

            # Common PAID alert formats
            r'🔔\s*PAID\s*🔔',
            r'\[PAID\]',
            r'⚡\s*PAID\s*⚡',
            r'payment\s+(approved|received|confirmed|completed)',
            r'profile\s+(boost|promotion|upgrade)\s+(paid|active|activated)',

            # Payment confirmation phrases
            r'thanks\s+for\s+(the\s+)?payment',
            r'payment\s+success',
            r'transaction\s+(confirmed|complete)',
        ]

        text_lower = text.lower()

        # Check if any paid alert pattern matches
        for pattern in paid_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def check_keywords(self, text: str) -> bool:
        """
        Check if text contains any required keywords.

        Args:
            text: Message text to check

        Returns:
            True if keywords are satisfied (either no keywords set, or text contains one)
        """
        if not self.keywords:
            # No keywords configured = allow all
            return True

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

    def check_blocklist(self, text: str) -> bool:
        """
        Check if text contains blocked words.

        Args:
            text: Message text to check

        Returns:
            True if text is allowed (not blocked), False if blocked
        """
        if not self.blocklist:
            # No blocklist configured = allow all
            return True

        text_lower = text.lower()
        is_blocked = any(blocked in text_lower for blocked in self.blocklist)

        if is_blocked:
            self.stats['blocked_by_blocklist'] += 1

        return not is_blocked

    def detect_crypto_addresses(self, text: str) -> dict:
        """
        Detect cryptocurrency addresses in text.

        Args:
            text: Message text to scan

        Returns:
            Dictionary with detected addresses by type
        """
        results = {
            'solana': self.SOLANA_CA_PATTERN.findall(text),
            'ethereum': self.ETH_ADDRESS_PATTERN.findall(text),
            'hex': self.HEX_PATTERN.findall(text),
            'has_ca': False
        }

        results['has_ca'] = bool(
            results['solana'] or
            results['ethereum'] or
            results['hex']
        )

        return results

    def should_forward(self, text: Optional[str]) -> tuple:
        """
        Determine if a message should be forwarded based on filters.

        Args:
            text: Message text (can be None for media-only messages)

        Returns:
            Tuple of (should_forward: bool, reason: str)
        """
        self.stats['total_checked'] += 1

        # Handle None or empty text
        if not text:
            if self.require_ca:
                # Media-only message without CA requirement
                self.stats['blocked_by_ca_requirement'] += 1
                return False, "No text and CA required"
            return True, "No text to filter"

        # Skip Top Early Trending leaderboard updates
        if self.is_top_trending_update(text):
            self.stats['blocked'] += 1
            return False, "Top Early Trending leaderboard update"

        # Skip milestone/multiplier alerts
        if self.is_milestone_alert(text):
            self.stats['blocked'] += 1
            self.stats['blocked_by_milestone'] += 1
            return False, "Milestone/multiplier alert"

        # Skip DexScreener PAID/payment alerts
        if self.is_dexscreener_paid_alert(text):
            self.stats['blocked'] += 1
            self.stats['blocked_by_paid_alerts'] += 1
            return False, "DexScreener paid alert"

        # Check blocklist first
        if not self.check_blocklist(text):
            self.stats['blocked'] += 1
            return False, f"Blocked by blocklist"

        # Check keyword whitelist
        if self.keywords and not self.check_keywords(text):
            self.stats['blocked_by_keywords'] += 1
            self.stats['blocked'] += 1
            return False, "Missing required keywords"

        # Check for crypto addresses if required
        if self.require_ca:
            ca_detected = self.detect_crypto_addresses(text)
            if not ca_detected['has_ca']:
                self.stats['blocked_by_ca_requirement'] += 1
                self.stats['blocked'] += 1
                return False, "No crypto address detected"

        # Passed all filters
        self.stats['allowed'] += 1
        return True, "Passed all filters"

    def get_stats(self) -> dict:
        """Get filtering statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset filtering statistics."""
        self.stats = {
            'total_checked': 0,
            'allowed': 0,
            'blocked': 0,
            'blocked_by_keywords': 0,
            'blocked_by_blocklist': 0,
            'blocked_by_ca_requirement': 0,
            'blocked_by_milestone': 0,
            'blocked_by_paid_alerts': 0,
        }


# Global filter instance
filters = MessageFilters()


def should_forward_message(text: str, skip_trending: bool = True, skip_milestones: bool = True, skip_paid: bool = True) -> bool:
    """
    Standalone filter function to check if a message should be forwarded.
    This is a convenience function for direct use in event handlers.

    Args:
        text: Message text to check
        skip_trending: Whether to skip trending updates (default: true,
                      can be overridden via SKIP_TRENDING_UPDATES env var)
        skip_milestones: Whether to skip milestone/multiplier alerts (default: true)
        skip_paid: Whether to skip DexScreener paid alerts (default: true)

    Returns:
        True if message should be forwarded, False if it should be skipped
    """
    if not text:
        return True  # Forward media-only messages

    # Check environment variable for skip_trending setting
    # Can be overridden by function parameter
    env_skip_trending = os.getenv('SKIP_TRENDING_UPDATES', 'true').lower() == 'true'
    should_skip = skip_trending and env_skip_trending

    # Skip Top Early Trending updates if enabled
    if should_skip and filters.is_top_trending_update(text):
        return False

    # Skip milestone/multiplier alerts if enabled
    env_skip_milestones = os.getenv('SKIP_MILESTONE_ALERTS', 'true').lower() == 'true'
    should_skip_milestones = skip_milestones and env_skip_milestones

    if should_skip_milestones and filters.is_milestone_alert(text):
        return False

    # Skip DexScreener PAID/payment alerts if enabled
    env_skip_paid = os.getenv('SKIP_PAID_ALERTS', 'true').lower() == 'true'
    should_skip_paid = skip_paid and env_skip_paid

    if should_skip_paid and filters.is_dexscreener_paid_alert(text):
        return False

    # Add more filters here in future (spam, scams, etc.)
    return True


def get_filters() -> MessageFilters:
    """Get the global filters instance."""
    return filters
