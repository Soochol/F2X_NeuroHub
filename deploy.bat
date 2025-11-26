@echo off
REM =============================================================================
REM F2X NeuroHub MES - Windows Server Deployment Script
REM Usage: deploy.bat [command]
REM Commands: start, stop, restart, logs, status, migrate, build, deploy, clean, help
REM =============================================================================

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.prod.yml
set ENV_FILE=.env.production

REM Colors are not well supported in cmd, using simple prefixes
set INFO=[INFO]
set WARN=[WARN]
set ERROR=[ERROR]

REM Check command argument
if "%1"=="" goto help
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="build" goto build
if "%1"=="deploy" goto deploy
if "%1"=="migrate" goto migrate
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean
if "%1"=="help" goto help
goto help

REM =============================================================================
REM Check if .env.production exists
REM =============================================================================
:check_env
if not exist "%ENV_FILE%" (
    echo %ERROR% .env.production file not found!
    echo %INFO% Copy .env.production.example to .env.production and update values
    echo        copy .env.production.example .env.production
    exit /b 1
)
exit /b 0

REM =============================================================================
REM Build Docker images
REM =============================================================================
:build
echo %INFO% Building Docker images...
docker-compose -f %COMPOSE_FILE% build
if %errorlevel% neq 0 (
    echo %ERROR% Build failed!
    exit /b 1
)
echo %INFO% Build completed!
goto end

REM =============================================================================
REM Start services
REM =============================================================================
:start
call :check_env
if %errorlevel% neq 0 exit /b 1

echo %INFO% Starting F2X NeuroHub MES...
docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% up -d
if %errorlevel% neq 0 (
    echo %ERROR% Failed to start services!
    exit /b 1
)
echo %INFO% Services started!
echo %INFO% Access the application at http://localhost
goto end

REM =============================================================================
REM Stop services
REM =============================================================================
:stop
echo %INFO% Stopping F2X NeuroHub MES...
docker-compose -f %COMPOSE_FILE% down
echo %INFO% Services stopped!
goto end

REM =============================================================================
REM Restart services
REM =============================================================================
:restart
call :stop
call :start
goto end

REM =============================================================================
REM Show logs
REM =============================================================================
:logs
if "%2"=="" (
    echo %INFO% Showing all logs (Ctrl+C to exit)...
    docker-compose -f %COMPOSE_FILE% logs -f
) else (
    echo %INFO% Showing logs for %2 (Ctrl+C to exit)...
    docker-compose -f %COMPOSE_FILE% logs -f %2
)
goto end

REM =============================================================================
REM Show status
REM =============================================================================
:status
echo %INFO% Service Status:
echo.
docker-compose -f %COMPOSE_FILE% ps
goto end

REM =============================================================================
REM Run database migrations
REM =============================================================================
:migrate
echo %INFO% Running database migrations...
docker-compose -f %COMPOSE_FILE% exec backend alembic upgrade head
if %errorlevel% neq 0 (
    echo %ERROR% Migration failed!
    exit /b 1
)
echo %INFO% Migrations completed!
goto end

REM =============================================================================
REM Full deployment (build + start + migrate)
REM =============================================================================
:deploy
call :check_env
if %errorlevel% neq 0 exit /b 1

echo %INFO% Starting full deployment...
call :build
if %errorlevel% neq 0 exit /b 1

call :start
if %errorlevel% neq 0 exit /b 1

echo %INFO% Waiting for services to be ready...
timeout /t 15 /nobreak > nul

call :migrate
if %errorlevel% neq 0 (
    echo %WARN% Migration failed, but services are running.
    echo %INFO% You may need to run 'deploy.bat migrate' manually.
)

echo.
echo %INFO% Deployment completed!
call :status
goto end

REM =============================================================================
REM Clean up (remove containers, networks, volumes)
REM =============================================================================
:clean
echo %WARN% This will remove all containers, networks, and volumes!
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    docker-compose -f %COMPOSE_FILE% down -v --rmi local
    echo %INFO% Cleanup completed!
) else (
    echo %INFO% Cleanup cancelled.
)
goto end

REM =============================================================================
REM Help
REM =============================================================================
:help
echo.
echo F2X NeuroHub MES - Windows Server Deployment Script
echo.
echo Usage: deploy.bat [command]
echo.
echo Commands:
echo   start     - Start all services
echo   stop      - Stop all services
echo   restart   - Restart all services
echo   build     - Build Docker images
echo   deploy    - Full deployment (build + start + migrate)
echo   migrate   - Run database migrations
echo   logs      - Show logs (optionally specify service: logs backend)
echo   status    - Show service status
echo   clean     - Remove all containers and volumes (WARNING: data loss)
echo   help      - Show this help
echo.
echo Examples:
echo   deploy.bat start          - Start the application
echo   deploy.bat logs backend   - Show backend logs only
echo   deploy.bat deploy         - Full deployment from scratch
echo.
goto end

:end
endlocal
