#!/bin/bash
echo '=== PROJECT STRUCTURE (excluding .git) ==='
find /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/ -maxdepth 3 -type f -not -path '*/.git/*' 2>/dev/null
echo ''
echo '=== BACKEND FILES ==='
ls -la /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/ 2>/dev/null
echo ''
echo '=== FRONTEND FILES ==='
ls -la /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/ 2>/dev/null
echo ''
echo '=== ROOT FILES ==='
ls -la /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/ 2>/dev/null