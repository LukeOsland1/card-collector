# Discord Bot Setup Guide

## 🚀 Quick Setup

### 1. Create Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Enter a name (e.g., "My Card Collector")
4. Click **"Create"**

### 2. Create Bot & Get Token
1. Go to **"Bot"** section in left sidebar
2. Click **"Add Bot"**
3. Under **"Token"**, click **"Copy"**
4. Save this token - you'll need it for your `.env` file

### 3. Configure Bot Permissions
**Slash Commands (Recommended):**
- ✅ `Send Messages`
- ✅ `Use Slash Commands` 
- ✅ `Embed Links`
- ✅ `Attach Files`
- ✅ `Read Message History`

**Privileged Intents (Usually NOT needed):**
- ❌ `Message Content Intent` - Only if you want prefix commands (!)

### 4. Invite Bot to Server
1. Go to **"OAuth2"** → **"URL Generator"**
2. Select **Scopes**: `bot`, `applications.commands`
3. Select **Bot Permissions** (from step 3 above)
4. Copy generated URL and visit it
5. Select your Discord server and authorize

## 🔧 Common Issues & Solutions

### ❌ "PrivilegedIntentsRequired" Error
```
discord.errors.PrivilegedIntentsRequired: Shard ID None is requesting privileged intents...
```

**Solution 1: Disable Privileged Intents (Recommended)**
- Card Collector uses slash commands primarily
- No privileged intents needed for slash commands
- This is already fixed in the latest version

**Solution 2: Enable Privileged Intents (If needed)**
1. Go to Discord Developer Portal → Your App → **"Bot"**
2. Scroll to **"Privileged Gateway Intents"**
3. Enable **"Message Content Intent"** 
4. Click **"Save Changes"**
5. Restart the application

### ❌ "LoginFailure" / "401 Unauthorized" Error
```
discord.errors.LoginFailure: Improper token has been passed.
```

**Solutions:**
1. **Check your token**: Make sure it's copied correctly
2. **Reset token**: In Discord Developer Portal → Bot → Reset Token
3. **Update .env file**: `DISCORD_BOT_TOKEN=your_new_token_here`

### ❌ Bot Not Responding to Commands
1. **Check bot is online**: Should show as online in your Discord server
2. **Re-invite bot**: Use OAuth2 URL Generator with `applications.commands` scope
3. **Wait for sync**: Slash commands may take up to 1 hour to appear globally

## 🎯 Bot Features

### Slash Commands
- `/card my` - View your collection
- `/card submit` - Submit a card for review
- `/card info <id>` - Get card information
- `/admin setup` - Configure server (admins only)
- And many more!

### Web Interface
- View collections online
- Admin dashboard
- API documentation
- Discord OAuth login

## 🔐 Security Best Practices

1. **Keep token secret**: Never share your bot token publicly
2. **Use environment files**: Store token in `.env` file, not code
3. **Regenerate if compromised**: Reset token if accidentally exposed
4. **Minimum permissions**: Only enable intents/permissions you need

## 📞 Need Help?

- **Run**: `python3 configure_token.py` for interactive setup
- **Check**: `python3 check_deps.py` for dependency issues  
- **Read**: `QUICK_FIX.md` for common problems
- **Issues**: [GitHub Issues](https://github.com/LukeOsland1/card-collector/issues)

## 🎉 Success!

Once properly configured, you should see:
```
INFO:__main__:Discord bot starting...
INFO:discord.client:logging in using static token
INFO:discord.gateway:Shard ID None has connected to Gateway
INFO:bot.main:Setting up bot...
INFO:bot.main:Bot is ready!
```

Your Card Collector bot is now ready to manage collectible cards! 🎴