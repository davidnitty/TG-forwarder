# Telegram Forwarder Bot

A robust Telegram bot that forwards all messages from a public channel to a private group using Telethon (MTProto).

## Features

- Forward all message types (text, photos, videos, documents, links)
- Optional watermark/branding on forwarded messages
- Duplicate prevention using message ID tracking
- Automatic reconnection on connection errors
- Comprehensive logging with timestamps
- 24/7 operation ready

## Prerequisites

- Python 3.8 or higher
- Telegram account
- API credentials from [https://my.telegram.org/apps](https://my.telegram.org/apps)
- Source channel username or ID
- Destination group ID

## Installation

1. Clone or download this project:
```bash
cd telegram-forwarder
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Get API credentials:
   - Go to [https://my.telegram.org/apps](https://my.telegram.org/apps)
   - Login with your phone number
   - Create a new application
   - Copy `api_id` and `api_hash`

2. Get your destination group ID:
   - Add @getidsbot to your group
   - Use `/groupid` command to get the ID (e.g., -1001234567890)

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Edit `.env` with your credentials:
```env
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_NAME=forwarder_session
SOURCE_CHANNEL=solearlytrending
DESTINATION_GROUP=-1001234567890
WATERMARK=📡 via MyChannel
LOG_LEVEL=INFO
```

## Usage

### First Time Setup (Login)

1. Authenticate with Telegram:
```bash
python login.py
```

2. Enter your phone number with country code (e.g., +1234567890)
3. Enter the confirmation code sent to Telegram
4. If you have 2FA enabled, enter your password

### Start the Bot

```bash
python main.py
```

The bot will:
- Connect to Telegram
- Verify channel/group access
- Start monitoring the source channel
- Forward all new messages to your group

### Check Bot Status

```bash
python status.py
```

### Stop the Bot

Press `Ctrl+C` in the terminal

## Running on VPS

### Using Systemd (Linux)

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/telegram-forwarder.service
```

2. Add the following:
```ini
[Unit]
Description=Telegram Forwarder Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-forwarder
ExecStart=/path/to/telegram-forwarder/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable telegram-forwarder
sudo systemctl start telegram-forwarder
sudo systemctl status telegram-forwarder
```

### Using Screen (Simple Method)

```bash
screen -S telegram-forwarder
python main.py
# Press Ctrl+A, then D to detach
screen -r telegram-forwarder  # To reattach
```

### Using Docker (Optional)

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

2. Run:
```bash
docker build -t telegram-forwarder .
docker run -d --name forwarder --restart unless-stopped telegram-forwarder
```

## File Structure

```
telegram-forwarder/
├── main.py                  # Core forwarding logic
├── login.py                 # Authentication helper
├── status.py                # Status checker
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .env                    # Your credentials (DO NOT COMMIT)
├── .session                # Telegram session file (auto-generated)
├── forwarded_messages.txt  # Track forwarded message IDs (auto-generated)
├── forwarder.log          # Application logs (auto-generated)
└── README.md              # This file
```

## Troubleshooting

### FloodWaitError
- Telegram rate limit reached
- Bot will automatically wait and retry
- Reduce forwarding speed if this occurs frequently

### Connection Errors
- Bot automatically reconnects
- Check internet connection
- Verify API credentials

### Messages Not Forwarding
- Check bot is member of both channel and group
- Verify bot has permission to post in destination group
- Check logs with `tail -f forwarder.log`

### Session File Issues
- Delete `*.session` files and run `python login.py` again
- This will create a fresh session

## Security Notes

- **NEVER** commit `.env` file to version control
- **NEVER** share your session files
- Keep `api_hash` private
- Use strong 2FA on your Telegram account
- Consider using a separate Telegram account for the bot

## Logging

Logs are saved to `forwarder.log` with the following levels:
- INFO: Normal operations
- WARNING: Minor issues
- ERROR: Failures
- DEBUG: Detailed information

View logs in real-time:
```bash
tail -f forwarder.log
```

## License

MIT License - Use at your own risk

## Contributing

Feel free to submit issues and pull requests
