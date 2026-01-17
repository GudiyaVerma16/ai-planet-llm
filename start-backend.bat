@echo off
echo 🚀 Starting Backend Server...
echo.

cd backend

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found! Creating from .env.example...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit backend\.env and add your API keys before starting!
    echo.
    pause
)

echo ✅ Starting FastAPI server on http://localhost:8000
echo 📚 API Documentation will be available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
