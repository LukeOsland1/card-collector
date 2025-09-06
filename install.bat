@echo off
title Card Collector - One-Click Installer
echo ========================================
echo   Card Collector - One-Click Install
echo ========================================
echo.
echo This will automatically:
echo - Check Python installation
echo - Install all dependencies
echo - Set up configuration
echo - Create necessary directories
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Run setup
call setup.bat
if errorlevel 1 (
    echo Setup failed. Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo      INSTALLATION COMPLETED!
echo ========================================
echo.
echo Quick Start:
echo.
echo 1. Edit your bot token:
echo    - Run: config.bat
echo    - Or edit .env file manually
echo.
echo 2. Start the application:
echo    - Run: start.bat (production)
echo    - Or: dev.bat (development)
echo.
echo 3. Discord Setup:
echo    - Invite your bot to your Discord server
echo    - Use /card commands to get started
echo.
echo 4. Web Interface:
echo    - Visit: http://localhost:8080
echo    - API docs: http://localhost:8080/docs
echo.
echo ========================================
echo       NEED YOUR DISCORD BOT TOKEN
echo ========================================
echo.
echo To get your Discord bot token:
echo 1. Go to https://discord.com/developers/applications
echo 2. Create a new application or select existing one
echo 3. Go to "Bot" section in left sidebar
echo 4. Click "Reset Token" to reveal your token
echo 5. Copy the token and run config.bat to set it up
echo.
echo Bot Permissions Needed:
echo - Send Messages
echo - Use Slash Commands
echo - Embed Links
echo - Attach Files
echo - Read Message History
echo.
echo Invite URL Generator:
echo https://discord.com/developers/applications/[YOUR_APP_ID]/oauth2/url-generator
echo.

choice /C YN /M "Do you want to open the configuration helper now"
if errorlevel 2 goto end
if errorlevel 1 call config.bat

:end
echo.
echo Installation complete! You're ready to go.
echo.
pause