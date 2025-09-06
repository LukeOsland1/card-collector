@echo off
echo ========================================
echo    Card Collector - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/6] Python detected - OK
echo.

REM Check if we're in a virtual environment, if not create one
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/6] Virtual environment exists - OK
)

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [4/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Setup environment file if it doesn't exist
if not exist ".env" (
    echo [5/6] Setting up environment configuration...
    copy env.example .env
    echo.
    echo ========================================
    echo    IMPORTANT: CONFIGURATION REQUIRED
    echo ========================================
    echo A .env file has been created for you.
    echo You MUST edit it with your Discord bot token before running.
    echo.
    echo Required settings:
    echo - DISCORD_BOT_TOKEN=your_bot_token_here
    echo - JWT_SECRET_KEY=your-secret-key
    echo.
    echo Optional but recommended:
    echo - DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET for web login
    echo.
    pause
) else (
    echo [5/6] Environment file exists - OK
)

REM Create directories
echo [6/6] Creating directories...
if not exist "logs" mkdir logs
if not exist "storage" mkdir storage
if not exist "storage\images" mkdir storage\images
if not exist "storage\thumbnails" mkdir storage\thumbnails
if not exist "storage\previews" mkdir storage\previews
if not exist "storage\cards" mkdir storage\cards
if not exist "storage\temp" mkdir storage\temp

echo.
echo ========================================
echo        SETUP COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Discord bot token
echo 2. Run: start.bat (full features) or dev.bat (development)
echo.
echo Need help? Check README.md or the GitHub repository
echo.
pause