# 🍃 MongoDB Database Auto-Setup Guide

## ❓ **Does the app generate the correct MongoDB database automatically?**

**✅ YES!** The Card Collector application automatically creates the MongoDB database and collections when they don't exist.

## 🔄 **How Auto-Setup Works**

### **1. Database Creation**
```python
# MongoDB creates databases automatically on first use
database = mongodb_client[database_name]  # Creates 'card_collector' database
```
- **Lazy Creation**: MongoDB creates databases when the first document is inserted
- **No manual setup required**: Database appears automatically when needed

### **2. Collection Creation**
```python
# Beanie ODM creates collections automatically
await init_beanie(database=database, document_models=[Card, CardInstance, ...])
```
- **Automatic Collections**: Created when first document is inserted into each collection
- **Collections Created**:
  - `cards` - Stores card definitions
  - `card_instances` - Stores user card ownership
  - `users` - Stores Discord user information
  - `guild_configs` - Stores server configurations  
  - `audit_logs` - Stores action history
  - `card_submissions` - Stores pending card submissions

### **3. Index Creation**
```python
# Indexes are created automatically based on model definitions
class Card(Document):
    class Settings:
        indexes = [
            IndexModel([("status", 1), ("rarity", 1)]),
            IndexModel([("created_by_user_id", 1)]),
            IndexModel([("name", "text"), ("description", "text")])
        ]
```
- **Performance Indexes**: Created automatically for optimal query performance
- **Text Search**: Full-text search indexes for card names and descriptions
- **Compound Indexes**: For complex queries across multiple fields

## 🧪 **Testing Auto-Setup**

You can verify the auto-setup process:

```bash
# Test MongoDB database creation
python3 test_mongodb_setup.py

# Setup database with verification  
python3 setup_database.py
```

**Expected Output:**
```
✅ MongoDB connection initialized
✅ Database accessed: card_collector
📋 Collections before: []
✅ Test card created with ID: 64f7b2c8e4b0a1b2c3d4e5f6
📋 Collections after: ['cards']
✅ Card retrieved: Test Card (ID: 64f7b2c8e4b0a1b2c3d4e5f6)
✅ Health check passed
🎉 All tests passed!
```

## 🚀 **What Happens on First Run**

### **Scenario 1: Brand New MongoDB Instance**

```bash
# Start the application
python run.py
```

**Auto-Setup Process:**
1. **Connect** to MongoDB server
2. **Create** `card_collector` database (lazy creation)
3. **Initialize** Beanie ODM
4. **Prepare** collection schemas (no documents yet)
5. **Ready** - Collections created on first document insertion

**Logs You'll See:**
```
INFO: Successfully connected to MongoDB at mongodb://localhost:27017
INFO: Using MongoDB database: card_collector  
INFO: Beanie ODM initialized successfully
INFO: Available collections: []
INFO: Database indexes verified
```

### **Scenario 2: Existing MongoDB with Data**

**Auto-Setup Process:**
1. **Connect** to existing database
2. **Verify** existing collections
3. **Update** indexes if needed
4. **Ready** - Use existing data

**Logs You'll See:**
```
INFO: Successfully connected to MongoDB at mongodb://localhost:27017
INFO: Using MongoDB database: card_collector
INFO: Beanie ODM initialized successfully  
INFO: Available collections: ['cards', 'users', 'guild_configs']
INFO: Database indexes verified
```

## 📊 **First Document Creation**

When the first card, user, or other document is created:

```python
# This automatically creates the 'cards' collection
card = Card(name="My First Card", rarity=CardRarity.COMMON, ...)
await card.insert()  # Collection 'cards' is created here
```

**What Happens:**
1. **Collection Creation**: MongoDB creates the `cards` collection
2. **Index Creation**: All indexes defined in the model are created
3. **Document Insert**: The card document is stored
4. **Ready**: Collection is fully set up and indexed

## 🔍 **Verification Commands**

### **Check Database Status**
```bash
# Health check endpoint
curl http://localhost:8080/api/health

# Response shows database info:
{
  "database": {
    "status": "healthy",
    "database_name": "card_collector",
    "collections_count": 6,
    "data_size": 15360
  }
}
```

### **MongoDB Shell Verification**
```javascript
// Connect to MongoDB shell
mongo mongodb://localhost:27017/card_collector

// Show collections
show collections
// Output: cards, card_instances, users, guild_configs, audit_logs

// Count documents
db.cards.countDocuments()
// Output: 0 (for new database)

// Show indexes
db.cards.getIndexes()
// Output: Shows all auto-created indexes
```

## ⚙️ **Configuration Options**

### **Environment Variables**
```env
# Database auto-creation settings
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=card_collector
```

### **Connection String Variations**
```env
# Local MongoDB
MONGODB_URL=mongodb://localhost:27017

# MongoDB with authentication
MONGODB_URL=mongodb://username:password@localhost:27017

# MongoDB Atlas (cloud)
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/

# MongoDB with options
MONGODB_URL=mongodb://localhost:27017/?authSource=admin&retryWrites=true
```

## 🛠️ **Troubleshooting Auto-Setup**

### **❌ Connection Refused**
```
ERROR: localhost:27017: Connection refused
```
**Solution:** MongoDB server is not running
```bash
# Start MongoDB locally
mongod --dbpath /path/to/data

# Or use Docker
docker run -d -p 27017:27017 mongo

# Or use MongoDB Atlas (cloud)
```

### **❌ Authentication Failed**
```
ERROR: Authentication failed
```
**Solution:** Check credentials in connection string
```env
MONGODB_URL=mongodb://correct_username:correct_password@host:port/
```

### **❌ Database Not Created**
```
INFO: Available collections: []
```
**This is normal!** Collections are created on first document insertion.

To trigger collection creation:
```bash
# Use the Discord bot to create a card
/card create name:"Test Card" rarity:common

# Or use the test script
python3 test_mongodb_setup.py
```

## 🎉 **Summary**

**✅ YES** - The Card Collector app automatically creates:
- ✅ **MongoDB Database** (`card_collector`)
- ✅ **Collections** (cards, users, instances, etc.)
- ✅ **Indexes** (for optimal performance)
- ✅ **Schema Validation** (via Beanie ODM models)

**🔄 Auto-Creation Triggers:**
- Database: Created on first connection
- Collections: Created on first document insertion
- Indexes: Created automatically by Beanie ODM

**📊 No Manual Setup Required:**
- No SQL migrations needed
- No schema files to run
- No manual index creation
- Everything happens automatically!

The MongoDB database setup is **fully automated** and **production-ready**! 🍃

---

**Made with ❤️ for Discord communities worldwide**

🤖 **Generated with [Claude Code](https://claude.ai/code)**