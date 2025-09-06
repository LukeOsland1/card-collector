# 🌐 Step-by-Step Web Hosting Guide

This guide will walk you through hosting your Card Collector web application on the internet, making it accessible to anyone with a web browser.

## 📋 **Before You Start**

### **Prerequisites Checklist**
- ✅ **Discord Bot Token** ([Get one here](https://discord.com/developers/applications))
- ✅ **GitHub Account** (to store your code)
- ✅ **Email Address** (for hosting platform signup)
- ✅ **5-10 minutes** of free time

### **What You'll Get**
- 🌐 **Public web application** accessible from anywhere
- 🔗 **Custom URL** (e.g., `https://your-app.onrender.com`)
- 📱 **Mobile-friendly interface** 
- 🔐 **Discord login integration**
- 📊 **Admin dashboard** for management
- 📚 **API documentation** at `/docs`

---

## 🚀 **Method 1: Render.com (Recommended - FREE)**

**Why Render.com?**
- ✅ **Completely free** for small apps
- ✅ **No credit card required**
- ✅ **Automatic deployments** from GitHub
- ✅ **Free SSL certificates**
- ✅ **Great performance**

### **Step 1: Prepare Your Code**

1. **Fork this repository:**
   - Go to [GitHub Card Collector Repository](https://github.com/LukeOsland1/card-collector)
   - Click **"Fork"** (top-right corner)
   - This creates your own copy of the code

2. **Get your Discord Bot Token:**
   - Visit [Discord Developer Portal](https://discord.com/developers/applications)
   - Click **"New Application"** → Enter name → **"Create"**
   - Go to **"Bot"** section → **"Add Bot"**
   - Copy the **Token** (you'll need this soon)

### **Step 2: Deploy to Render**

1. **Sign up for Render:**
   - Go to [render.com](https://render.com)
   - Click **"Get Started for Free"**
   - Sign up with your GitHub account

2. **Create a New Web Service:**
   - Click **"New"** → **"Web Service"**
   - Connect your GitHub account if not already
   - Select your **forked repository**
   - Choose the **card-collector** repository

3. **Configure the Service:**
   ```
   Name: my-card-collector (or any name you prefer)
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn web.app:app --host 0.0.0.0 --port $PORT
   ```

### **Step 3: Set Environment Variables**

1. **In Render Dashboard:**
   - Scroll down to **"Environment Variables"**
   - Click **"Add Environment Variable"**

2. **Add these variables:**
   ```
   Key: DISCORD_BOT_TOKEN
   Value: [Paste your Discord bot token here]
   
   Key: JWT_SECRET_KEY  
   Value: my-super-secret-jwt-key-change-this-123
   
   Key: DATABASE_URL
   Value: sqlite+aiosqlite:///./card_collector.db
   
   Key: WEB_HOST
   Value: 0.0.0.0
   
   Key: DEBUG
   Value: false
   ```

### **Step 4: Deploy**

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Your app will be live!** 🎉

**Your web app URL:** `https://my-card-collector.onrender.com` (replace with your chosen name)

### **Step 5: Test Your Deployment**

Visit your new web app and check:
- ✅ Home page loads
- ✅ Cards page works
- ✅ API docs available at `/docs`
- ✅ Health check returns OK at `/api/health`

---

## 🚀 **Method 2: Heroku (FREE Tier)**

**Why Heroku?**
- ✅ **Free tier available**
- ✅ **Easy Git-based deployment**
- ✅ **Great documentation**
- ⚠️ **Sleeps after 30 min of inactivity**

### **Step 1: Prepare Your Code**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LukeOsland1/card-collector.git
   cd card-collector
   ```

2. **Install Heroku CLI:**
   - Download from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
   - Install and restart your terminal

### **Step 2: Deploy to Heroku**

1. **Login to Heroku:**
   ```bash
   heroku login
   ```

2. **Create Heroku App:**
   ```bash
   heroku create my-card-collector
   ```

3. **Set Environment Variables:**
   ```bash
   heroku config:set DISCORD_BOT_TOKEN=your_discord_bot_token_here
   heroku config:set JWT_SECRET_KEY=$(openssl rand -base64 32)
   heroku config:set DATABASE_URL=sqlite+aiosqlite:///./card_collector.db
   heroku config:set WEB_HOST=0.0.0.0
   heroku config:set DEBUG=false
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

**Your web app URL:** `https://my-card-collector.herokuapp.com`

---

## 🚀 **Method 3: DigitalOcean App Platform**

**Why DigitalOcean?**
- ✅ **$5/month for reliable hosting**
- ✅ **Great performance**
- ✅ **Easy scaling**
- ⚠️ **Requires credit card**

### **Step 1: Prepare**

1. **Sign up:** [digitalocean.com](https://digitalocean.com)
2. **Fork the repository** on GitHub

### **Step 2: Deploy**

1. **Create App:**
   - Go to **Apps** in DigitalOcean dashboard
   - Click **"Create App"**
   - Connect your GitHub repository

2. **Configure App:**
   - **Source:** Your forked repository
   - **Branch:** main
   - **Autodeploy:** Yes (recommended)

3. **Environment Variables:**
   ```
   DISCORD_BOT_TOKEN=your_token_here
   JWT_SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite+aiosqlite:///./card_collector.db
   WEB_HOST=0.0.0.0
   WEB_PORT=8080
   ```

4. **Deploy and wait** for completion

---

## 🔧 **Post-Deployment Configuration**

### **Step 1: Update Discord OAuth URLs**

1. **Go to Discord Developer Portal:**
   - Visit [discord.com/developers/applications](https://discord.com/developers/applications)
   - Select your application

2. **Update OAuth2 Redirect URIs:**
   - Go to **OAuth2** → **General**
   - Add: `https://your-app-url.com/auth/callback`
   - Replace `your-app-url.com` with your actual deployed URL

3. **Copy Client Credentials:**
   - Copy **Client ID** and **Client Secret**
   - Add them to your hosting platform's environment variables:
   ```
   DISCORD_CLIENT_ID=your_client_id
   DISCORD_CLIENT_SECRET=your_client_secret
   ```

### **Step 2: Invite Your Bot to Discord**

1. **Generate Invite URL:**
   - Discord Developer Portal → **OAuth2** → **URL Generator**
   - **Scopes:** `bot`, `applications.commands`
   - **Permissions:** Send Messages, Use Slash Commands, Embed Links, Attach Files

2. **Invite Bot:**
   - Copy the generated URL
   - Visit it and select your Discord server
   - Authorize the bot

### **Step 3: Test Everything**

**Test the Web Interface:**
- ✅ Visit your deployed URL
- ✅ Try logging in with Discord
- ✅ Browse the cards page
- ✅ Check admin dashboard (if you're admin)

**Test the Discord Bot:**
- ✅ Use `/card my` in Discord
- ✅ Try `/admin setup` (admin only)
- ✅ Create a test card with `/card create`

---

## 🎯 **Customization Options**

### **Custom Domain (Optional)**

Most hosting platforms support custom domains:

1. **Buy a domain** (namecheap.com, godaddy.com, etc.)
2. **Add custom domain** in your hosting platform dashboard
3. **Update DNS records** as instructed by the platform
4. **Update Discord OAuth URLs** to use your custom domain

### **Database Upgrade (Optional)**

For production use, consider upgrading from SQLite:

1. **PostgreSQL on Heroku:**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

2. **Update DATABASE_URL:**
   ```
   DATABASE_URL=postgresql+psycopg://username:password@host:port/database
   ```

---

## 🆘 **Troubleshooting**

### **Common Issues**

**❌ "Application Error" or 500 Error**
- Check your environment variables are set correctly
- Verify your Discord bot token is valid
- Check platform logs for specific errors

**❌ Discord Login Not Working**
- Verify `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET` are set
- Check OAuth redirect URLs match your deployed domain
- Ensure the redirect URL ends with `/auth/callback`

**❌ Bot Not Responding in Discord**
- Check `DISCORD_BOT_TOKEN` is correct
- Verify bot has proper permissions in your server
- Make sure bot is invited with `applications.commands` scope

**❌ Database Errors**
- For SQLite: Ensure proper file permissions
- For PostgreSQL: Check connection string format
- Verify `DATABASE_URL` environment variable

### **Getting Help**

1. **Check Platform Logs:**
   - **Render:** Dashboard → Your service → Logs
   - **Heroku:** `heroku logs --tail`
   - **DigitalOcean:** Apps → Your app → Runtime Logs

2. **Test Health Endpoint:**
   - Visit: `https://your-app.com/api/health`
   - Should return: `{\"status\": \"ok\"}`

3. **GitHub Issues:**
   - Report issues at the [GitHub repository](https://github.com/LukeOsland1/card-collector/issues)

---

## 🎉 **Success!**

Congratulations! Your Card Collector web application is now live on the internet. You should now have:

- 🌐 **Public web application** accessible from anywhere
- 🤖 **Discord bot** responding to slash commands
- 🔐 **Secure authentication** via Discord OAuth
- 📊 **Admin dashboard** for management
- 📱 **Mobile-responsive** design
- 📚 **API documentation** for developers

**Share your deployed app URL with your Discord community and start collecting cards!** 🎴

---

**Made with ❤️ for Discord communities worldwide**

🤖 **Generated with [Claude Code](https://claude.ai/code)**