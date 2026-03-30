#!/bin/bash
export PATH="/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/venv/bin:$PATH"
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend
python -m pytest test_regression.py -v --tb=short > /tmp/test_output.txt 2>&1
echo "EXIT_CODE: $?" >> /tmp/test_output.txt
cat /tmp/test_output.txt