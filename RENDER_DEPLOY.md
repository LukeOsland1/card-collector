# 🚀 Deploy to Render.com - Complete Guide

Deploy your Card Collector web application to **Render.com** for FREE! This guide provides step-by-step instructions with screenshots and troubleshooting.

## 🌟 **Why Render.com?**

- ✅ **100% Free** for small applications (no credit card required)
- ✅ **Automatic deployments** from GitHub
- ✅ **Free SSL certificates** (HTTPS)
- ✅ **Global CDN** for fast loading worldwide
- ✅ **Zero downtime deployments**
- ✅ **Built-in monitoring** and logs
- ✅ **Custom domains** supported (free)

**Perfect for Discord bots, personal projects, and small communities!**

---

## 📋 **Prerequisites (5 minutes)**

### **What You Need:**
1. **GitHub account** ([github.com](https://github.com) - free)
2. **Discord bot token** ([Get one here](https://discord.com/developers/applications))
3. **Email address** (for Render signup)

### **What You'll Get:**
- 🌐 **Live web application** at `https://your-app-name.onrender.com`
- 🤖 **Discord bot** running 24/7
- 📱 **Mobile-friendly interface**
- 🔐 **Discord OAuth login**
- 📊 **Admin dashboard**

---

## 🎯 **Step 1: Prepare Your Repository**

### **Option A: Fork the Repository (Recommended)**

1. **Go to the Card Collector repository:**
   - Visit: [github.com/LukeOsland1/card-collector](https://github.com/LukeOsland1/card-collector)

2. **Fork the repository:**
   - Click the **"Fork"** button (top-right)
   - Select your GitHub account as the destination
   - Wait for the fork to complete

3. **Your forked repository is ready!**
   - URL will be: `https://github.com/YOUR-USERNAME/card-collector`

### **Option B: Clone and Push to Your Own Repository**

```bash
# Clone the repository
git clone https://github.com/LukeOsland1/card-collector.git
cd card-collector

# Create a new repository on GitHub (via web interface)
# Then connect your local repository
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

---

## 🔑 **Step 2: Get Your Discord Bot Token**

### **Create Discord Application:**

1. **Visit Discord Developer Portal:**
   - Go to: [discord.com/developers/applications](https://discord.com/developers/applications)
   - Click **"New Application"**

2. **Create Your Application:**
   ```
   Application Name: My Card Collector Bot
   Click "Create"
   ```

3. **Create the Bot:**
   - Go to **"Bot"** section (left sidebar)
   - Click **"Add Bot"** → **"Yes, do it!"**

4. **Copy Your Bot Token:**
   - Under **"Token"** section
   - Click **"Copy"**
   - **Save this token securely** - you'll need it for deployment

### **Set Bot Permissions:**

1. **Go to "Bot" section:**
   - **Privileged Gateway Intents**: Leave disabled (not needed)
   - **Bot Permissions**: Will be set during server invitation

---

## 🚀 **Step 3: Deploy to Render**

### **Sign Up for Render:**

1. **Visit Render.com:**
   - Go to: [render.com](https://render.com)
   - Click **"Get Started for Free"**

2. **Sign Up Options:**
   - **Recommended**: "Continue with GitHub" (easiest)
   - **Alternative**: Email signup

3. **Authorize GitHub Connection:**
   - Allow Render to access your repositories
   - You can limit access to specific repositories

### **Create Web Service:**

1. **Create New Service:**
   - Click **"New"** → **"Web Service"**

2. **Connect Repository:**
   - **Source**: GitHub
   - **Repository**: Select your `card-collector` fork
   - **Branch**: `main` (default)

3. **Configure Service Settings:**
   ```
   Name: my-card-collector
   (or any name you prefer - this will be part of your URL)
   
   Environment: Python 3
   
   Region: Select closest to your users
   (US Central, Europe, etc.)
   
   Branch: main
   
   Build Command: pip install -r requirements.txt
   
   Start Command: python start.py
   ```
   
   > 💡 **Note**: The `start.py` command automatically starts both the Discord bot and web server together! No need for separate services.

4. **Choose Plan:**
   - Select **"Free"** plan
   - **$0/month** - Perfect for small applications

---

## ⚙️ **Step 4: Configure Environment Variables**

### **Add Required Environment Variables:**

1. **In Service Configuration:**
   - Scroll down to **"Environment Variables"**
   - Click **"Add Environment Variable"**

2. **Add Each Variable:**

   **Variable 1 - Discord Bot Token:**
   ```
   Key: DISCORD_BOT_TOKEN
   Value: [Paste your Discord bot token here]
   ```

   **Variable 2 - JWT Secret:**
   ```
   Key: JWT_SECRET_KEY
   Value: my-super-secret-jwt-key-change-this-to-something-random-123
   ```

   **Variable 3 - Database Type:**
   ```
   Key: DATABASE_TYPE
   Value: mongodb
   ```

   **Variable 4 - MongoDB Connection (Recommended):**
   ```
   Key: MONGODB_URL
   Value: [See MongoDB setup options below]
   ```

   **Variable 5 - MongoDB Database Name:**
   ```
   Key: MONGODB_DATABASE
   Value: card_collector
   ```

   **Variable 6 - Web Host:**
   ```
   Key: WEB_HOST
   Value: 0.0.0.0
   ```

   **Variable 7 - Debug Mode:**
   ```
   Key: DEBUG
   Value: false
   ```

   **Variable 8 - Log Level:**
   ```
   Key: LOG_LEVEL
   Value: INFO
   ```

   **🔐 Discord OAuth Variables (Required for Web Login):**

   **Variable 9 - Discord Client ID:**
   ```
   Key: DISCORD_CLIENT_ID
   Value: [Your Discord Application Client ID from Developer Portal]
   ```

   **Variable 10 - Discord Client Secret:**
   ```
   Key: DISCORD_CLIENT_SECRET
   Value: [Your Discord Application Client Secret from Developer Portal]
   ```

   **Variable 11 - Discord Redirect URI:**
   ```
   Key: DISCORD_REDIRECT_URI
   Value: https://[your-render-app-name].onrender.com/auth/callback
   ```

   > 💡 **Note:** Replace `[your-render-app-name]` with your actual Render app name. Get Discord OAuth credentials from the Discord Developer Portal.

## 📊 **Database Options for Render**

Choose the best database option for your deployment:

### **🐘 Option 1: PostgreSQL (RECOMMENDED)**

**Best for production web applications:**
- ✅ Persistent storage - never lose data
- ✅ Automatic backups - built-in protection
- ✅ Free tier available (256MB)
- ✅ Managed by Render - zero maintenance
- ✅ Better performance for web apps

**Setup Steps:**
1. **Create PostgreSQL Database:**
   - Render Dashboard → New → PostgreSQL
   - Name: `card-collector-db`
   - Plan: Free (256MB)
   - Region: Same as your web service

2. **Connect to Web Service:**
   - Go to your web service → Environment
   - Add environment variable:
   ```
   Key: DATABASE_TYPE
   Value: postgresql
   ```
   - Render automatically provides `DATABASE_URL` from your PostgreSQL service

3. **Deploy:** Your app will automatically create tables on first run!

### **🗃️ Option 2: SQLite (SIMPLE)**

**Good for development and small apps:**
- ✅ Zero configuration
- ✅ Works immediately
- ⚠️ Requires persistent disk for data retention

**Setup Steps:**
1. **Add Persistent Disk:**
   - Your web service → Settings → Environment
   - Add Disk: 1GB, mount path: `/app/data`

2. **Set Environment Variables:**
   ```
   Key: DATABASE_TYPE
   Value: sqlite
   ```
   ```
   Key: DATABASE_URL
   Value: sqlite+aiosqlite:///./data/card_collector.db
   ```

### **🍃 Option 3: MongoDB (ADVANCED)**

**For MongoDB enthusiasts (may have SSL issues on Render):**

### **Option 1: MongoDB Atlas (Recommended - FREE)**

1. **Sign up for MongoDB Atlas:**
   - Visit: [mongodb.com/atlas](https://www.mongodb.com/atlas)
   - Create free account (no credit card required)
   - Create a free M0 cluster

2. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like `mongodb+srv://...`)

3. **Update Render Environment Variable:**
   ```
   Key: MONGODB_URL
   Value: mongodb+srv://username:password@cluster.mongodb.net/
   ```

### **Option 2: Render PostgreSQL Service (Alternative)**

If you prefer SQL database on Render:

1. **Add PostgreSQL Service:**
   - Render Dashboard → "New" → "PostgreSQL"
   - Choose free plan

2. **Update Environment Variables:**
   ```
   Key: DATABASE_TYPE
   Value: postgresql
   
   Key: DATABASE_URL  
   Value: [Render provides this automatically]
   ```

### **Option 3: SQLite (Simple, but limited)**

For basic testing only:

```
Key: DATABASE_TYPE
Value: sqlite

Key: DATABASE_URL
Value: sqlite+aiosqlite:///./card_collector.db
```

**⚠️ Note:** SQLite on Render has limitations - data may be lost on deployments.

---

### **Optional Variables (for Discord OAuth):**

Add these if you want web login functionality:

```
Key: DISCORD_CLIENT_ID
Value: [Your Discord Application Client ID]

Key: DISCORD_CLIENT_SECRET  
Value: [Your Discord Application Client Secret]
```

---

## 🎉 **Step 5: Deploy!**

### **Start Deployment:**

1. **Click "Create Web Service"**
2. **Wait for Deployment** (5-15 minutes for first deploy)
3. **Monitor Progress** in the dashboard

### **Deployment Process:**
```
📥 Fetching code from GitHub...
🔨 Installing Python dependencies...
🚀 Starting web server...
✅ Deployment successful!
```

### **Your Live URL:**
Once deployed, your app will be available at:
```
https://my-card-collector.onrender.com
```
(Replace `my-card-collector` with your chosen name)

---

## 🔗 **Step 6: Configure Discord Integration**

### **Update Discord OAuth URLs:**

1. **Go to Discord Developer Portal:**
   - Visit: [discord.com/developers/applications](https://discord.com/developers/applications)
   - Select your application

2. **Add OAuth Redirect URLs:**
   - Go to **"OAuth2"** → **"General"**
   - **Redirects** section → **"Add Redirect"**
   - Add: `https://your-app-name.onrender.com/auth/callback`
   - Replace `your-app-name` with your actual app name
   - Click **"Save Changes"**

3. **Copy OAuth Credentials:**
   - **Client ID**: Copy and save
   - **Client Secret**: Click "Copy" and save

4. **Update Render Environment Variables:**
   - Go back to Render dashboard
   - Your service → **"Environment"** tab
   - Add the Discord OAuth variables:
   ```
   DISCORD_CLIENT_ID=your_client_id_here
   DISCORD_CLIENT_SECRET=your_client_secret_here
   ```

### **Invite Bot to Discord Server:**

1. **Generate Bot Invite URL:**
   - Discord Developer Portal → **"OAuth2"** → **"URL Generator"**
   - **Scopes**: Select `bot` and `applications.commands`
   - **Bot Permissions**: Select all needed permissions:
     - Send Messages
     - Use Slash Commands
     - Embed Links
     - Attach Files
     - Read Message History

2. **Copy Generated URL and Visit It:**
   - Select your Discord server
   - Click **"Authorize"**
   - Your bot should now appear online in your server!

---

## ✅ **Step 7: Test Your Deployment**

### **Test Web Interface:**

1. **Visit Your Web App:**
   - Go to: `https://your-app-name.onrender.com`
   - ✅ Home page should load

2. **Test Core Features:**
   - ✅ **Browse Cards**: `/cards` page loads
   - ✅ **API Health**: `/api/health` returns `{\"status\": \"ok\"}`
   - ✅ **API Docs**: `/docs` shows interactive documentation
   - ✅ **Discord Login**: Login button redirects to Discord

3. **Test Mobile Responsiveness:**
   - ✅ Open on your phone
   - ✅ All features work on mobile

### **Test Discord Bot:**

1. **In Your Discord Server:**
   ```
   /card my          # View your collection
   /admin setup      # Configure permissions (admin only)
   /card create      # Create a test card (moderator+)
   ```

2. **Expected Results:**
   - ✅ Bot responds to slash commands
   - ✅ Commands show proper Discord embeds
   - ✅ Data syncs between web app and Discord

---

## 🎨 **Step 8: Customization (Optional)**

### **Custom Domain:**

1. **Buy a Domain** (optional):
   - Namecheap, GoDaddy, Cloudflare, etc.
   - Example: `mycardcollector.com`

2. **Add Custom Domain to Render:**
   - Render Dashboard → Your service → **"Settings"**
   - **"Custom Domains"** section
   - Click **"Add Custom Domain"**
   - Enter your domain
   - Follow DNS setup instructions

3. **Update Discord OAuth:**
   - Update redirect URLs to use your custom domain
   - `https://mycardcollector.com/auth/callback`

### **Environment Customization:**

Add these optional environment variables for enhanced features:

```
# Branding
WATERMARK_TEXT=My Custom Card Collector

# Storage
STORAGE_PATH=storage
IMAGE_QUALITY=90

# Features
SCHEDULER_ENABLED=true

# CDN (for image hosting)
CDN_UPLOAD_URL=https://your-cdn.com/upload
CDN_BASE_URL=https://your-cdn.com
CDN_API_KEY=your_api_key
```

---

## 🔄 **Automatic Updates**

### **How It Works:**
- Render automatically deploys when you push to GitHub
- **No manual intervention required!**

### **Update Your App:**

1. **Make Changes Locally:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/card-collector.git
   cd card-collector
   # Make your changes
   git add .
   git commit -m "Update my card collector"
   git push origin main
   ```

2. **Automatic Deployment:**
   - Render detects the GitHub push
   - Automatically rebuilds and redeploys
   - **Zero downtime deployment**

### **Monitor Deployments:**
- Render Dashboard → Your service → **"Events"** tab
- See all deployments and their status
- View build logs for troubleshooting

---

## 🛠️ **Monitoring & Maintenance**

### **Check App Health:**

1. **Render Dashboard:**
   - **Metrics**: CPU, memory, response times
   - **Logs**: Real-time application logs
   - **Events**: Deployment history

2. **Health Endpoints:**
   - `https://your-app.onrender.com/api/health`
   - Should return: `{\"status\": \"ok\", \"service\": \"card-collector-web\"}`

### **View Application Logs:**

1. **Real-time Logs:**
   - Render Dashboard → Your service → **"Logs"** tab
   - Shows live application output

2. **Common Log Messages:**
   ```
   ✅ INFO: Application startup complete
   ✅ INFO: Uvicorn running on http://0.0.0.0:10000  
   ✅ INFO: Bot is ready! Logged in as BotName
   ```

### **Performance Monitoring:**

- **Free tier includes**:
  - 750 hours/month runtime (always-on for small apps)
  - 100GB bandwidth/month
  - Automatic SSL certificates
  - 99.9% uptime SLA

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**❌ "Build failed" Error:**
```
Solution:
1. Check build logs in Render dashboard
2. Verify requirements.txt exists and is valid
3. Ensure Python version compatibility
```

**❌ "Application Error" (500 Error):**
```
Solution:
1. Check environment variables are set correctly
2. Verify DISCORD_BOT_TOKEN is valid and not expired
3. Check application logs for specific error messages
```

**❌ Discord Bot Not Responding:**
```
Solution:
1. Verify DISCORD_BOT_TOKEN is correct
2. Check bot has proper permissions in Discord server
3. Ensure bot was invited with 'applications.commands' scope
4. Wait up to 1 hour for slash commands to register globally
```

**❌ Discord Login Not Working:**
```
Solution:
1. Verify DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET are set
2. Check OAuth redirect URLs in Discord Developer Portal
3. Ensure redirect URL exactly matches: https://your-app.onrender.com/auth/callback
```

**❌ Database Errors:**
```
MongoDB Issues:
1. Check MONGODB_URL format: mongodb+srv://username:password@cluster.mongodb.net/
2. Verify MongoDB Atlas cluster is running and accessible
3. Check database connection in Atlas dashboard

SQLite Issues:
1. Ensure DATABASE_URL is exactly: sqlite+aiosqlite:///./card_collector.db
2. Note: SQLite data may be lost on Render deployments
3. Consider upgrading to MongoDB Atlas (free)

General:
1. Check application logs for specific database errors
2. Restart the service in Render dashboard
3. Verify DATABASE_TYPE matches your chosen database
```

### **Getting Detailed Logs:**

1. **Enable Debug Logging:**
   ```
   Environment Variable:
   LOG_LEVEL=DEBUG
   ```

2. **View Logs:**
   - Render Dashboard → Your service → **"Logs"** tab
   - Filter by error level
   - Download logs for analysis

### **Performance Issues:**

**❌ Slow Response Times:**
```
Solutions:
1. Upgrade to paid plan for dedicated resources
2. Use Render's global CDN
3. Optimize database queries
4. Enable gzip compression in nginx.conf
```

**❌ App Goes to Sleep:**
```
Note: Free tier apps sleep after 15 minutes of inactivity
Solutions:
1. Upgrade to paid plan ($7/month) for always-on
2. Use a service to ping your app periodically (not recommended)
3. Accept the limitation for low-traffic apps
```

---

## 💰 **Render.com Pricing**

### **Free Tier (Perfect for Small Communities):**
- ✅ **$0/month**
- ✅ 750 hours/month (enough for always-on small apps)
- ✅ 100GB bandwidth/month
- ✅ Free SSL certificates
- ✅ Automatic deployments
- ⚠️ Apps sleep after 15 minutes of inactivity
- ⚠️ Shared resources

### **Starter Tier (Recommended for Active Communities):**
- 💰 **$7/month**
- ✅ Always-on (no sleeping)
- ✅ Dedicated CPU and memory
- ✅ 100GB bandwidth/month
- ✅ Priority support
- ✅ All free tier features

### **Pro Tier (For Large Communities):**
- 💰 **$25/month**
- ✅ High-performance resources
- ✅ 1TB bandwidth/month
- ✅ Advanced monitoring
- ✅ Priority support

---

## 🎯 **Advanced Configuration**

### **Database Upgrade (Optional):**

For high-traffic applications, consider PostgreSQL:

1. **Add PostgreSQL Service:**
   - Render Dashboard → **"New"** → **"PostgreSQL"**
   - Choose plan (free tier available)

2. **Update Environment Variable:**
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   ```
   (Render provides this automatically)

### **Redis for Caching (Optional):**

1. **Add Redis Service:**
   - Render Dashboard → **"New"** → **"Redis"**

2. **Environment Variable:**
   ```
   REDIS_URL=redis://host:port
   ```

### **✨ All-in-One Deployment:**

Your single web service automatically runs everything:

- **🤖 Discord Bot** - Responds to slash commands and manages cards
- **🌐 Web Application** - User-friendly interface with Discord OAuth
- **📡 API Server** - RESTful API with automatic documentation
- **⚙️ Background Tasks** - Scheduled jobs and maintenance

---

## ✨ **Success Checklist**

After following this guide, you should have:

- ✅ **Live web application** at `https://your-app.onrender.com`
- ✅ **Discord bot** responding to slash commands
- ✅ **MongoDB Atlas database** (or your chosen database) running
- ✅ **Automatic deployments** from GitHub
- ✅ **Free SSL certificate** (HTTPS)
- ✅ **Mobile-responsive** interface
- ✅ **Discord OAuth login** working
- ✅ **Admin dashboard** accessible
- ✅ **API documentation** at `/docs`
- ✅ **Monitoring and logs** in Render dashboard
- ✅ **Scalable database** ready for growth

### **Share Your Success!**

Your Card Collector is now live on the internet! Share it with your Discord community:

```
🎉 Our Card Collector is now live!

🌐 Web App: https://your-app.onrender.com
🤖 Bot Commands: /card my, /admin setup
📱 Mobile Friendly: Works on all devices
🔐 Login: Use your Discord account

Start collecting cards today! 🎴
```

---

## 📞 **Need Help?**

### **Resources:**
- 📖 **Render Documentation**: [render.com/docs](https://render.com/docs)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/LukeOsland1/card-collector/issues)
- 💬 **Discord Setup Guide**: [DISCORD_SETUP.md](DISCORD_SETUP.md)
- 🚀 **General Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

### **Community Support:**
- Create a GitHub issue with your problem
- Include your Render logs and error messages
- Mention you're following the Render deployment guide

---

**🎉 Congratulations! Your Card Collector is now live on Render.com!**

**Made with ❤️ for Discord communities worldwide**

🤖 **Generated with [Claude Code](https://claude.ai/code)**