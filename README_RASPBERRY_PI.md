# 🥧 Raspberry Pi Deployment Guide

This guide covers deploying the Card Collector Discord bot on a Raspberry Pi.

## Prerequisites

### Hardware Requirements
- **Raspberry Pi 4 (4GB+ RAM)** or Raspberry Pi 5 (recommended)
- **32GB+ MicroSD card** (Class 10 or A1/A2 rated)
- **Stable internet connection** (Ethernet preferred for reliability)

### Software Requirements
- **Raspberry Pi OS 64-bit** (Bookworm or newer)
- **Docker** (for containerized deployment)
- OR **Python 3.11+** (for native deployment)

## Setup Methods

### Option 1: Docker Deployment (Recommended)

Docker provides the cleanest deployment with automatic dependency management.

#### 1. Install Docker on Raspberry Pi
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Reboot to apply group changes
sudo reboot
```

#### 2. Clone and Configure Project
```bash
# Clone repository
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# Create environment file
cp .env.example .env

# Edit configuration (use nano or vim)
nano .env
```

#### 3. Configure Environment Variables
```bash
# Required Discord settings
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here

# Web settings
OAUTH_REDIRECT_URI=http://your-pi-ip:8080/oauth/callback
JWT_SECRET=your-secure-random-string-here

# Database (PostgreSQL in Docker)
DATABASE_URL=postgresql+psycopg://cards_user:cards_password@db:5432/cards

# Performance settings for Pi
LOG_LEVEL=INFO
```

#### 4. Deploy with Docker Compose
```bash
# Start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Native Python Installation

For maximum performance and resource efficiency on Pi.

#### 1. Install Python Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y
sudo apt install build-essential libffi-dev libssl-dev -y

# Install PostgreSQL (optional, can use SQLite)
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Setup Project
```bash
# Clone repository
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -e .

# Configure environment
cp .env.example .env
nano .env
```

#### 3. Configure for SQLite (Lightweight Option)
```bash
# Edit .env file for SQLite instead of PostgreSQL
DATABASE_URL=sqlite:///cards.db
```

#### 4. Setup Database
```bash
# Install Alembic for migrations (when available)
# alembic upgrade head

# For now, create tables manually
python -c "
from db.base import Base, async_engine
import asyncio

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())
print('Database tables created!')
"
```

#### 5. Run Services
```bash
# Start web server (in background)
nohup python -m web.app > web.log 2>&1 &

# Start Discord bot (in background)
nohup python -m bot.main > bot.log 2>&1 &

# Check processes
ps aux | grep python
```

## Raspberry Pi Optimizations

### 1. Memory Configuration
Add to `/boot/config.txt`:
```bash
# Increase GPU memory split (helps with performance)
gpu_mem=128

# Enable memory cgroup
cgroup_memory=1 cgroup_enable=memory
```

### 2. System Limits
Add to `/etc/security/limits.conf`:
```bash
# Increase open file limits
* soft nofile 65536
* hard nofile 65536
```

### 3. Docker Optimizations
Create `docker-compose.override.yml`:
```yaml
version: '3.8'
services:
  db:
    # Use lighter PostgreSQL settings for Pi
    command: postgres -c shared_buffers=128MB -c max_connections=50
    
  bot:
    # Limit memory usage
    mem_limit: 512m
    
  web:
    # Limit memory usage  
    mem_limit: 256m
```

### 4. Performance Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Monitor resources
htop              # CPU/Memory usage
iotop             # Disk I/O
docker stats      # Container resource usage
```

## Networking Setup

### 1. Static IP Configuration
Edit `/etc/dhcpcd.conf`:
```bash
# Static IP configuration
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

### 2. Port Forwarding
If accessing from outside your network:
- **Port 8080** - Web interface
- Configure your router to forward these ports to your Pi's IP

### 3. Domain Setup (Optional)
Use Dynamic DNS services like:
- DuckDNS
- No-IP
- FreeDNS

## Auto-Start on Boot

### For Docker Deployment
```bash
# Docker services auto-start by default
# Verify with:
docker-compose config
```

### For Native Installation
Create systemd service files:

#### Bot Service (`/etc/systemd/system/cardbot.service`)
```ini
[Unit]
Description=Card Collector Discord Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/card-collector
Environment=PATH=/home/pi/card-collector/.venv/bin
ExecStart=/home/pi/card-collector/.venv/bin/python -m bot.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Web Service (`/etc/systemd/system/cardweb.service`)
```ini
[Unit]
Description=Card Collector Web Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/card-collector
Environment=PATH=/home/pi/card-collector/.venv/bin
ExecStart=/home/pi/card-collector/.venv/bin/python -m web.app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Enable Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable cardbot cardweb
sudo systemctl start cardbot cardweb

# Check status
sudo systemctl status cardbot
sudo systemctl status cardweb
```

## Maintenance

### Regular Updates
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update project
cd card-collector
git pull origin master

# Restart services
docker-compose restart  # For Docker
# OR
sudo systemctl restart cardbot cardweb  # For native
```

### Log Management
```bash
# View logs
docker-compose logs -f bot web  # Docker
journalctl -u cardbot -f        # Native bot
journalctl -u cardweb -f        # Native web

# Rotate logs to prevent disk fill
sudo logrotate -f /etc/logrotate.conf
```

### Backup Strategy
```bash
# Backup database
docker-compose exec db pg_dump -U cards_user cards > backup.sql

# Backup configuration
cp .env .env.backup
tar -czf config-backup.tar.gz .env docker-compose.yml
```

## Troubleshooting

### Common Issues

#### 1. Out of Memory
```bash
# Check memory usage
free -h
docker stats

# Add swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### 2. Slow Performance
```bash
# Check SD card speed
sudo hdparm -t /dev/mmcblk0

# Monitor I/O
iotop -o

# Consider using USB 3.0 SSD instead of SD card
```

#### 3. Docker Issues
```bash
# Clean up Docker resources
docker system prune -a

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 4. Network Connectivity
```bash
# Test Discord API connectivity
curl -I https://discord.com/api/v10/gateway

# Check DNS resolution
nslookup discord.com
```

## Performance Expectations

### Raspberry Pi 4 (4GB)
- **Bot Response Time**: < 500ms for most commands
- **Web Interface**: Responsive for 1-10 concurrent users
- **Memory Usage**: ~400MB total (all services)
- **Storage**: ~2GB for full installation

### Raspberry Pi 5
- **Significantly better performance** across all metrics
- **Faster startup times** and command processing
- **Better concurrent user handling**

## Security Considerations

### 1. Firewall Setup
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw status
```

### 2. SSH Security
```bash
# Change default SSH port
sudo nano /etc/ssh/sshd_config  # Change Port 22 to something else
sudo systemctl restart ssh
```

### 3. Keep Updated
```bash
# Automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## Support

If you encounter issues:
1. Check the main project README.md
2. Review Docker/systemd logs
3. Monitor Pi resources with `htop`
4. Verify Discord API connectivity

The Card Collector bot runs efficiently on Raspberry Pi 4+ with proper configuration!