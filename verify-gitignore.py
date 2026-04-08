#!/usr/bin/env python3
"""
Git Security Verification Script

Run this script to verify that your git repository is properly configured
to prevent accidental commits of sensitive files.

Usage:
    python verify-gitignore.py
"""

import os
import sys
from pathlib import Path


class GitSecurityChecker:
    """Verify git repository security configuration."""

    def __init__(self) -> None:
        """Initialize the security checker."""
        self.repo_root = Path.cwd()
        self.gitignore_path = self.repo_root / '.gitignore'
        self.env_file = self.repo_root / '.env'
        self.session_files = list(self.repo_root.glob('*.session'))

        self.issues = []
        self.warnings = []
        self.passed = []

    def check_gitignore_exists(self) -> bool:
        """Check if .gitignore exists."""
        if not self.gitignore_path.exists():
            self.issues.append("❌ .gitignore file does not exist!")
            return False
        self.passed.append("✅ .gitignore file exists")
        return True

    def check_gitignore_contents(self) -> bool:
        """Check if .gitignore contains essential patterns."""
        if not self.gitignore_path.exists():
            return False

        required_patterns = [
            '.env',
            '*.session',
            '*.session-journal',
            'forwarded_messages.txt',
            'logs/',
        ]

        with open(self.gitignore_path, 'r') as f:
            gitignore_content = f.read()

        missing = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing.append(pattern)

        if missing:
            self.issues.append(f"❌ .gitignore missing patterns: {', '.join(missing)}")
            return False

        self.passed.append("✅ .gitignore contains all required patterns")
        return True

    def check_env_file_ignored(self) -> bool:
        """Check if .env file is properly ignored."""
        if not self.env_file.exists():
            self.warnings.append("⚠️  .env file does not exist (this is OK if you haven't created it yet)")
            return True

        # Check if .env is ignored by git
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'check-ignore', '.env'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.passed.append("✅ .env is properly ignored by git")
                return True
            else:
                self.issues.append("❌ .env exists but is NOT ignored by git!")
                return False

        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.warnings.append("⚠️  Could not verify git ignore status (git not available?)")
            return True

    def check_session_files_ignored(self) -> bool:
        """Check if session files are properly ignored."""
        if not self.session_files:
            self.warnings.append("⚠️  No session files found (this is OK if you haven't logged in yet)")
            return True

        all_ignored = True
        for session_file in self.session_files:
            import subprocess
            try:
                result = subprocess.run(
                    ['git', 'check-ignore', str(session_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode != 0:
                    self.issues.append(f"❌ {session_file.name} exists but is NOT ignored by git!")
                    all_ignored = False

            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.warnings.append(f"⚠️  Could not verify ignore status for {session_file.name}")
                all_ignored = False

        if all_ignored and self.session_files:
            self.passed.append(f"✅ All session files ({len(self.session_files)}) are properly ignored")

        return all_ignored

    def check_env_example_exists(self) -> bool:
        """Check if .env.example exists."""
        env_example = self.repo_root / '.env.example'
        if not env_example.exists():
            self.warnings.append("⚠️  .env.example does not exist (recommended to include)")
            return False

        self.passed.append("✅ .env.example exists")
        return True

    def check_for_secrets_in_code(self) -> bool:
        """Check for potential secrets in Python files."""
        secret_patterns = [
            ('API_HASH', 'api_hash'),
            ('API_KEY', 'api_key'),
            ('SECRET', 'secret'),
            ('PASSWORD', 'password'),
        ]

        found_secrets = False
        for py_file in self.repo_root.glob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines[:50], 1):  # Check first 50 lines
                    for pattern_name, pattern in secret_patterns:
                        # Skip comments
                        if line.strip().startswith('#'):
                            continue

                        # Look for suspicious patterns
                        if pattern in line.lower():
                            # Skip if it's getting from os.getenv
                            if 'os.getenv' in line or 'os.environ' in line:
                                continue

                            # Skip if it's a placeholder
                            if 'your_' in line or 'placeholder' in line.lower():
                                continue

                            # Skip if it's just a variable name
                            if '=' not in line:
                                continue

                            self.warnings.append(f"⚠️  {py_file.name}:{i} - Potential secret: {line.strip()[:60]}")
                            found_secrets = True

            except (UnicodeDecodeError, IOError):
                pass

        if not found_secrets:
            self.passed.append("✅ No obvious secrets found in Python files")

        return not found_secrets

    def run_all_checks(self) -> bool:
        """Run all security checks."""
        print("=" * 70)
        print("🔍 GIT SECURITY VERIFICATION")
        print("=" * 70)
        print()

        self.check_gitignore_exists()
        self.check_gitignore_contents()
        self.check_env_file_ignored()
        self.check_session_files_ignored()
        self.check_env_example_exists()
        self.check_for_secrets_in_code()

        # Print results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        if self.passed:
            print("\n✅ PASSED:")
            for item in self.passed:
                print(f"  {item}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"  {item}")

        if self.issues:
            print("\n❌ ISSUES FOUND:")
            for item in self.issues:
                print(f"  {item}")

        print("\n" + "=" * 70)

        if self.issues:
            print("🚨 SECURITY ISSUES DETECTED!")
            print("\nPlease fix the issues above before committing to git.")
            print("See SECURITY.md for guidance.")
            return False
        else:
            print("✅ ALL CHECKS PASSED!")
            print("\nYour repository appears to be properly configured.")
            print("Remember to always review changes before committing.")
            return True


def main() -> int:
    """Main entry point."""
    print()

    checker = GitSecurityChecker()
    success = checker.run_all_checks()

    print()

    if not success:
        print("\n💡 TIPS:")
        print("  - Add sensitive files to .gitignore")
        print("  - Run: git rm --cached <file> to untrack files")
        print("  - Never commit .env, *.session, or credentials")
        print("  - See SECURITY.md for more information")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
