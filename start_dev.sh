#!/bin/bash

echo "🚀 Starting Rehoboam Development Environment"
echo "============================================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the backend API server
echo "🔧 Starting API server..."
python3 api_server.py &
API_PID=$!

# Wait a bit for the API to start
sleep 3

# Start the frontend development server
echo "🌐 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Rehoboam is starting up!"
echo "📊 Frontend: http://localhost:5173"
echo "🔌 API: http://localhost:5002"
echo ""
echo "🤖 Features enabled:"
echo "   • Real-time price updates"
echo "   • AI-powered trading (Rehoboam)"
echo "   • Interactive UI buttons"
echo "   • Live market sentiment"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
