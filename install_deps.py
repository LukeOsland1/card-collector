#!/usr/bin/env python3
"""
Simple dependency installer for Card Collector
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies."""
    print("Installing Card Collector dependencies...")
    print("This may take a few minutes...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("\nDependencies installed successfully!")
        print("You can now run:")
        print("  python run.py       # Quick start")
        print("  python start.py     # Full features")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nError installing dependencies: {e}")
        print("\nTry manual installation:")
        print("  pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("Error: pip not found. Please install Python with pip.")
        return False

if __name__ == "__main__":
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found")
        print("Make sure you're in the Card Collector directory")
        sys.exit(1)
    
    success = install_dependencies()
    sys.exit(0 if success else 1)