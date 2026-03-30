#!/bin/bash
PYTHON=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/venv/bin/python
BACKEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend

echo '=== BACKEND FAST TESTS (skip slow API calls) ==='
cd $BACKEND
$PYTHON -m pytest test_regression.py -v --tb=short -k 'not driver_stats and not race_laps and not race_results' --timeout=10 2>&1
echo ''
echo 'PYTEST_EXIT:' $?

echo ''
echo '=== BACKEND SERVER STATUS ==='
curl -s http://localhost:8000/health
echo ''
curl -s http://localhost:8000/
echo ''