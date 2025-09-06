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

### **🪟 Windows Users (Easiest)**

1. **Download** the project from GitHub
2. **Double-click** `install.bat` 
3. **Follow the prompts** to enter your Discord bot token
4. **Done!** 🎉

> **Detailed Windows Guide**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

### **🐧 Linux/Mac Users**

```bash
# 1. Clone repository
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# 2. Quick development setup
python run.py
# OR full production setup
python start.py
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

## ⚙️ **Configuration**

### **Getting Your Discord Bot Token**

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a **New Application**
3. Go to **"Bot"** section → Create bot
4. Copy the **bot token**
5. Edit `.env` file: `DISCORD_BOT_TOKEN=your_token_here`

### **Bot Permissions Required**
- ✅ Send Messages
- ✅ Use Slash Commands
- ✅ Embed Links
- ✅ Attach Files
- ✅ Read Message History

### **Environment Variables**
```env
# Required
DISCORD_BOT_TOKEN=your_bot_token_here
JWT_SECRET_KEY=your-super-secret-key

# Optional (for web login)
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret

# Database (SQLite default)
DATABASE_URL=sqlite+aiosqlite:///./card_collector.db
```

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