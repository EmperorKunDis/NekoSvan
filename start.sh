#!/bin/bash
# NekoSvan CRM - Start script for praut.cz/app integration
# Backend: 13666, Frontend: 12666

set -e

cd "$(dirname "$0")"

echo "🚀 Starting NekoSvan CRM..."
echo "   Backend:  http://localhost:13666"
echo "   Frontend: http://localhost:12666"
echo ""

# Kill existing processes
pkill -f "manage.py runserver.*13666" 2>/dev/null || true
pkill -f "ng serve.*12666" 2>/dev/null || true
sleep 1

# Start Django backend
echo "Starting Django backend on port 13666..."
source venv/bin/activate
python manage.py runserver 0.0.0.0:13666 > /tmp/nekosvan-backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend
sleep 3

# Start Angular frontend
echo "Starting Angular frontend on port 12666..."
cd frontend
npx ng serve --host 0.0.0.0 --port 12666 --proxy-config proxy.conf.json > /tmp/nekosvan-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ NekoSvan CRM is starting..."
echo "   Frontend: http://localhost:12666"
echo "   Backend API: http://localhost:13666/api/v1/"
echo ""
echo "Logs:"
echo "   Backend:  tail -f /tmp/nekosvan-backend.log"
echo "   Frontend: tail -f /tmp/nekosvan-frontend.log"
echo ""
echo "To stop: pkill -f 'manage.py runserver.*13666' && pkill -f 'ng serve.*12666'"

# Wait for frontend to be ready
sleep 10
echo ""
echo "🎉 Ready! Open http://localhost:12666"
