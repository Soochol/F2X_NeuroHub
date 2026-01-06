@echo off
chcp 65001 >nul
echo ========================================
echo   F2X Station Service - Update and Run
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] Updating from GitHub...
git pull origin main
if errorlevel 1 (
    echo ERROR: git pull failed
    pause
    exit /b 1
)

echo.
echo [2/3] Installing dependencies...
call .venv\Scripts\activate.bat
pip install -e . --quiet
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Station Service...
echo Press Ctrl+C to stop
python -m station_service.main
pause
