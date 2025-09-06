@echo off
title Card Collector - Production Server
echo ========================================
echo   Card Collector - Starting Production
echo ========================================
echo.

REM Check if setup was run
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

if not exist ".env" (
    echo ERROR: .env file not found
    echo Please run setup.bat first and configure your .env file
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Discord token is configured
findstr /C:"your_bot_token_here" .env >nul
if not errorlevel 1 (
    echo.
    echo ========================================
    echo           CONFIGURATION ERROR
    echo ========================================
    echo Your .env file still contains placeholder values.
    echo Please edit .env and set your Discord bot token:
    echo.
    echo DISCORD_BOT_TOKEN=your_actual_bot_token
    echo JWT_SECRET_KEY=your_secret_key
    echo.
    echo Get your bot token from: https://discord.com/developers/applications
    echo.
    pause
    exit /b 1
)

echo Starting Card Collector...
echo.
echo ========================================
echo Services will start on:
echo - Discord Bot: Connected to your server
echo - Web Interface: http://localhost:8080
echo - API Documentation: http://localhost:8080/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python start.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo            ERROR OCCURRED
    echo ========================================
    echo The application failed to start.
    echo Check the error messages above.
    echo.
    echo Common issues:
    echo - Invalid Discord bot token
    echo - Missing dependencies (run setup.bat again)
    echo - Port 8080 already in use
    echo.
    pause
)

echo.
echo Card Collector stopped.
pause