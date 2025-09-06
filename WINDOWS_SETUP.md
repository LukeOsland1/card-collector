# 🪟 Card Collector - Windows Setup Guide

Easy deployment of Card Collector on Windows with batch scripts.

## 🚀 Quick Install (Recommended)

### Option 1: One-Click Install
1. **Download** the project from GitHub
2. **Double-click** `install.bat`
3. **Follow the prompts** - it handles everything automatically!

### Option 2: Manual Setup
1. **Double-click** `setup.bat` to install dependencies
2. **Double-click** `config.bat` to set up your Discord bot token
3. **Double-click** `start.bat` to run the application

## 📋 Prerequisites

- **Windows 10/11** (or Windows Server 2016+)
- **Python 3.9+** installed from [python.org](https://python.org)
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

## 🎯 Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `install.bat` | Complete one-click setup | First time setup |
| `setup.bat` | Install dependencies only | Manual installation |
| `config.bat` | Edit configuration | Change settings |
| `start.bat` | Start production server | Normal usage |
| `dev.bat` | Start development server | Development/testing |

## 🔧 Configuration

### Getting Your Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a **New Application** (or select existing)
3. Go to **"Bot"** section in the left sidebar
4. Click **"Reset Token"** to reveal your bot token
5. **Copy the token** (you'll need this in step 6)
6. Run `config.bat` and paste the token in the `.env` file

### Required Bot Permissions
When inviting your bot to Discord, ensure it has these permissions:
- ✅ Send Messages
- ✅ Use Slash Commands  
- ✅ Embed Links
- ✅ Attach Files
- ✅ Read Message History
- ✅ Manage Messages (for moderators)

### Invite URL Generator
Use this URL to generate an invite link for your bot:
```
https://discord.com/developers/applications/[YOUR_APP_ID]/oauth2/url-generator
```

## 🎮 Usage

### Starting the Application

**Production Mode (Recommended):**
```batch
start.bat
```
- Full features enabled
- Background jobs running
- Web interface + Discord bot
- Automatic database setup

**Development Mode:**
```batch
dev.bat
```
- Development-friendly logging
- Auto-reload on changes
- Reduced features for testing

### Accessing Services

Once started, you can access:
- **Discord Bot**: Use slash commands in your Discord server
- **Web Interface**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Admin Dashboard**: http://localhost:8080/admin (login required)

## 📊 Discord Commands

### User Commands
- `/card my` - View your card collection
- `/card submit` - Submit a card for review
- `/card info <id>` - Get information about a card

### Moderator Commands
- `/card create` - Create and approve a card instantly
- `/card assign <card> <user>` - Assign a card to a user
- `/card approve <id>` - Approve a submitted card
- `/card reject <id>` - Reject a submitted card
- `/card queue` - View cards waiting for approval

### Admin Commands
- `/admin setup` - Configure server permissions
- `/admin stats` - View server statistics
- `/admin audit` - View recent actions

## 🔧 Troubleshooting

### Common Issues

**"Python is not installed"**
- Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH"
- Restart command prompt after installation

**"Virtual environment failed"**
- Run Command Prompt as Administrator
- Make sure you have write permissions in the project folder

**"Failed to install dependencies"**
- Check your internet connection
- Try running `setup.bat` again
- Some packages require Microsoft Visual C++ Build Tools

**Bot doesn't respond to commands**
- Verify your Discord bot token in `.env`
- Make sure the bot is invited to your server with correct permissions
- Check that the bot is online in Discord

**Web interface won't load**
- Check if port 8080 is available (not used by another program)
- Try changing `WEB_PORT=8080` in `.env` to a different port like `8081`
- Make sure Windows Firewall isn't blocking the application

**Database errors**
- The default SQLite database works for most users
- Files are stored in the project directory
- For multiple users, consider PostgreSQL (advanced setup)

### Getting Help

1. **Check the logs** in the `logs/` folder
2. **Review error messages** in the command prompt
3. **Verify your configuration** by running `config.bat`
4. **Test with development mode** by running `dev.bat`

### Advanced Configuration

Edit `.env` file for advanced settings:
- `DATABASE_URL` - Change database (PostgreSQL for production)
- `WEB_HOST` and `WEB_PORT` - Change web server binding
- `JWT_SECRET_KEY` - Change authentication secret
- `STORAGE_PATH` - Change where images are stored

## 🎉 Success!

If everything is working correctly, you should see:
- ✅ Discord bot online in your server
- ✅ Web interface accessible at http://localhost:8080
- ✅ Slash commands working in Discord
- ✅ No error messages in the console

**Enjoy your Card Collector bot!** 🎴

## 📞 Support

Need help? Check:
- GitHub Issues for known problems
- `.env.example` for configuration examples  
- `logs/card-collector.log` for detailed error information
- Discord Developer Documentation for bot setup help