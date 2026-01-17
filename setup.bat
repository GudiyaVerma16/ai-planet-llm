@echo off
echo 🚀 Setting up AI Planet...

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create backend .env file if it doesn't exist
if not exist backend\.env (
    echo 📝 Creating backend\.env file...
    copy backend\.env.example backend\.env
    echo ⚠️  Please edit backend\.env and add your API keys before starting the application.
)

REM Create uploads directory
if not exist backend\uploads mkdir backend\uploads

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env and add your API keys
echo 2. Run: docker-compose up --build
echo 3. Access the application at http://localhost:3000
