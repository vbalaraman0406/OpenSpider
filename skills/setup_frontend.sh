#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend

echo '=== NODE VERSION ==='
node --version
echo '=== NPM VERSION ==='
npm --version

echo ''
echo '=== INSTALLING FRONTEND DEPS ==='
npm install 2>&1 | tail -15
echo ''
echo 'NPM INSTALL EXIT CODE:' $?

# Kill any existing process on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
sleep 1

# Start dev server in background
echo ''
echo '=== STARTING FRONTEND DEV SERVER ==='
nohup npm run dev > /tmp/frontend_server.log 2>&1 &
echo "Frontend PID: $!"
sleep 5

echo ''
echo '=== FRONTEND SERVER LOG ==='
cat /tmp/frontend_server.log 2>/dev/null
echo ''
echo '=== CHECK PORT 5173 ==='
lsof -i:5173 2>/dev/null
echo ''
echo '=== CHECK PORT 3000 ==='
lsof -i:3000 2>/dev/null
echo ''
echo '=== FRONTEND HEALTH CHECK ==='
curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/ 2>/dev/null
echo ''