#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend
source venv/bin/activate

# Kill any existing uvicorn on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# Read all router files to understand endpoints
echo '=== ALL ROUTER FILES ==='
for f in routers/*.py; do
  echo "--- $f ---"
  cat "$f"
  echo ''
done

echo '=== MAIN.PY FULL ==='
cat main.py

# Start uvicorn in background
echo ''
echo '=== STARTING BACKEND SERVER ==='
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend_server.log 2>&1 &
echo "Backend PID: $!"
sleep 3

# Check if running
echo '=== HEALTH CHECK ==='
curl -s http://localhost:8000/api/health 2>/dev/null
echo ''
echo '=== SERVER LOG ==='
cat /tmp/backend_server.log 2>/dev/null