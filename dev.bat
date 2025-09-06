@echo off
title Card Collector - Development Server
echo ========================================
echo   Card Collector - Development Mode
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
    echo WARNING: .env file contains placeholder values
    echo You should edit .env with your Discord bot token for full functionality
    echo.
    echo Continuing in development mode...
    timeout /t 3 >nul
)

echo Starting Card Collector in development mode...
echo.
echo ========================================
echo Development Features:
echo - Auto-reload on code changes
echo - Detailed debug logging
echo - SQLite database (lightweight)
echo - Local file storage
echo ========================================
echo.
echo Services:
echo - Web Interface: http://localhost:8080
echo - API Docs: http://localhost:8080/docs
echo ========================================
echo.
echo Press Ctrl+C to stop
echo.

REM Start in development mode
python run.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo            ERROR OCCURRED
    echo ========================================
    echo The application failed to start.
    echo.
    pause
)

echo.
echo Development server stopped.
pause