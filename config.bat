@echo off
title Card Collector - Configuration Helper
echo ========================================
echo   Card Collector - Configuration
echo ========================================
echo.

if not exist ".env" (
    echo Creating .env file from template...
    copy env.example .env >nul
)

echo Opening .env file for editing...
echo.
echo ========================================
echo        CONFIGURATION GUIDE
echo ========================================
echo.
echo Required settings:
echo.
echo 1. DISCORD_BOT_TOKEN
echo    - Get this from https://discord.com/developers/applications
echo    - Create a new application, go to "Bot" section
echo    - Copy the token and paste it in .env
echo.
echo 2. JWT_SECRET_KEY
echo    - Change this to a random secret string
echo    - Example: my-super-secret-key-12345
echo.
echo Optional settings:
echo.
echo 3. DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET
echo    - For web login functionality
echo    - Get from OAuth2 section in Discord Developer Portal
echo.
echo 4. DATABASE_URL
echo    - Default SQLite is fine for most users
echo    - Use PostgreSQL for production
echo.
echo The .env file will open in Notepad when you press any key.
echo Save and close Notepad when you're done editing.
echo.
pause

REM Open .env file in default editor
notepad .env

echo.
echo Configuration updated!
echo.
echo To verify your settings, you can:
echo - Run dev.bat to test in development mode
echo - Run start.bat for full production mode
echo.
pause