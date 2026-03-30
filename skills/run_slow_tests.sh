#!/bin/bash
PYTHON=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/venv/bin/python
BACKEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend

echo '=== BACKEND SLOW TESTS (API-dependent) ==='
cd $BACKEND
$PYTHON -m pytest test_regression.py -v --tb=short -k 'race_laps or race_results or driver_stats_2024' 2>&1
echo ''
echo 'PYTEST_EXIT:' $?