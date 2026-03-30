#!/bin/bash
PYTHON=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/venv/bin/python
BACKEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend

echo '=== BACKEND FAST TESTS ==='
cd $BACKEND
$PYTHON -m pytest test_regression.py -v --tb=short -k 'not driver_stats and not race_laps and not race_results and not telemetry and not strategy' 2>&1
echo ''
echo 'PYTEST_EXIT:' $?