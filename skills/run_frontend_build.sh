#!/bin/bash
FRONTEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend

echo '=== FRONTEND BUILD TEST ==='
cd $FRONTEND
npm run build 2>&1
echo ''
echo 'BUILD_EXIT:' $?

echo ''
echo '=== FRONTEND SERVER STATUS ==='
curl -s -o /dev/null -w 'HTTP_CODE: %{http_code}' http://localhost:3000/ 2>/dev/null
echo ''

echo ''
echo '=== BACKEND SERVER STATUS ==='
curl -s http://localhost:8000/health 2>/dev/null
echo ''
curl -s http://localhost:8000/ 2>/dev/null
echo ''