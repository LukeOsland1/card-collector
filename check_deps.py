#!/usr/bin/env python3
"""
Dependency checker for Card Collector
"""
import sys

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking Card Collector dependencies...")
    print("=" * 50)
    
    dependencies = [
        ("discord.py", "discord"),
        ("fastapi", "fastapi"), 
        ("uvicorn", "uvicorn"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Pydantic", "pydantic"),
        ("python-dotenv", "dotenv"),
        ("aiosqlite", "aiosqlite"),
        ("greenlet", "greenlet"),
        ("Pillow", "PIL"),
        ("httpx", "httpx"),
    ]
    
    missing = []
    installed = []
    
    for name, module in dependencies:
        try:
            __import__(module)
            version = "unknown"
            try:
                mod = __import__(module)
                if hasattr(mod, '__version__'):
                    version = mod.__version__
                elif hasattr(mod, 'VERSION'):
                    version = str(mod.VERSION)
            except:
                pass
            installed.append((name, version))
            print(f"✅ {name:<15} - {version}")
        except ImportError:
            missing.append(name)
            print(f"❌ {name:<15} - NOT INSTALLED")
    
    print("=" * 50)
    print(f"Installed: {len(installed)}")
    print(f"Missing:   {len(missing)}")
    
    if missing:
        print("\nTo install missing dependencies:")
        print("  python3 install_deps.py")
        print("  # OR manually:")
        print("  pip3 install " + " ".join(missing.lower().replace('-', '_') for name in missing))
        return False
    else:
        print("\n🎉 All dependencies are installed!")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)