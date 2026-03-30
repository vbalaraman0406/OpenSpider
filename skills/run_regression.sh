#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend
source venv/bin/activate

# Install test dependencies
pip install pytest httpx 2>&1 | tail -5

# Copy test file to correct location
cp /Users/vbalaraman/OpenSpider/skills/test_regression.py /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/test_regression.py

echo ''
echo '=== RUNNING BACKEND REGRESSION TESTS ==='
python -m pytest test_regression.py -v --tb=short 2>&1
echo ''
echo 'PYTEST EXIT CODE:' $?

# Now test frontend build
echo ''
echo '=== RUNNING FRONTEND BUILD TEST ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npm run build 2>&1 | tail -20
echo ''
echo 'FRONTEND BUILD EXIT CODE:' $?