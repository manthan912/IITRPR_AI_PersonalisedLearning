#!/bin/bash

# AI Personalized Learning System - Development Runner
echo "🤖 Starting AI Personalized Learning System"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All dependencies found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
if [ ! -f "venv/lib/python*/site-packages/fastapi/__init__.py" ]; then
    echo "📦 Installing backend dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Setup database if needed
if [ ! -f "learning_system.db" ]; then
    echo "🗄️  Setting up database with sample data..."
    python app/data/sample_data.py
fi

# Install frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "🚀 Starting services..."

# Start backend in background
echo "🔧 Starting backend server..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 System is starting up!"
echo "📍 Services:"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Frontend App: http://localhost:3000"
echo ""
echo "🧪 Demo Accounts:"
echo "   Username: alice_chen (Visual Learner)"
echo "   Username: bob_garcia (Auditory Learner)" 
echo "   Username: carol_smith (Kinesthetic Learner)"
echo "   Password: password123 (for all demo accounts)"
echo ""
echo "💡 Features to Try:"
echo "   • View personalized dashboard with AI insights"
echo "   • Browse learning materials with smart filtering"
echo "   • Track detailed progress and performance analytics"
echo "   • Get AI-powered learning recommendations"
echo "   • Generate personalized learning paths"
echo "   • Update learning style preferences"
echo ""
echo "⏹️  To stop all services: Press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for services (keeps script running)
wait