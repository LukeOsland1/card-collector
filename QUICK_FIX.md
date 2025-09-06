# Quick Fix for Greenlet Error

If you're getting this error:
```
ERROR: Database initialization failed: the greenlet library is required to use this function. No module named 'greenlet'
```

## 🚀 Quick Solution

Run one of these commands:

### Option 1: Auto-install all dependencies
```bash
python3 install_deps.py
```

### Option 2: Manual install
```bash
pip3 install greenlet aiosqlite
# OR install all at once:
pip3 install -r requirements.txt
```

### Option 3: Check what's missing
```bash
python3 check_deps.py
```

## ✅ Verify Fix

After installation, test with:
```bash
python3 run.py
```

You should see:
```
INFO:__main__:Starting Card Collector in development mode...
INFO:__main__:Initializing database...
INFO:__main__:Database initialized  ✅
```

## 🔧 If Still Not Working

1. **Check Python version**: `python3 --version` (need 3.9+)
2. **Check pip**: `pip3 --version` 
3. **Manual install**: `pip3 install greenlet==3.2.4`
4. **Virtual environment**: Make sure you're in the right environment

## 📞 Need More Help?

- Run: `python3 check_deps.py` to see all missing dependencies
- Check: [GitHub Issues](https://github.com/LukeOsland1/card-collector/issues)