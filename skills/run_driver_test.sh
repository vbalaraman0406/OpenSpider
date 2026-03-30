#!/bin/bash
PYTHON=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/venv/bin/python
BACKEND=/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend

echo '=== DRIVER STATS TEST ==='
cd $BACKEND
$PYTHON -m pytest test_regression.py -v --tb=short -k 'test_get_driver_stats and not invalid' 2>&1
echo ''
echo 'PYTEST_EXIT:' $?