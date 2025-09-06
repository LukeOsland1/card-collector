# 🍃 MongoDB Setup Guide for Card Collector

This guide will help you migrate from SQLite to MongoDB for better scalability and performance.

## 🌟 **Why MongoDB?**

- ✅ **Better scalability** for large card collections
- ✅ **Flexible schema** for evolving data models  
- ✅ **Advanced querying** with aggregation pipelines
- ✅ **High performance** for read/write operations
- ✅ **Cloud-ready** with MongoDB Atlas
- ✅ **Native JSON storage** perfect for Discord bot data

## ⚡ **Quick Setup (Automated)**

### **Option 1: Automatic Setup Script**

```bash
# Run the automated MongoDB setup
python install_mongodb.py
```

This script will:
- Install Python MongoDB dependencies
- Check MongoDB installation
- Test connection
- Configure environment variables
- Provide platform-specific installation instructions

### **Option 2: Manual Setup**

Follow the steps below for manual installation and configuration.

---

## 📦 **Step 1: Install MongoDB**

### **🍎 macOS (Homebrew)**

```bash
# Install MongoDB Community Edition
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb/brew/mongodb-community

# Verify installation
mongod --version
```

### **🐧 Linux (Ubuntu/Debian)**

```bash
# Update package database
sudo apt update

# Install MongoDB
sudo apt install -y mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Verify installation
mongo --version
```

### **🪟 Windows**

1. **Download MongoDB Community Server:**
   - Visit: [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Download the Windows installer (.msi)

2. **Run the installer:**
   - Choose "Complete" installation
   - Install as a Windows Service (recommended)
   - Install MongoDB Compass (optional GUI)

3. **Verify installation:**
   ```cmd
   mongod --version
   ```

### **🐳 Docker (All Platforms)**

```bash
# Run MongoDB in Docker container
docker run -d \
  --name card-collector-mongo \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:latest

# Verify container is running
docker ps | grep mongo
```

### **☁️ MongoDB Atlas (Cloud)**

1. **Sign up for free:** [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create a free cluster** (M0 tier)
3. **Get connection string:** `mongodb+srv://username:password@cluster.mongodb.net/card_collector`
4. **Add to .env file:** `MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/`

---

## 🔧 **Step 2: Install Python Dependencies**

```bash
# Install MongoDB dependencies
pip install motor>=3.3.0 pymongo>=4.6.0 beanie>=1.24.0

# Or use requirements.txt (already includes MongoDB deps)
pip install -r requirements.txt
```

---

## ⚙️ **Step 3: Configure Environment Variables**

### **Update .env File**

```env
# ===== DATABASE CONFIGURATION =====
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=card_collector

# For MongoDB Atlas (cloud)
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

# Legacy SQL database settings (keep for fallback)
DATABASE_URL=sqlite+aiosqlite:///./card_collector.db
```

### **Environment Variables Explained**

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_TYPE` | Database engine to use | `mongodb` |
| `MONGODB_URL` | MongoDB connection URL | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `card_collector` |

---

## 🧪 **Step 4: Test MongoDB Connection**

### **Test Connection Script**

```bash
# Test MongoDB connection
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
client.admin.command('ping')
print('✅ MongoDB connection successful!')
client.close()
"
```

### **Test Web Application**

```bash
# Start the application
python run.py

# Check health endpoint
curl http://localhost:8080/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "service": "card-collector-web", 
  "database": {
    "status": "healthy",
    "database_name": "card_collector"
  },
  "database_type": "mongodb"
}
```

---

## 🚀 **Step 5: Run the Application**

### **Start the Application**

```bash
# Development mode with MongoDB
python run.py

# Production mode 
python start.py
```

### **Verify Everything Works**

1. **Web Interface:** http://localhost:8080
2. **API Health:** http://localhost:8080/api/health
3. **API Docs:** http://localhost:8080/docs
4. **Discord Bot:** Test slash commands in Discord

---

## 📊 **Database Features with MongoDB**

### **Enhanced Querying**

MongoDB provides powerful querying capabilities:

```python
# Text search across cards
cards = await Card.find(
    Card.name.contains("dragon", ignore_case=True)
).to_list()

# Complex filtering
epic_cards = await Card.find(
    And(
        Card.rarity == CardRarity.EPIC,
        Card.status == CardStatus.APPROVED,
        In("fantasy", Card.tags)
    )
).to_list()

# Aggregation pipelines for statistics
pipeline = [
    {"$group": {"_id": "$rarity", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
```

### **Flexible Schema**

Add new fields without migrations:

```python
# Add new fields dynamically
card.custom_properties = {"artist": "John Doe", "series": "Fantasy Pack"}
await card.save()
```

### **Performance Benefits**

- **Indexing:** Automatic index creation for better query performance
- **Aggregation:** Built-in aggregation framework for complex analytics
- **Scaling:** Horizontal scaling with sharding (for large deployments)

---

## 🔄 **Migration from SQLite**

### **Export SQLite Data**

```bash
# Export your existing SQLite data (if you have any)
python scripts/export_sqlite.py > cards_backup.json
```

### **Import to MongoDB**

```bash
# Import data to MongoDB (future feature)
python scripts/import_to_mongodb.py cards_backup.json
```

**Note:** Automatic migration tools will be added in future versions.

---

## 🛠️ **MongoDB Management Tools**

### **MongoDB Compass (GUI)**

- **Download:** [MongoDB Compass](https://www.mongodb.com/products/compass)
- **Connect to:** `mongodb://localhost:27017`
- **Browse collections:** cards, card_instances, users, guild_configs

### **Command Line Interface**

```bash
# Connect to MongoDB shell
mongo mongodb://localhost:27017/card_collector

# Show collections
show collections

# Query cards
db.cards.find().limit(5)

# Count documents
db.cards.countDocuments()
```

### **MongoDB Atlas (Cloud Management)**

If using MongoDB Atlas:
- **Dashboard:** Monitor performance, storage usage
- **Alerting:** Set up alerts for performance issues
- **Backup:** Automatic backups and point-in-time recovery

---

## 🆘 **Troubleshooting**

### **Common Issues**

**❌ "MongoServerError: Authentication failed"**
```bash
# Solution: Check connection string and credentials
# For local MongoDB (no auth by default):
MONGODB_URL=mongodb://localhost:27017

# For Atlas:
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
```

**❌ "pymongo.errors.ServerSelectionTimeoutError"**
```bash
# Solution: Check if MongoDB is running
# macOS:
brew services start mongodb/brew/mongodb-community

# Linux:
sudo systemctl start mongodb

# Docker:
docker start card-collector-mongo
```

**❌ "beanie.exceptions.CollectionWasNotInitialized"**
```bash
# Solution: Ensure database initialization in your code
await init_database()
```

**❌ "Connection refused on port 27017"**
```bash
# Check if MongoDB is running
netstat -an | grep 27017

# For Docker:
docker ps | grep mongo

# Check MongoDB logs:
tail -f /var/log/mongodb/mongod.log  # Linux
tail -f /usr/local/var/log/mongodb/mongo.log  # macOS
```

### **Performance Optimization**

**Enable Profiling:**
```javascript
// In MongoDB shell
db.setProfilingLevel(2)  // Profile all operations
db.system.profile.find().limit(5).sort({ts:-1}).pretty()
```

**Index Management:**
```bash
# Check existing indexes
db.cards.getIndexes()

# Create custom indexes for better performance
db.cards.createIndex({"name": "text", "description": "text"})
```

---

## 🌐 **Production Deployment with MongoDB**

### **Update Deployment Configurations**

**docker-compose.yml:**
```yaml
services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=card_collector
    restart: unless-stopped

  web:
    build: .
    environment:
      - DATABASE_TYPE=mongodb
      - MONGODB_URL=mongodb://mongodb:27017
      - MONGODB_DATABASE=card_collector
    depends_on:
      - mongodb

volumes:
  mongodb_data:
```

**Render.com:**
```env
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=card_collector
```

**Heroku:**
```bash
# Add MongoDB Atlas add-on
heroku addons:create mongolab:sandbox

# Or set custom MongoDB URL
heroku config:set DATABASE_TYPE=mongodb
heroku config:set MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
```

---

## 📈 **Monitoring & Maintenance**

### **Health Checks**

The application includes built-in MongoDB health checks:

```bash
# Check application health
curl http://localhost:8080/api/health

# Response includes database status:
{
  "database": {
    "status": "healthy",
    "collections_count": 6,
    "data_size": 15360,
    "storage_size": 32768
  }
}
```

### **Backup Strategies**

**Local Backups:**
```bash
# Create backup
mongodump --db card_collector --out ./backups/

# Restore backup  
mongorestore --db card_collector ./backups/card_collector/
```

**MongoDB Atlas:**
- Automatic backups enabled by default
- Point-in-time recovery available
- Download backups via Atlas dashboard

---

## 🎉 **Success!**

Once setup is complete, you'll have:

- ✅ **MongoDB database** running locally or in the cloud
- ✅ **Python dependencies** installed and working  
- ✅ **Card Collector application** using MongoDB
- ✅ **Enhanced performance** for large card collections
- ✅ **Flexible schema** for future feature additions
- ✅ **Production-ready** configuration

Your Card Collector now uses MongoDB for better scalability and performance! 🍃

---

**Need Help?**

- 📖 **MongoDB Documentation:** [docs.mongodb.com](https://docs.mongodb.com/)
- 🐛 **Report Issues:** [GitHub Issues](https://github.com/LukeOsland1/card-collector/issues)
- 💬 **MongoDB Community:** [community.mongodb.com](https://community.mongodb.com/)

**Made with ❤️ for Discord communities worldwide**

🤖 **Generated with [Claude Code](https://claude.ai/code)**