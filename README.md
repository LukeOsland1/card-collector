# 🎴 Card Collector - Discord Bot & Web Platform

A comprehensive, production-ready Discord bot and web application for managing collectible card communities. Create, trade, and collect digital cards with your friends!

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3%2B-7289da?logo=discord)](https://discordpy.readthedocs.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ **Key Features**

### 🤖 **Discord Bot**
- **Slash Commands**: Modern Discord slash command interface
- **Card Management**: Create, submit, approve/reject cards with moderation workflow
- **Card Assignment**: Assign cards to users with optional expiry dates
- **User Collections**: Filter by rarity, tags, and status
- **Permission System**: Role-based permissions for admins and moderators
- **Rich Embeds**: Beautiful card displays with pagination
- **Expiry System**: Automatic handling with notifications

### 🌐 **Web Interface**
- **Modern UI**: Responsive design with Bootstrap 5
- **Discord OAuth2**: Secure login with Discord account
- **Admin Dashboard**: Statistics, user management, system health
- **Card Browser**: Search, filter, and discover cards
- **Collection Manager**: View and organize your cards
- **API Documentation**: Interactive OpenAPI/Swagger docs

### ⚡ **Technical Features**
- **Production Ready**: Docker support, PostgreSQL compatibility
- **Database Migrations**: Alembic for schema management
- **Background Jobs**: APScheduler for automated tasks
- **Image Processing**: Automatic thumbnails and card previews
- **Comprehensive API**: RESTful API with authentication
- **Security**: JWT tokens, input validation, audit logging

## 🚀 **Quick Start**

### **🪟 Windows Users (Recommended)**

1. **Download & Extract** the project from [GitHub](https://github.com/LukeOsland1/card-collector/archive/refs/heads/master.zip)
2. **Open Command Prompt** in the project folder
3. **Install dependencies**: `python install_deps.py`
4. **Setup configuration**: `copy env.example .env` and edit with your Discord bot token
5. **Run the application**: `python start.bat` or `python run.py`

> **Alternative**: Use the batch files for one-click setup - `setup.bat`, then `start.bat`

### **🐧 Linux/Mac Users**

```bash
# 1. Clone and enter repository
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# 2. Install dependencies (automatic)
python3 install_deps.py

# 3. Setup configuration
cp env.example .env
# Edit .env with your Discord bot token

# 4. Run the application
python3 run.py        # Quick development start
# OR
python3 start.py      # Full production features
```

### **⚡ One-Command Install (All Platforms)**

```bash
# Clone, install dependencies, and setup in one go
git clone https://github.com/LukeOsland1/card-collector.git && cd card-collector && python install_deps.py
```

### **🐳 Docker (Production)**

```bash
# 1. Setup environment
cp env.example .env
# Edit .env with your Discord bot token

# 2. Start with Docker Compose
docker-compose up -d

# 3. Access services
# Web: http://localhost:8080
# API Docs: http://localhost:8080/docs
```

## 📋 **Prerequisites**

- **Python 3.9+** ([Download Python](https://python.org))
- **Discord Bot Token** ([Discord Developer Portal](https://discord.com/developers/applications))
- **PostgreSQL** (production) or **SQLite** (development)

## 🛠️ **Installation Troubleshooting**

### **Common Issues & Solutions**

#### **"ModuleNotFoundError: No module named 'dotenv'"**
```bash
# Solution: Install dependencies
python install_deps.py
# OR manually:
pip install -r requirements.txt
```

#### **"DISCORD_BOT_TOKEN not found in environment"**
```bash
# Solution: Setup configuration file
cp env.example .env    # Linux/Mac
copy env.example .env  # Windows
# Then edit .env with your Discord bot token
```

#### **"UnicodeEncodeError" on Windows**
- **Fixed in latest version** - Windows console encoding issues resolved
- Update to latest version or run: `git pull origin master`

#### **Port 8080 already in use**
```bash
# Solution: Change port in .env file
WEB_PORT=8081
# OR kill existing process
netstat -ano | findstr :8080  # Windows
lsof -ti:8080 | xargs kill    # Linux/Mac
```

#### **Python command not found**
- **Windows**: Reinstall Python with "Add to PATH" checked
- **Linux/Mac**: Install Python 3.9+ or use `python3` instead of `python`
- **Verify**: `python --version` should show 3.9+

### **Manual Installation (If install_deps.py fails)**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import discord, fastapi, uvicorn; print('Dependencies OK!')"
```

## ⚙️ **Configuration**

### **Step-by-Step Configuration**

#### **1. Create Configuration File**
```bash
# Copy the example configuration
cp env.example .env    # Linux/Mac
copy env.example .env  # Windows
```

#### **2. Get Your Discord Bot Token**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → Enter a name (e.g., "My Card Collector")
3. Go to **"Bot"** section in the left sidebar
4. Click **"Add Bot"** (if not already created)
5. Under **"Token"**, click **"Copy"** to get your bot token
6. Open `.env` file and replace: `DISCORD_BOT_TOKEN=your_actual_bot_token_here`

#### **3. Configure Required Settings**
Edit your `.env` file with these **required** values:
```env
DISCORD_BOT_TOKEN=your_actual_bot_token_here
JWT_SECRET_KEY=change-this-to-a-random-secret-string-123
```

#### **4. Optional: Web Login Setup**
For the web interface login (optional):
1. In Discord Developer Portal → **"OAuth2"** → **"General"**
2. Add redirect URI: `http://localhost:8080/auth/callback`
3. Copy **Client ID** and **Client Secret** to your `.env`:
```env
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
```

### **Bot Permissions Required**
- ✅ Send Messages
- ✅ Use Slash Commands
- ✅ Embed Links
- ✅ Attach Files
- ✅ Read Message History

### **Complete Environment Variables Reference**
```env
# ===== REQUIRED SETTINGS =====
DISCORD_BOT_TOKEN=your_actual_bot_token_here
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this

# ===== DATABASE (Required) =====
DATABASE_URL=sqlite+aiosqlite:///./card_collector.db
# For PostgreSQL: postgresql+asyncpg://username:password@localhost/card_collector

# ===== WEB SERVER =====
WEB_HOST=0.0.0.0
WEB_PORT=8080

# ===== OPTIONAL: WEB LOGIN =====
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:8080/auth/callback

# ===== OPTIONAL: ADVANCED =====
CDN_UPLOAD_URL=
CDN_BASE_URL=
CDN_API_KEY=
STORAGE_PATH=storage
IMAGE_QUALITY=90
SCHEDULER_ENABLED=true
DEBUG=false
LOG_LEVEL=INFO
API_KEY=your-api-key-for-external-access
WATERMARK_TEXT=Card Collector
```

## 🎯 **First Run Guide**

### **After Installation & Configuration**

1. **Start the Application**:
   ```bash
   python run.py    # Quick start (development)
   python start.py  # Full features (production)
   ```

2. **Verify Everything Works**:
   - ✅ **Discord Bot**: Check Discord for slash commands (`/card`)
   - ✅ **Web Interface**: Visit http://localhost:8080
   - ✅ **API Docs**: Visit http://localhost:8080/docs

3. **Invite Bot to Your Discord Server**:
   - Go to Discord Developer Portal → Your App → **OAuth2** → **URL Generator**
   - Select **Scopes**: `bot`, `applications.commands`
   - Select **Bot Permissions**: `Send Messages`, `Use Slash Commands`, `Embed Links`, `Attach Files`, `Read Message History`
   - Copy the generated URL and visit it to invite your bot

4. **Test Basic Functionality**:
   ```
   /admin setup     # Configure server permissions (admin only)
   /card create     # Create your first card (moderator+)
   /card my         # View your collection
   ```

### **Need Help?**
- Check the **Installation Troubleshooting** section above
- Visit the API documentation at http://localhost:8080/docs
- Review logs in the `logs/` folder
- Check [GitHub Issues](https://github.com/LukeOsland1/card-collector/issues)

## 🎮 **Discord Commands**

### **👤 User Commands**
| Command | Description |
|---------|-------------|
| `/card my` | View your card collection |
| `/card submit` | Submit a card for review |
| `/card info <id>` | Get card/instance information |

### **🛡️ Moderator Commands**
| Command | Description |
|---------|-------------|
| `/card create` | Create and approve a card instantly |
| `/card assign <card> <user>` | Assign cards to users |
| `/card approve <id>` | Approve submitted cards |
| `/card reject <id>` | Reject submitted cards |
| `/card queue` | View pending approvals |

### **👑 Admin Commands**
| Command | Description |
|---------|-------------|
| `/admin setup` | Configure server permissions |
| `/admin stats` | View server statistics |
| `/admin audit` | View recent actions |

## 🌐 **Web Interface**

Once running, access these services:

- **🏠 Home Page**: http://localhost:8080
- **🎴 Browse Cards**: http://localhost:8080/cards
- **📁 My Collection**: http://localhost:8080/collection
- **⚙️ Admin Dashboard**: http://localhost:8080/admin
- **📚 API Docs**: http://localhost:8080/docs

## 🎯 **Card Rarity System**

| Rarity | Color | Description |
|--------|-------|-------------|
| **Common** | Gray | Basic cards, easy to obtain |
| **Uncommon** | Green | Slightly rare cards |
| **Rare** | Blue | Moderately difficult to obtain |
| **Epic** | Purple | Hard to find cards |
| **Legendary** | Gold | Extremely rare, prestigious cards |

## 🔧 **Deployment Options**

### **🪟 Windows (Recommended for Beginners)**
- **One-click installer**: `install.bat`
- **Production server**: `start.bat`
- **Development mode**: `dev.bat`
- **Configuration helper**: `config.bat`

### **🐧 Linux/Mac (Manual)**
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Start application
python start.py  # Production
python run.py    # Development
```

### **🐳 Docker (Production)**
```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose up -d

# Raspberry Pi
docker-compose -f docker-compose.pi.yml up -d
```

## 📁 **Project Structure**

```
card-collector/
├── 🤖 bot/                    # Discord bot implementation
│   ├── commands.py            # Slash commands
│   ├── embeds.py              # Rich Discord embeds
│   ├── permissions.py         # Permission system
│   └── main.py                # Bot entry point
├── 🌐 web/                    # Web application
│   ├── app.py                 # FastAPI application
│   ├── api.py                 # REST API endpoints
│   ├── auth.py                # OAuth2 authentication
│   ├── templates/             # HTML templates
│   └── static/                # CSS/JS assets
├── 🗄️ db/                     # Database layer
│   ├── models.py              # SQLAlchemy models
│   ├── crud.py                # Database operations
│   └── migrations/            # Alembic migrations
├── ⚙️ services/               # Background services
│   ├── scheduler.py           # Job scheduler
│   └── image_service.py       # Image processing
├── 🪟 Windows Deployment      # Easy Windows deployment
│   ├── install.bat            # One-click installer
│   ├── start.bat              # Production server
│   ├── dev.bat                # Development server
│   └── config.bat             # Configuration helper
├── 🐳 docker-compose.yml      # Docker orchestration
└── 📚 Documentation           # Setup guides and docs
```

## 🛠️ **Development**

### **Running Tests**
```bash
# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### **Database Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Reset database (development)
rm card_collector.db
python scripts/init_db.py
```

## 📊 **API Reference**

### **Authentication**
```http
# Login via Discord OAuth
GET /login

# API authentication
Authorization: Bearer <jwt_token>
```

### **Key Endpoints**
- `GET /api/v1/cards` - Browse all cards
- `GET /api/v1/cards/{id}` - Get specific card
- `GET /api/v1/instances` - Get user's collection
- `GET /api/v1/leaderboard` - Top collectors
- `GET /api/v1/admin/stats` - System statistics

> **Full API Documentation**: http://localhost:8080/docs

## 🔒 **Security Features**

- **🔐 JWT Authentication**: Secure token-based auth
- **🛡️ Input Validation**: Pydantic models and sanitization  
- **🔍 Audit Logging**: Track all system actions
- **👥 Role-Based Permissions**: Granular access control
- **🚫 Rate Limiting**: Prevent abuse and spam
- **📝 SQL Injection Protection**: Parameterized queries

## 🚀 **Production Deployment**

### **Environment Setup**
```bash
# Production environment variables
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cardcollector
WEB_HOST=0.0.0.0
WEB_PORT=8080
JWT_SECRET_KEY=your-production-secret-key
```

### **Performance Recommendations**
- **Database**: PostgreSQL for production
- **Web Server**: Run behind nginx/Apache proxy
- **Background Jobs**: Enable APScheduler
- **Image Storage**: Configure CDN for images
- **Monitoring**: Set up logging and health checks

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📝 **Changelog**

### **v2.0.0** (Latest)
- ✅ Complete Discord bot with slash commands
- ✅ Full web interface with authentication
- ✅ Windows one-click deployment system
- ✅ Image processing and thumbnails
- ✅ Background job scheduler
- ✅ Admin dashboard and analytics

### **v1.0.0**
- ✅ Basic Discord bot functionality
- ✅ Database models and migrations
- ✅ Docker deployment

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **[Discord.py](https://discordpy.readthedocs.io/)** - Discord API wrapper
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Database ORM
- **[Bootstrap](https://getbootstrap.com/)** - UI framework
- **[APScheduler](https://apscheduler.readthedocs.io/)** - Background jobs

## 📞 **Support & Help**

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/LukeOsland1/card-collector/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/LukeOsland1/card-collector/discussions)
- **📖 Documentation**: Check the wiki and setup guides
- **💬 Community**: Join our Discord server (coming soon!)

---

**Made with ❤️ for Discord communities worldwide**

🤖 **Generated with [Claude Code](https://claude.ai/code)**