#!/bin/bash
# ============================================================
# Git Pre-commit Hook - Prevents Sensitive File Commits
# ============================================================
# Installation:
#   cp pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# This hook prevents accidental commits of:
# - .env files
# - *.session files
# - forwarded_messages.txt
# - Files containing API_HASH
# ============================================================

echo "🔍 Running pre-commit security checks..."

# Set exit on error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if we found any issues
FOUND_ISSUES=0

# ============================================================
# Check 1: Forbidden file patterns
# ============================================================
echo "Checking for forbidden file patterns..."

FORBIDDEN_PATTERNS=(
    ".env$"
    "\.session$"
    "\.session-journal$"
    "forwarded_messages\.txt$"
)

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -n "$STAGED_FILES" ]; then
    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
        MATCHING_FILES=$(echo "$STAGED_FILES" | grep -E "$pattern" || true)

        if [ -n "$MATCHING_FILES" ]; then
            echo -e "${RED}❌ ERROR: Attempting to commit forbidden files matching: $pattern${NC}"
            echo "Files found:"
            echo "$MATCHING_FILES"
            echo ""
            echo "Please unstage these files:"
            echo "  git reset HEAD <file>"
            FOUND_ISSUES=1
        fi
    done
fi

# ============================================================
# Check 2: Check for API_HASH in staged changes
# ============================================================
echo "Checking for API_HASH in staged changes..."

# Look for API_HASH additions (lines starting with +)
API_HASH_FOUND=$(git diff --cached | grep -E "^\+.*API_HASH\s*=" | grep -v "API_HASH=your_api_hash" | grep -v "API_HASH=.*\.\.\." || true)

if [ -n "$API_HASH_FOUND" ]; then
    echo -e "${RED}❌ ERROR: API_HASH found in staged changes!${NC}"
    echo "This looks like a real API hash, not a placeholder."
    echo ""
    echo "Found:"
    echo "$API_HASH_FOUND"
    echo ""
    echo "Please remove it before committing."
    FOUND_ISSUES=1
fi

# ============================================================
# Check 3: Check for other potential secrets
# ============================================================
echo "Checking for other potential secrets..."

SECRET_PATTERNS=(
    "api_key\s*=\s*[\"']?[a-zA-Z0-9]{20,}"
    "secret_key\s*=\s*[\"']?[a-zA-Z0-9]{20,}"
    "password\s*=\s*[\"']?[a-zA-Z0-9]{8,}"
    "token\s*=\s*[\"']?[a-zA-Z0-9]{20,}"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    SECRETS_FOUND=$(git diff --cached | grep -iE "^\+.*$pattern" || true)

    if [ -n "$SECRETS_FOUND" ]; then
        echo -e "${YELLOW}⚠️  WARNING: Potential secret found matching pattern: $pattern${NC}"
        echo "Please verify this is not a real credential."
        echo "Found:"
        echo "$SECRETS_FOUND"
        echo ""
        # Don't fail for this, just warn
    fi
done

# ============================================================
# Final result
# ============================================================
if [ $FOUND_ISSUES -eq 1 ]; then
    echo ""
    echo -e "${RED}❌ Pre-commit hook failed!${NC}"
    echo "Please fix the issues above before committing."
    echo ""
    echo "For help, see SECURITY.md"
    exit 1
else
    echo -e "${GREEN}✅ Pre-commit security checks passed!${NC}"
    exit 0
fi
