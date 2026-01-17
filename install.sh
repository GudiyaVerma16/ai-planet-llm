#!/bin/bash

echo "🔧 Installing AI Planet Dependencies..."
echo ""

# Install Backend Dependencies
echo "📦 Installing Backend Dependencies (Python)..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend dependencies installed!"
cd ..

# Install Frontend Dependencies
echo ""
echo "📦 Installing Frontend Dependencies (Node.js)..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Frontend dependencies installed!"
else
    echo "✅ Frontend dependencies already installed!"
fi
cd ..

echo ""
echo "🎉 All dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy backend/.env.example to backend/.env"
echo "2. Add your API keys to backend/.env"
echo "3. Start PostgreSQL (or use Docker)"
echo "4. Run backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Run frontend: cd frontend && npm run dev"
