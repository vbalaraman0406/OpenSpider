#!/bin/bash
echo '=== MAIN.PY ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/main.py 2>/dev/null
echo ''
echo '=== DATA DIR ==='
ls /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/data/ 2>/dev/null
echo ''
echo '=== fastf1_loader.py (first 80 lines) ==='
head -80 /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/data/fastf1_loader.py 2>/dev/null
echo ''
echo '=== MODELS DIR ==='
ls /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/models/ 2>/dev/null
echo ''
echo '=== requirements.txt ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/requirements.txt 2>/dev/null
echo ''
echo '=== Makefile ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/Makefile 2>/dev/null
echo ''
echo '=== app.yaml ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/app.yaml 2>/dev/null