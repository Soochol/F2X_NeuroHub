@echo off
chcp 65001 >nul
echo ========================================
echo   F2X Station 1 - Update and Run
echo   Port: 8080
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
echo [3/3] Starting Station 1...
echo Press Ctrl+C to stop
set STATION_CONFIG=./config/station1.yaml
python -m station_service.main
pause
