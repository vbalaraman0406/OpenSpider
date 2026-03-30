#!/bin/bash
PYTHON=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/venv/bin/python
BACKEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend
FRONTEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend

echo '=== BACKEND REGRESSION TESTS ==='
cd $BACKEND
$PYTHON -m pytest test_regression.py -v --tb=short 2>&1
echo ''
echo 'PYTEST_EXIT:' $?

echo ''
echo '=== FRONTEND BUILD TEST ==='
cd $FRONTEND
npm run build 2>&1
echo ''
echo 'BUILD_EXIT:' $?

echo ''
echo '=== BACKEND SERVER STATUS ==='
curl -s http://localhost:8000/health
echo ''
curl -s http://localhost:8000/
echo ''

echo ''
echo '=== FRONTEND SERVER STATUS ==='
curl -s -o /dev/null -w 'HTTP_CODE: %{http_code}' http://localhost:3000/
echo ''