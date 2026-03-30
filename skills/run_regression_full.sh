#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend
source venv/bin/activate

# Run backend tests and capture full output
python -m pytest test_regression.py -v --tb=short 2>&1 > /tmp/backend_test_results.txt
echo "PYTEST_EXIT=$?" >> /tmp/backend_test_results.txt

# Run frontend build
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npm run build 2>&1 > /tmp/frontend_build_results.txt
echo "BUILD_EXIT=$?" >> /tmp/frontend_build_results.txt

# Show results
echo '=== BACKEND TEST RESULTS ==='
cat /tmp/backend_test_results.txt
echo ''
echo '=== FRONTEND BUILD RESULTS ==='
cat /tmp/frontend_build_results.txt