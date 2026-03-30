#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend

# Create venv if not exists
if [ ! -d "venv" ]; then
  echo 'Creating virtual environment...'
  python3 -m venv venv
fi

# Activate and install deps
source venv/bin/activate
echo 'Installing backend dependencies...'
pip install -r requirements.txt 2>&1 | tail -20
echo ''
echo 'INSTALL EXIT CODE:' $?
echo ''
echo '=== Installed packages ==='
pip list 2>/dev/null | grep -i -E 'fastapi|uvicorn|fastf1|pandas|numpy|pydantic|scikit|requests'
echo ''
echo '=== Python version ==='
python --version