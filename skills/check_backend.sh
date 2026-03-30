#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend
source venv/bin/activate

echo '=== SERVER LOG ==='
cat /tmp/backend_server.log 2>/dev/null
echo ''
echo '=== CHECK PORT 8000 ==='
lsof -i:8000 2>/dev/null
echo ''
echo '=== HEALTH CHECK (root) ==='
curl -s http://localhost:8000/ 2>/dev/null
echo ''
echo '=== HEALTH CHECK (/health) ==='
curl -s http://localhost:8000/health 2>/dev/null
echo ''
echo '=== HEALTH CHECK (/api/health) ==='
curl -s http://localhost:8000/api/health 2>/dev/null
echo ''