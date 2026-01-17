@echo off
echo 🚀 Starting AI Planet Application...
echo.

REM Check if Docker is available
where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Docker found! Using Docker Compose...
    echo.
    docker-compose up --build
) else (
    echo ❌ Docker not found!
    echo.
    echo Please use one of these options:
    echo 1. Install Docker and run: docker-compose up --build
    echo 2. Run start-backend.bat in one terminal
    echo 3. Run start-frontend.bat in another terminal
    echo.
    pause
)
