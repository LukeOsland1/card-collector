#!/bin/bash
# Card Collector - macOS Setup Script
# Automatically creates .env file with interactive configuration

set -e  # Exit on any error

echo "============================================"
echo "   Card Collector - macOS Setup Script"
echo "============================================"
echo

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python is installed
print_step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ from: https://python.org"
    echo "Or install via Homebrew: brew install python"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
print_status "Python $python_version detected"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    echo "Please run this script from the Card Collector directory"
    exit 1
fi

print_step "Installing dependencies..."
if [ -f "install_deps.py" ]; then
    python3 install_deps.py
else
    print_warning "install_deps.py not found, using pip directly"
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
fi

# Create .env file if it doesn't exist
print_step "Setting up environment configuration..."

if [ -f ".env" ]; then
    print_warning ".env file already exists"
    echo -n "Do you want to overwrite it? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Keeping existing .env file"
        echo "Setup complete! You can run: python3 start.py"
        exit 0
    fi
fi

# Copy from env.example if it exists
if [ -f "env.example" ]; then
    cp env.example .env
    print_status "Copied env.example to .env"
else
    print_warning "env.example not found, creating .env from scratch"
    touch .env
fi

echo
echo "============================================"
echo "        DISCORD BOT CONFIGURATION"
echo "============================================"
echo
echo "To get your Discord bot token:"
echo "1. Go to: https://discord.com/developers/applications"
echo "2. Create a 'New Application'"
echo "3. Go to 'Bot' section and create a bot"
echo "4. Copy the bot token"
echo

# Get Discord bot token
while true; do
    echo -n "Enter your Discord bot token: "
    read -r -s bot_token
    echo
    
    if [ -z "$bot_token" ]; then
        print_error "Bot token cannot be empty"
        continue
    fi
    
    # Basic validation (Discord bot tokens are usually 70+ characters)
    if [ ${#bot_token} -lt 50 ]; then
        print_warning "Token seems too short. Discord bot tokens are usually 70+ characters"
        echo -n "Continue anyway? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            continue
        fi
    fi
    
    break
done

# Get JWT secret key
echo
echo -n "Enter a secret key for JWT tokens (or press Enter for auto-generated): "
read -r jwt_secret

if [ -z "$jwt_secret" ]; then
    # Generate a random JWT secret
    jwt_secret="card-collector-$(openssl rand -hex 16)-$(date +%s)"
    print_status "Generated random JWT secret key"
fi

# Optional: Discord OAuth for web login
echo
echo "============================================"
echo "     OPTIONAL: WEB LOGIN CONFIGURATION"
echo "============================================"
echo
echo "For web interface login (optional):"
echo "1. In Discord Developer Portal → OAuth2 → General"
echo "2. Add redirect URI: http://localhost:8080/auth/callback"
echo "3. Copy Client ID and Client Secret"
echo

echo -n "Do you want to configure web login? (y/N): "
read -r setup_oauth

client_id=""
client_secret=""

if [[ "$setup_oauth" =~ ^[Yy]$ ]]; then
    echo -n "Enter Discord Client ID: "
    read -r client_id
    
    echo -n "Enter Discord Client Secret: "
    read -r -s client_secret
    echo
fi

# Database configuration
echo
echo "============================================"
echo "        DATABASE CONFIGURATION"
echo "============================================"
echo
echo "Database options:"
echo "1. SQLite (default, recommended for development)"
echo "2. PostgreSQL (for production)"
echo

echo -n "Choose database type (1 or 2) [1]: "
read -r db_choice

database_url="sqlite+aiosqlite:///./card_collector.db"
if [ "$db_choice" = "2" ]; then
    echo -n "Enter PostgreSQL connection string: "
    read -r database_url
fi

# Web server configuration
echo
echo -n "Web server port [8080]: "
read -r web_port
web_port=${web_port:-8080}

echo -n "Web server host [0.0.0.0]: "
read -r web_host
web_host=${web_host:-0.0.0.0}

# Create the .env file
print_step "Creating .env file..."

# Debug: Show what we're about to write
echo "Debug: Writing .env with the following values:"
echo "  DISCORD_BOT_TOKEN: ${bot_token:0:10}..." # Show first 10 chars
echo "  JWT_SECRET_KEY: ${jwt_secret:0:20}..."
echo "  DATABASE_URL: $database_url"
echo "  WEB_HOST: $web_host"
echo "  WEB_PORT: $web_port"

# Create the .env file with proper error handling
{
cat > .env << ENVEOF
# Card Collector - Environment Configuration
# Generated automatically by setup_macos.sh on $(date)

# ===== REQUIRED SETTINGS =====
DISCORD_BOT_TOKEN=$bot_token
JWT_SECRET_KEY=$jwt_secret

# ===== DATABASE =====
DATABASE_URL=$database_url

# ===== WEB SERVER =====
WEB_HOST=$web_host
WEB_PORT=$web_port

ENVEOF
} || {
    print_error "Failed to create .env file"
    echo "Current directory: $(pwd)"
    echo "Directory permissions: $(ls -ld .)"
    exit 1
}

# Add OAuth settings if configured
if [ -n "$client_id" ] && [ -n "$client_secret" ]; then
    {
    cat >> .env << OAUTHEOF
# ===== OAUTH2 WEB LOGIN =====
DISCORD_CLIENT_ID=$client_id
DISCORD_CLIENT_SECRET=$client_secret
DISCORD_REDIRECT_URI=http://localhost:$web_port/auth/callback

OAUTHEOF
    } || {
        print_error "Failed to add OAuth settings to .env file"
        exit 1
    }
fi

# Add optional settings
{
cat >> .env << ENVEOF2
# ===== OPTIONAL SETTINGS =====
STORAGE_PATH=storage
IMAGE_QUALITY=90
SCHEDULER_ENABLED=true
DEBUG=false
LOG_LEVEL=INFO

# ===== CDN (Optional) =====
CDN_UPLOAD_URL=
CDN_BASE_URL=
CDN_API_KEY=

# ===== ADVANCED =====
API_KEY=
WATERMARK_TEXT=Card Collector
ENVEOF2
} || {
    print_error "Failed to append to .env file"
    exit 1
}

# Verify .env file was created properly
if [ -f ".env" ] && [ -s ".env" ]; then
    print_status ".env file created successfully!"
    echo "  File size: $(wc -c < .env) bytes"
    echo "  First few lines:"
    head -n 3 .env | sed 's/^/    /'
else
    print_error ".env file was not created properly"
    echo "File exists: $([ -f .env ] && echo 'YES' || echo 'NO')"
    echo "File size: $([ -f .env ] && wc -c < .env || echo 'N/A') bytes"
    exit 1
fi

# Set proper permissions
chmod 600 .env
print_status "Set .env file permissions to 600 (read/write for owner only)"

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p logs storage/{images,thumbnails,previews,cards,temp}
print_status "Created storage directories"

echo
echo "============================================"
echo "           SETUP COMPLETE!"
echo "============================================"
echo
print_status "Configuration saved to .env file"
print_status "Next steps:"
echo "  1. Invite your bot to Discord server:"
echo "     - Go to: https://discord.com/developers/applications"
echo "     - Select your app → OAuth2 → URL Generator"
echo "     - Select: bot, applications.commands"
echo "     - Copy URL and visit it to invite bot"
echo
echo "  2. Start the application:"
echo "     python3 run.py     # Quick start"
echo "     python3 start.py   # Full features"
echo
echo "  3. Access the services:"
echo "     - Discord Bot: Use slash commands in your server"
echo "     - Web Interface: http://localhost:$web_port"
echo "     - API Documentation: http://localhost:$web_port/docs"
echo
print_status "Happy card collecting! 🎴"

echo
echo "============================================"
echo "           TROUBLESHOOTING"
echo "============================================"
echo "If you encounter issues:"
echo "  • Check that .env file was created: ls -la .env"
echo "  • Verify .env contents: head .env"
echo "  • Check file permissions: ls -la .env (should be -rw-------)"
echo "  • For Python issues: python3 --version"
echo "  • For dependency issues: python3 install_deps.py"
echo "  • GitHub Issues: https://github.com/LukeOsland1/card-collector/issues"