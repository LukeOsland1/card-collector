#!/usr/bin/env python3
"""
Interactive Discord bot token configuration script
"""
import os
import sys
from pathlib import Path

def configure_discord_token():
    """Interactive setup for Discord bot token."""
    print("=" * 50)
    print("   Discord Bot Token Configuration")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Creating .env file...")
        
        # Copy from env.example if it exists
        example_file = Path("env.example")
        if example_file.exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ Copied env.example to .env")
        else:
            # Create basic .env file
            with open(".env", "w") as f:
                f.write("""# Card Collector - Environment Configuration

# ===== REQUIRED SETTINGS =====
DISCORD_BOT_TOKEN=your_bot_token_here
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this

# ===== DATABASE =====
DATABASE_URL=sqlite+aiosqlite:///./card_collector.db

# ===== WEB SERVER =====
WEB_HOST=0.0.0.0
WEB_PORT=8080
""")
            print("✅ Created basic .env file")
    
    print("\n📋 How to get your Discord bot token:")
    print("1. Go to: https://discord.com/developers/applications")
    print("2. Click 'New Application' or select existing one")
    print("3. Give it a name (e.g., 'My Card Collector')")
    print("4. Go to 'Bot' section in left sidebar")
    print("5. Click 'Add Bot' if not already created")
    print("6. Under 'Token', click 'Copy'")
    print()
    
    # Get current token
    try:
        with open(".env", "r") as f:
            content = f.read()
            current_token = ""
            for line in content.split("\n"):
                if line.startswith("DISCORD_BOT_TOKEN="):
                    current_token = line.split("=", 1)[1]
                    break
        
        if current_token and not current_token.startswith(("your_", "test_", "placeholder_")):
            print(f"📝 Current token: {current_token[:20]}...{current_token[-10:]}")
            print("   (showing first 20 and last 10 characters)")
            print()
            replace = input("Do you want to replace this token? (y/N): ").lower()
            if replace != 'y':
                print("✅ Keeping current token")
                return
    except Exception as e:
        print(f"⚠️  Could not read current token: {e}")
    
    # Get new token
    print("\n🔑 Please paste your Discord bot token:")
    print("   (it will be hidden as you type)")
    
    try:
        import getpass
        token = getpass.getpass("Token: ").strip()
    except Exception:
        # Fallback if getpass doesn't work
        token = input("Token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return
    
    # Basic validation
    if token.startswith(("your_", "test_", "placeholder_", "example_")):
        print("❌ That looks like a placeholder token, not a real one")
        print("   Please get your actual bot token from Discord Developer Portal")
        return
    
    if len(token) < 50:
        print("⚠️  Token seems short. Discord bot tokens are usually 70+ characters")
        proceed = input("Continue anyway? (y/N): ").lower()
        if proceed != 'y':
            return
    
    # Update .env file
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        # Replace token line
        lines = content.split("\n")
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("DISCORD_BOT_TOKEN="):
                lines[i] = f"DISCORD_BOT_TOKEN={token}"
                updated = True
                break
        
        if not updated:
            lines.append(f"DISCORD_BOT_TOKEN={token}")
        
        with open(".env", "w") as f:
            f.write("\n".join(lines))
        
        print("\n✅ Discord bot token updated successfully!")
        print("\n🚀 Next steps:")
        print("1. Invite your bot to a Discord server:")
        print("   - Go back to Discord Developer Portal")
        print("   - OAuth2 → URL Generator")
        print("   - Select 'bot' and 'applications.commands'")
        print("   - Copy URL and visit it to invite bot")
        print()
        print("2. Test the application:")
        print("   python3 run.py")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    if not Path("requirements.txt").exists():
        print("❌ Error: Not in Card Collector directory")
        print("Please run this script from the card-collector folder")
        sys.exit(1)
    
    configure_discord_token()