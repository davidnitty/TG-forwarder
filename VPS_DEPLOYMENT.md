# VPS Deployment Guide

## Prerequisites

- A VPS with at least 512MB RAM (1GB recommended)
- Ubuntu 20.04+ or similar Linux distribution
- Root or sudo access

## Method 1: Traditional Python Deployment

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python and Dependencies

```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### Step 3: Clone or Upload Project

```bash
# Option A: Clone from git (if you have one)
cd /opt
git clone your-repo-url telegram-forwarder

# Option B: Manual upload
# Upload files via SCP or SFTP to /opt/telegram-forwarder
```

### Step 4: Setup Environment

```bash
cd /opt/telegram-forwarder
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Edit with your credentials
```

### Step 5: First Login

```bash
python login.py
```

### Step 6: Test Run

```bash
python main.py
```

Press Ctrl+C after verifying it works.

### Step 7: Setup Systemd Service

```bash
sudo nano /etc/systemd/system/telegram-forwarder.service
```

Add:

```ini
[Unit]
Description=Telegram Forwarder Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/telegram-forwarder
ExecStart=/opt/telegram-forwarder/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Step 8: Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-forwarder
sudo systemctl start telegram-forwarder
sudo systemctl status telegram-forwarder
```

### Monitor and Manage

```bash
# View logs
sudo journalctl -u telegram-forwarder -f

# View last 100 lines
sudo journalctl -u telegram-forwarder -n 100

# Restart service
sudo systemctl restart telegram-forwarder

# Stop service
sudo systemctl stop telegram-forwarder

# Check status
sudo systemctl status telegram-forwarder
```

## Method 2: Docker Deployment

### Step 1: Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

### Step 2: Install Docker Compose (Optional)

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Setup Environment

```bash
cd /opt/telegram-forwarder
cp .env.example .env
nano .env  # Edit with your credentials
```

### Step 4: First Login (Create Session)

```bash
docker run --rm -it -v $(pwd)/data:/app/data --env-file .env telegram-forwarder python login.py
```

### Step 5: Start Container

Using Docker:
```bash
docker build -t telegram-forwarder .
docker run -d --name telegram-forwarder --restart unless-stopped --env-file .env -v $(pwd)/data:/app/data telegram-forwarder
```

Using Docker Compose:
```bash
docker-compose up -d
```

### Monitor and Manage

```bash
# View logs
docker logs -f telegram-forwarder

# View last 100 lines
docker logs --tail 100 telegram-forwarder

# Restart container
docker restart telegram-forwarder

# Stop container
docker stop telegram-forwarder

# Check status
docker ps | grep telegram-forwarder

# Enter container shell
docker exec -it telegram-forwarder bash
```

## Method 3: Screen (Quick & Dirty)

```bash
# Install screen
sudo apt install -y screen

# Create screen session
screen -S telegram-forwarder

# Navigate to project
cd /opt/telegram-forwarder
source venv/bin/activate

# Start bot
python main.py

# Press Ctrl+A, then D to detach

# Reattach when needed
screen -r telegram-forwarder

# List all screens
screen -ls
```

## Monitoring and Maintenance

### Log Rotation

```bash
# Install logrotate
sudo apt install -y logrotate

# Create config
sudo nano /etc/logrotate.d/telegram-forwarder
```

Add:

```
/opt/telegram-forwarder/forwarder.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload telegram-forwarder > /dev/null 2>&1 || true
    endscript
}
```

### Auto-Update Script

```bash
#!/bin/bash
# /opt/telegram-forwarder/update.sh

cd /opt/telegram-forwarder
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
systemctl restart telegram-forwarder
```

Make executable:
```bash
chmod +x /opt/telegram-forwarder/update.sh
```

### Monitoring Script (Cron)

```bash
#!/bin/bash
# /opt/telegram-forwarder/monitor.sh

if ! systemctl is-active --quiet telegram-forwarder; then
    echo "Telegram forwarder is not running! Starting..." | mail -s "Alert: Forwarder Down" admin@example.com
    systemctl start telegram-forwarder
fi
```

Add to cron:
```bash
crontab -e
```

Add line to check every 5 minutes:
```
*/5 * * * * /opt/telegram-forwarder/monitor.sh
```

## Security Best Practices

### 1. Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS (if you add web interface later)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 2. Create Dedicated User

```bash
# Create user
sudo useradd -m -s /bin/bash telegrambot

# Add to docker group (if using Docker)
sudo usermod -aG docker telegrambot

# Set ownership
sudo chown -R telegrambot:telegrambot /opt/telegram-forwarder

# Switch to user
su - telegrambot
```

### 3. File Permissions

```bash
# Restrict .env file
chmod 600 .env

# Restrict session files
chmod 600 *.session

# Restrict log files
chmod 640 forwarder.log
```

## Troubleshooting

### Bot Won't Start

1. Check logs:
```bash
sudo journalctl -u telegram-forwarder -n 50
```

2. Verify credentials in `.env`

3. Test manually:
```bash
cd /opt/telegram-forwarder
source venv/bin/activate
python main.py
```

### Connection Issues

1. Check internet connectivity:
```bash
ping -c 3 telegram.org
```

2. Verify firewall settings

3. Check Telegram API status

### Memory Issues

Create swap file:
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Performance Tuning

### For High-Volume Channels

1. Increase timeout in `.env`:
```env
RECONNECT_TIMEOUT=30
```

2. Adjust log level:
```env
LOG_LEVEL=WARNING
```

3. Use faster storage (SSD)

4. Consider multiple bot instances for different channels

## Backup and Restore

### Backup Script

```bash
#!/bin/bash
# /opt/telegram-forwarder/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/telegram-forwarder"
mkdir -p $BACKUP_DIR

# Backup critical files
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz \
    /opt/telegram-forwarder/.env \
    /opt/telegram-forwarder/*.session \
    /opt/telegram-forwarder/forwarded_messages.txt

# Keep last 7 days
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
```

### Restore

```bash
tar -xzf /backup/telegram-forwarder/backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

## Getting Help

- Check logs: `tail -f forwarder.log`
- Test locally before deploying
- Start with one channel, add more gradually
- Monitor resource usage: `htop`
