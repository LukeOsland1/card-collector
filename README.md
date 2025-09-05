# Card Collector Discord Bot

A comprehensive Discord bot for managing collectible cards with a web interface. Features card creation, assignment, expiry tracking, and user collections with Discord OAuth2 integration.

## Features

### Discord Bot
- **Card Management**: Create, submit, approve/reject cards with moderation workflow
- **Card Assignment**: Assign cards to users with optional expiry dates
- **User Collections**: Users can view their cards, filter by status, rarity, and tags
- **Expiry System**: Automatic expiry handling with user notifications
- **Permission System**: Role-based permissions for admins and moderators
- **Rich Embeds**: Beautiful card displays with pagination

### Web Interface
- **My Cards Page**: Web dashboard to view card collections
- **Discord OAuth2**: Secure login with Discord account
- **Search & Filter**: Find cards by name, rarity, tags, and status
- **Responsive Design**: Works on desktop and mobile devices

### Technical Features
- **Production Ready**: Docker containers, PostgreSQL support
- **Database Migrations**: Alembic for schema management
- **Background Jobs**: APScheduler for expiry processing
- **Comprehensive API**: RESTful API with FastAPI
- **Testing**: Unit tests with pytest
- **Security**: JWT tokens, input validation, SQL injection protection

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- Discord application with bot token
- PostgreSQL (for production) or SQLite (for development)

### 1. Clone and Setup
```bash
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` with your Discord application settings:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
OAUTH_REDIRECT_URI=http://localhost:8080/oauth/callback
JWT_SECRET=your-secure-random-string-here
```

### 3. Run Development Environment
```bash
# Using the development script
chmod +x scripts/run_dev.sh
./scripts/run_dev.sh

# Or manually
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
# alembic upgrade head  # (when migrations are available)
# python db/seeds.py    # Optional: add sample data
python -m web.app &     # Start web server
python -m bot.main      # Start Discord bot
```

### 4. Access Services
- **Web Interface**: http://localhost:8080
- **Bot**: Invite to your Discord server using Discord Developer Portal

## Production Deployment (Docker)

### 1. Setup Environment
```bash
cp .env.example .env
# Configure production values in .env
```

### 2. Start with Docker Compose
```bash
# Start all services
docker-compose up --build -d

# Run migrations
docker-compose exec bot alembic upgrade head

# Optional: Add sample data
docker-compose exec bot python db/seeds.py
```

### 3. Access Services
- **Web Interface**: http://localhost:8080
- **Database Admin**: http://localhost:8081 (Adminer, optional)
- **Database**: localhost:5432

## Discord Bot Setup

### 1. Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable required intents (Message Content Intent if needed)

### 2. Setup OAuth2
1. Go to "OAuth2" → "General" section
2. Add redirect URI: `http://localhost:8080/oauth/callback` (or your domain)
3. Copy Client ID and Client Secret to your `.env` file

### 3. Invite Bot to Server
1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`, `applications.commands`
3. Select bot permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`
4. Use generated URL to invite bot to your server

## Slash Commands Reference

### User Commands
- `/card my [active_only] [search] [rarity] [tag]` - View your card collection
- `/card info <card_id|instance_id>` - Get detailed card information

### Moderator Commands
- `/card create <name> <rarity> <image> [description] [tags] [max_supply]` - Create and approve a card
- `/card approve <card_id>` - Approve a submitted card
- `/card reject <card_id> [reason]` - Reject a submitted card
- `/card assign <card_id> <@user> [expires_in_minutes] [note]` - Assign card to user
- `/card remove <instance_id>` - Remove a card instance

### User Submission
- `/card submit <name> <rarity> <image> [description] [tags]` - Submit card for review

## API Reference

### Authentication
Most user endpoints require a Bearer token obtained through Discord OAuth2:
```http
Authorization: Bearer <jwt_token>
```

### Key Endpoints
- `GET /api/health` - Health check
- `GET /api/cards` - List approved cards
- `GET /api/cards/{id}` - Get specific card
- `GET /api/users/@me/cards` - Get user's cards (auth required)
- `GET /api/instances/{id}` - Get card instance details (auth required)

## Development

### Running Tests
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Project Structure
```
card-collector/
├── bot/                    # Discord bot code
│   ├── commands.py         # Slash commands
│   ├── embeds.py          # Message embeds
│   ├── permissions.py     # Permission checking
│   ├── scheduler.py       # Background jobs
│   └── main.py            # Bot entry point
├── web/                   # Web application
│   ├── app.py             # FastAPI application
│   ├── auth.py            # OAuth2 authentication
│   ├── routers/           # API routes
│   ├── templates/         # HTML templates
│   └── static/            # CSS/JS assets
├── db/                    # Database layer
│   ├── models.py          # SQLAlchemy models
│   ├── crud.py            # Database operations
│   ├── migrations/        # Alembic migrations
│   └── seeds.py           # Sample data
├── tests/                 # Test suite
├── scripts/               # Utility scripts
└── docker-compose.yml     # Docker orchestration
```

## License

MIT License. See `LICENSE` file for details.

## Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/) for Discord integration
- [FastAPI](https://fastapi.tiangolo.com/) for the web API
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [APScheduler](https://apscheduler.readthedocs.io/) for background jobs