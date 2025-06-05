#!/bin/bash

echo "🚀 SYSTEM STATUS CHECK - POST-OPENHANDS"
echo "=================================================="
echo "Timestamp: $(date)"
echo ""

echo "🔧 PORT CONFIGURATION:"
echo "Frontend (Vite):     Port 12000"
echo "Backend (API):       Port 12001" 
echo "WebSocket:           Port 12001/ws"
echo ""

echo "📡 PORT STATUS:"
if ss -tlnp | grep -q ":12000 "; then
    echo "Frontend  Port 12000: ✅ ACTIVE"
else
    echo "Frontend  Port 12000: ❌ INACTIVE"
fi

if ss -tlnp | grep -q ":12001 "; then
    echo "Backend   Port 12001: ✅ ACTIVE"
else
    echo "Backend   Port 12001: ❌ INACTIVE"
fi

if ss -tlnp | grep -q ":5001 "; then
    echo "Old Frontend 5001:   ⚠️  STILL RUNNING (should be stopped)"
else
    echo "Old Frontend 5001:   ✅ STOPPED"
fi

if ss -tlnp | grep -q ":5002 "; then
    echo "Old Backend  5002:   ⚠️  STILL RUNNING (should be stopped)"
else
    echo "Old Backend  5002:   ✅ STOPPED"
fi

echo ""

echo "🔄 RUNNING PROCESSES:"
if pgrep -f "python.*api_server" > /dev/null; then
    echo "✅ API Server process running"
else
    echo "❌ No API Server process found"
fi

if pgrep -f "vite" > /dev/null; then
    echo "✅ Vite process running"
elif pgrep -f "npm.*dev" > /dev/null; then
    echo "✅ NPM dev process running"
else
    echo "❌ No Vite/NPM dev process found"
fi

echo ""

echo "🚀 QUICK START (if services not running):"
echo "1. Start Backend:  python3 api_server.py"
echo "2. Start Frontend: npm run dev"
echo "3. Open Browser:   http://localhost:12000"
echo ""

echo "⚙️  WHAT OPENHANDS CHANGED:"
echo "- ✅ Ports: 5001/5002 → 12000/12001"
echo "- ✅ Vite proxy updated to use port 12001"
echo "- ✅ WebSocket configuration updated"
echo "- ✅ All changes committed to GitHub"
echo ""

echo "✨ Status check complete!"
echo "Your repository is now synced with the OpenHands changes."
