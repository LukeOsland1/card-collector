@echo off
title Card Collector - Update & Maintenance
echo ========================================
echo   Card Collector - Update System
echo ========================================
echo.

if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo What would you like to do?
echo.
echo 1. Update dependencies
echo 2. Reset database
echo 3. Clean up files
echo 4. Backup data
echo 5. Check system health
echo 6. View logs
echo 0. Exit
echo.

set /p choice="Enter your choice (0-6): "

if "%choice%"=="0" goto end
if "%choice%"=="1" goto update_deps
if "%choice%"=="2" goto reset_db
if "%choice%"=="3" goto cleanup
if "%choice%"=="4" goto backup
if "%choice%"=="5" goto health_check
if "%choice%"=="6" goto view_logs

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:update_deps
echo.
echo ========================================
echo     UPDATING DEPENDENCIES
echo ========================================
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install --upgrade -r requirements.txt
echo Dependencies updated successfully!
goto menu

:reset_db
echo.
echo ========================================
echo       RESET DATABASE
echo ========================================
echo WARNING: This will delete all your data!
echo.
choice /C YN /M "Are you sure you want to continue"
if errorlevel 2 goto menu

if exist "card_collector.db" (
    del card_collector.db
    echo Database file deleted.
)
if exist "db\migrations\versions\*.py" (
    del /q db\migrations\versions\*.py
    echo Migration files cleared.
)
echo Database reset complete. Run the application to recreate it.
goto menu

:cleanup
echo.
echo ========================================
echo       CLEANUP FILES
echo ========================================
echo Cleaning temporary files...

if exist "storage\temp\*.*" (
    del /q storage\temp\*.*
    echo Temporary files cleaned.
)
if exist "logs\*.log.old" (
    del /q logs\*.log.old
    echo Old log files cleaned.
)
if exist "__pycache__" (
    rmdir /s /q __pycache__
    echo Python cache cleaned.
)

for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Cleanup complete!
goto menu

:backup
echo.
echo ========================================
echo        BACKUP DATA
echo ========================================
set backup_name=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

echo Creating backup: %backup_name%

if not exist "backups" mkdir backups

if exist "card_collector.db" (
    copy card_collector.db backups\%backup_name%_database.db >nul
    echo Database backed up.
)
if exist "storage" (
    xcopy storage backups\%backup_name%_storage\ /e /i /q >nul
    echo Storage files backed up.
)
if exist ".env" (
    copy .env backups\%backup_name%_config.env >nul
    echo Configuration backed up.
)

echo Backup created successfully in backups\ folder!
goto menu

:health_check
echo.
echo ========================================
echo      SYSTEM HEALTH CHECK
echo ========================================

call venv\Scripts\activate.bat

echo Checking Python environment...
python --version

echo.
echo Checking required packages...
python -c "import discord; print('✅ Discord.py:', discord.__version__)" 2>nul || echo "❌ Discord.py not found"
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>nul || echo "❌ FastAPI not found"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)" 2>nul || echo "❌ SQLAlchemy not found"
python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>nul || echo "❌ Pillow not found"

echo.
echo Checking configuration...
if exist ".env" (
    echo ✅ .env file exists
    findstr /C:"your_bot_token_here" .env >nul
    if errorlevel 1 (
        echo ✅ Bot token appears to be configured
    ) else (
        echo ❌ Bot token not configured
    )
) else (
    echo ❌ .env file missing
)

echo.
echo Checking directories...
if exist "storage" (echo ✅ Storage directory exists) else (echo ❌ Storage directory missing)
if exist "logs" (echo ✅ Logs directory exists) else (echo ❌ Logs directory missing)

echo.
echo Health check complete!
goto menu

:view_logs
echo.
echo ========================================
echo        VIEW RECENT LOGS
echo ========================================

if exist "logs\card-collector.log" (
    echo Last 50 lines of main log:
    echo.
    powershell "Get-Content 'logs\card-collector.log' | Select-Object -Last 50"
) else (
    echo No log file found. Run the application first to generate logs.
)

echo.
pause
goto menu

:menu
echo.
echo ========================================
echo   Card Collector - Update System
echo ========================================
echo.

echo What would you like to do?
echo.
echo 1. Update dependencies
echo 2. Reset database
echo 3. Clean up files
echo 4. Backup data
echo 5. Check system health
echo 6. View logs
echo 0. Exit
echo.

set /p choice="Enter your choice (0-6): "

if "%choice%"=="0" goto end
if "%choice%"=="1" goto update_deps
if "%choice%"=="2" goto reset_db
if "%choice%"=="3" goto cleanup
if "%choice%"=="4" goto backup
if "%choice%"=="5" goto health_check
if "%choice%"=="6" goto view_logs

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:end
echo.
echo Thanks for using Card Collector!
timeout /t 2 >nul