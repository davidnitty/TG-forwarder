# Quick Start Guide

Get your Telegram forwarder bot running in 5 minutes!

## Step 1: Get Telegram API Credentials (2 minutes)

1. Go to **https://my.telegram.org/apps**
2. Login with your phone number
3. Click "Create new application"
4. Fill in the form:
   - App title: `Forwarder Bot`
   - Short name: `forwarder`
   - Platform: `Desktop`
   - Description: `Personal forwarding bot`
5. Click **Create application**
6. Copy `api_id` and `api_hash`

## Step 2: Get Your Destination Group ID (1 minute)

1. Add **@getidsbot** to your private group
2. Send command: `/groupid`
3. Copy the number (e.g., `-1001234567890`)
4. You can remove the bot afterward

## Step 3: Configure the Bot (1 minute)

1. Copy the example config:
```bash
cp .env.example .env
```

2. Edit `.env` with your values:
```bash
nano .env  # or use any text editor
```

3. Fill in the required fields:
```env
API_ID=12345678                           # From step 1
API_HASH=abcdef123456...                  # From step 1
SOURCE_CHANNEL=solearlytrending           # Channel to monitor
DESTINATION_GROUP=-1001234567890          # From step 2
WATERMARK=📡 via MyChannel                # Optional: change or remove
```

## Step 4: First Login (1 minute)

1. Run the login script:
```bash
python login.py
```

2. Enter your phone number with country code:
```
+1234567890
```

3. Enter the verification code sent to Telegram:
```
12345
```

4. If you have 2FA enabled, enter your password

✅ Session file created! You're now authenticated.

## Step 5: Start the Bot!

```bash
python main.py
```

You should see:
```
[INFO] 2026-04-08 00:00:00 - Starting Telegram forwarder bot...
[INFO] 2026-04-08 00:00:01 - Connected to Telegram servers
[INFO] 2026-04-08 00:00:01 - Authorized as: YourName (@username)
[INFO] 2026-04-08 00:00:02 - Source channel: Solearly Trending
[INFO] 2026-04-08 00:00:02 - Destination group: My Private Group
[SUCCESS] 2026-04-08 00:00:02 - Bot is running and monitoring for messages...
[INFO] 2026-04-08 00:00:02 - Press Ctrl+C to stop
```

## Step 6: Test It!

1. Post a message in your source channel
2. Check your destination group
3. The message should appear there!

## Common Issues

### "Not authorized! Please run: python login.py"
- Solution: Run `python login.py` first

### "Cannot access source channel"
- Solution: Make sure your account follows/joined the public channel

### "Cannot access destination group"
- Solution: Make sure you're a member of the destination group
- Add the bot's account to the group as an admin

### Messages not appearing
- Check the bot has permission to post in the destination group
- Make the bot an admin in the destination group

### Where do I find my source channel username?
- Open the channel in Telegram
- Look at the link: `t.me/username`
- Use the `username` part (without @)

## Running 24/7

### On your computer:
```bash
# Windows
python main.py
# Keep the window open

# Linux/Mac
screen -S forwarder
python main.py
# Press Ctrl+A, then D to detach
```

### On a VPS:
See [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md) for detailed instructions.

## Checking Status

```bash
python status.py
```

Output:
```
==================================================
TELEGRAM FORWARDER BOT STATUS
==================================================
Connected: Yes
User: YourName
Source Channel: solearlytrending
Destination Group: -1001234567890
Messages Forwarded: 42
Watermark: Enabled
==================================================
```

## Stopping the Bot

Press `Ctrl+C` in the terminal

## Next Steps

- Read [README.md](README.md) for full documentation
- Configure watermark in `.env` (optional)
- Set up 24/7 deployment on VPS (see VPS_DEPLOYMENT.md)
- Monitor logs: `tail -f forwarder.log`

## Need Help?

1. Check the logs: `tail -f forwarder.log`
2. Run status check: `python status.py`
3. Review configuration: `cat .env`
4. Make sure you have the latest version: `pip install -r requirements.txt --upgrade`

---

**🎉 Congratulations! Your bot is now running!**

The bot will automatically:
- Forward all new messages from the source channel
- Forward edited message updates
- Skip duplicate messages
- Add watermark to text-only messages
- Handle errors gracefully
- Keep running 24/7

Messages will appear in real-time as they're posted in the source channel.
