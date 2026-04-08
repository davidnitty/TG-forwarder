# 🔐 Security Guidelines

## ⚠️ NEVER Commit These Files to GitHub

### Sensitive Files (Protected by .gitignore)
- `.env` - Contains API credentials and personal configuration
- `*.session` - Telegram session files (authentication keys)
- `*.session-journal` - Telegram session journal files
- `forwarded_messages.txt` - Internal cache data

### Why These Files Are Dangerous

1. **`.env` file contains:**
   - `API_ID` - Your Telegram API identifier
   - `API_HASH` - **SECRET** authentication key
   - `DESTINATION_GROUP` - Your private group ID
   - Session configuration

2. **Session files (`*.session`) contain:**
   - Authentication keys equivalent to your password
   - Can be used to impersonate your Telegram account
   - Valid indefinitely until revoked

3. **Consequences of leaking credentials:**
   - ❌ Unauthorized access to your Telegram account
   - ❌ Someone can impersonate you
   - ❌ Forward messages to any group they want
   - ❌ Access your private conversations
   - ❌ Potential account suspension by Telegram

## ✅ SAFE to Commit

These files contain no secrets and are safe for public repositories:

- `.env.example` - Template with placeholders only
- `requirements.txt` - Python dependencies
- `*.py` files - All Python source code (no hardcoded secrets)
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Docker orchestration
- `README.md` - Documentation
- `QUICKSTART.md` - Setup guide
- `VPS_DEPLOYMENT.md` - Deployment guide
- `.gitignore` - Protects sensitive files

## 🔒 Security Best Practices

### 1. Before Every Commit
```bash
# Check what you're about to commit
git status

# Review the actual changes
git diff

# Review staged changes
git diff --staged
```

### 2. Verify .gitignore is Working
```bash
# Check if .env is properly ignored
git check-ignore .env

# Should print: .env

# If nothing prints, .env is NOT ignored!
```

### 3. After Accidental Commit (Emergency Steps)
```bash
# If you accidentally committed sensitive files:

# 1. Remove the file from git tracking
git rm --cached .env

# 2. Add to .gitignore (if not already)
echo ".env" >> .gitignore

# 3. Commit the removal
git commit -m "Remove sensitive files"

# 4. Force push to overwrite history (DANGEROUS!)
git push --force

# 5. Revoke your API credentials:
#    - Go to https://my.telegram.org/apps
#    - Delete or regenerate your application
#    - Update .env with new credentials
```

### 4. Check git History for Secrets
```bash
# Search for API_HASH in git history
git log --all --full-history --source -- "*env*"

# Search for session files
git log --all --full-history --source -- "*.session"

# If found, consider repository compromised and:
# 1. Revoke all API credentials immediately
# 2. Delete Telegram sessions (stop using them)
# 3. Consider repository burned - create new one
```

## 🛡️ Preventive Measures

### Automated Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook to prevent accidental commits of sensitive files

echo "🔍 Checking for sensitive files..."

# Forbidden files
FORBIDDEN_FILES=(
    ".env"
    "*.session"
    "*.session-journal"
    "forwarded_messages.txt"
)

# Check if any forbidden files are staged
for pattern in "${FORBIDDEN_FILES[@]}"; do
    if git diff --cached --name-only | grep -E "$pattern"; then
        echo "❌ ERROR: Attempting to commit sensitive file: $pattern"
        echo "Please remove it from staging:"
        echo "  git reset HEAD <file>"
        exit 1
    fi
done

# Check for API_HASH in staged files
if git diff --cached | grep -E "^\+.*API_HASH\s*=" | grep -v "API_HASH=your_api_hash"; then
    echo "❌ ERROR: API_HASH found in staged changes!"
    echo "Please remove it before committing."
    exit 1
fi

echo "✅ Pre-commit check passed"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Using git-secrets Tool (Recommended)

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or
sudo apt install git-secrets  # Linux

# Configure for this repository
cd telegram-forwarder
git secrets --install
git secrets --register-aws

# Add patterns to scan for
git secrets --add 'API_HASH\s*=\s*[a-zA-Z0-9]+'
git secrets --add 'api_hash\s*=\s*[a-zA-Z0-9]+'

# Scan entire repository
git secrets --scan

# Scan before each commit (automated)
git secrets --install -f
```

## 📋 Security Checklist

### Before First Commit
- [ ] Reviewed .gitignore - ensures .env, *.session are ignored
- [ ] Verified no credentials in source code
- [ ] Tested `git check-ignore .env` - prints ".env"
- [ ] Tested `git check-ignore test.session` - prints "test.session"
- [ ] Ran `git status` - no sensitive files shown
- [ ] Considered setting up pre-commit hooks

### Before Every Push
- [ ] Reviewed `git diff` for secrets
- [ ] Confirmed .env is not tracked
- [ ] Confirmed *.session files are not tracked
- [ ] No hardcoded API_HASH in code
- [ ] No sensitive data in commit messages

### If You Accidentally Pushed Secrets
1. **IMMEDIATELY** revoke API credentials at https://my.telegram.org/apps
2. Delete/revoke Telegram sessions
3. Remove sensitive files from repository
4. Force push to overwrite git history
5. Consider the repository compromised - start fresh if needed

## 🚨 Incident Response

### What to Do If Credentials Are Leaked

1. **Immediate Actions (Within Minutes)**
   ```bash
   # Revoke API credentials
   # Visit: https://my.telegram.org/apps
   # Delete the application or regenerate keys

   # Stop using old session files
   rm *.session *.session-journal

   # Generate new credentials
   # Update .env with new API_ID and API_HASH
   ```

2. **Within Hours**
   - Change Telegram password
   - Enable 2-factor authentication
   - Review active Telegram sessions
   - Check for unauthorized account activity

3. **Within Days**
   - Audit all repositories for leaked credentials
   - Rotate all other passwords/keys
   - Set up git-secrets or pre-commit hooks
   - Educate team members on security

## 🔐 Additional Security Tips

### Environment Variables
- Never hardcode credentials in source code
- Always use environment variables
- Use different credentials for dev/prod
- Rotate credentials periodically

### Session Files
- Treat session files like passwords
- Never share session files
- Delete old session files when no longer needed
- Use different session names for different bots

### Git Best Practices
- Use `.gitignore` properly
- Review all changes before committing
- Use pull requests for code review
- Enable branch protection rules
- Use private repositories for sensitive projects

### VPS Security
- Use SSH keys instead of passwords
- Disable password authentication
- Use firewall (ufw)
- Keep system updated
- Monitor logs regularly

## 📞 Resources

- Telegram Security: https://telegram.org/privacy
- Git Secrets: https://github.com/awslabs/git-secrets
- Git Security: https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage

---

**Remember: Once credentials are on GitHub, they're potentially there forever, even if you delete them! Always verify before committing.**
