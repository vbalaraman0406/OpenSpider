#!/bin/bash
echo '=== BACKEND requirements.txt ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/requirements.txt 2>/dev/null
echo ''
echo '=== BACKEND main.py (first 50 lines) ==='
head -50 /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/main.py 2>/dev/null
echo ''
echo '=== BACKEND all .py files ==='
ls /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/*.py 2>/dev/null
echo ''
echo '=== FRONTEND package.json ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/package.json 2>/dev/null
echo ''
echo '=== EXISTING TEST FILES ==='
find /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/ -not -path '*/.git/*' -not -path '*/node_modules/*' -name '*test*' -o -name '*spec*' 2>/dev/null
echo ''
echo '=== README ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/README.md 2>/dev/null