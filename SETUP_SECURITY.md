# 🔐 Quick Security Setup Guide

## 1️⃣ Verify Your Repository is Safe (30 seconds)

```bash
# Run the security verification script
python verify-gitignore.py
```

This will check:
- ✅ .gitignore exists and has required patterns
- ✅ .env is ignored (if it exists)
- ✅ *.session files are ignored
- ✅ No obvious secrets in source code

## 2️⃣ Install Pre-commit Hook (1 minute)

Protect yourself from accidental commits:

```bash
# Install the pre-commit hook
cp pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Now git will automatically check before every commit!

## 3️⃣ Verify gitignore is Working

```bash
# Check if .env is properly ignored
git check-ignore .env

# Should print: .env

# Check if session files are ignored
git check-ignore test.session

# Should print: test.session
```

If nothing prints, the file is NOT ignored! ⚠️

## 4️⃣ What's Safe to Commit

```bash
# These files are SAFE:
git add .env.example
git add requirements.txt
git add *.py
git add README.md
git add .gitignore
git add SECURITY.md

# These are DANGEROUS - never commit:
# .env                    ❌ DANGEROUS
# *.session               ❌ DANGEROUS
# *.session-journal       ❌ DANGEROUS
# forwarded_messages.txt  ❌ Not needed in git
```

## 5️⃣ Before Every Commit

```bash
# Check what you're about to commit
git status

# Review the actual changes
git diff

# Review staged changes
git diff --staged

# Run security check
python verify-gitignore.py
```

## 🚨 If You Accidentally Committed Secrets

### Emergency Steps (do immediately):

```bash
# 1. Remove file from git tracking (keep local file)
git rm --cached .env

# 2. Add to .gitignore
echo ".env" >> .gitignore

# 3. Commit the removal
git commit -m "Remove sensitive files from tracking"

# 4. Force push to overwrite history
git push --force

# 5. Revoke credentials IMMEDIATELY
# Visit: https://my.telegram.org/apps
# Delete or regenerate your application
```

### If Credentials Were Already Pushed:

1. **REVOKE CREDENTIALS IMMEDIATELY** at https://my.telegram.org/apps
2. Delete all session files: `rm *.session`
3. Generate new API credentials
4. Update .env with new credentials
5. Consider the repository compromised - start fresh if needed

## 📋 Security Checklist

### Before First Commit
- [ ] Ran `python verify-gitignore.py` - all checks passed
- [ ] Verified `git check-ignore .env` prints ".env"
- [ ] Verified `git check-ignore test.session` prints "test.session"
- [ ] Installed pre-commit hook
- [ ] Reviewed `git status` - no sensitive files shown

### Before Every Push
- [ ] Reviewed `git diff` for secrets
- [ ] Confirmed .env is not tracked
- [ ] Confirmed *.session files are not tracked
- [ ] No API_HASH in code (only in .env)
- [ ] Commit messages don't contain credentials

## 🔐 Security Best Practices

### DO ✅
- Use environment variables for credentials
- Keep .env file local (never commit)
- Use .gitignore properly
- Review all changes before committing
- Use different credentials for dev/prod
- Rotate credentials periodically

### DON'T ❌
- Hardcode credentials in source code
- Commit .env file
- Commit *.session files
- Share credentials via email/chat
- Use same credentials everywhere
- Forget to revoke old credentials

## 📞 Need Help?

- See SECURITY.md for detailed security guidelines
- Run `python verify-gitignore.py` anytime you're unsure
- Check .gitignore if files aren't being ignored
- Review commit history for accidental secrets

---

**Remember: Once secrets are on GitHub, they're potentially there forever!**
**Always verify before committing!**
