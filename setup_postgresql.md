# 🐘 PostgreSQL Setup for Card Collector on Render

This guide helps you set up PostgreSQL database for your Card Collector Discord bot on Render.com.

## 🚀 **Quick Setup (5 minutes)**

### **Step 1: Create PostgreSQL Database**

1. **Go to Render Dashboard**: [https://dashboard.render.com/](https://dashboard.render.com/)
2. **Click "New +"** → **PostgreSQL**
3. **Configure Database:**
   ```
   Name: card-collector-db
   Plan: Free (256MB)
   Region: Same as your web service
   PostgreSQL Version: 15 (default)
   ```
4. **Click "Create Database"**
5. **Wait 2-3 minutes** for database to be ready

### **Step 2: Connect to Your Web Service**

1. **Go to your web service** (card-collector)
2. **Click "Environment"** tab
3. **Add/Update Environment Variables:**

   **Required Variables:**
   ```
   DATABASE_TYPE = postgresql
   ```
   
   **Optional (Render provides automatically):**
   ```
   DATABASE_URL = [Auto-filled by Render from your PostgreSQL service]
   ```

4. **Click "Save Changes"**

### **Step 3: Deploy**

1. **Your service will automatically redeploy**
2. **Tables will be created automatically** on first run
3. **Check logs** to verify successful connection:
   ```
   INFO - Using SQL database connection
   INFO - Database connection successful
   ```

## ✅ **Verification**

Once deployed, your Card Collector will:
- ✅ Connect to PostgreSQL automatically
- ✅ Create all necessary tables (users, cards, card_instances, etc.)
- ✅ Handle Discord OAuth login with persistent user storage
- ✅ Store all bot data permanently

## 🔍 **Viewing Your Data**

### **Option 1: pgAdmin (Recommended)**
1. Download [pgAdmin](https://www.pgadmin.org/)
2. Connect using your Render PostgreSQL connection details
3. Browse tables visually

### **Option 2: Render Dashboard**
1. Go to your PostgreSQL service in Render
2. Click "Connect" → "External Connection"
3. Use connection string with any PostgreSQL client

### **Option 3: Command Line**
```bash
# Get connection string from Render PostgreSQL service
psql "your_connection_string_from_render"

# View tables
\dt

# View users
SELECT * FROM users;

# View cards
SELECT * FROM cards;
```

## 💡 **Benefits of PostgreSQL vs SQLite**

| Feature | PostgreSQL | SQLite |
|---------|------------|--------|
| **Data Persistence** | ✅ Permanent | ⚠️ Lost on redeploy |
| **Concurrent Users** | ✅ Excellent | ❌ Limited |
| **Backups** | ✅ Automatic | ❌ Manual |
| **Scaling** | ✅ Handles growth | ❌ Single file |
| **Web Apps** | ✅ Perfect fit | ⚠️ Basic only |

## 🆘 **Troubleshooting**

**Connection Failed:**
- Check `DATABASE_TYPE=postgresql` is set
- Verify PostgreSQL service is running
- Check logs for specific error messages

**Tables Not Created:**
- Tables are created automatically on first request
- Try accessing your web app at `/` to trigger creation
- Check application logs for any errors

**Performance Issues:**
- PostgreSQL free tier: 256MB storage
- Upgrade to paid plan for more storage/performance
- Monitor usage in Render dashboard

## 🎉 **You're Done!**

Your Card Collector now has a production-ready PostgreSQL database that will:
- 🔒 **Never lose data** during deployments
- 📈 **Scale with your Discord server**
- 🛡️ **Backup automatically**
- ⚡ **Perform better** than file-based databases

Happy bot building! 🚀