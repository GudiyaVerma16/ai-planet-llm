@echo off
echo 🔧 Installing AI Planet Dependencies...
echo.

REM Install Backend Dependencies
echo 📦 Installing Backend Dependencies (Python)...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Backend dependencies installed!
cd ..

REM Install Frontend Dependencies
echo.
echo 📦 Installing Frontend Dependencies (Node.js)...
cd frontend
if not exist node_modules (
    call npm install
    echo ✅ Frontend dependencies installed!
) else (
    echo ✅ Frontend dependencies already installed!
)
cd ..

echo.
echo 🎉 All dependencies installed successfully!
echo.
echo Next steps:
echo 1. Copy backend\.env.example to backend\.env
echo 2. Add your API keys to backend\.env
echo 3. Start PostgreSQL (or use Docker)
echo 4. Run backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo 5. Run frontend: cd frontend ^&^& npm run dev
