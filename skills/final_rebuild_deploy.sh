#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/ 2>&1 | tail -10
echo '=== JS BUNDLE ==='
ls -la dist/assets/*.js
echo '=== INDEX HTML ==='
head -5 dist/index.html
echo '=== DEPLOYING ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v55 --promote --quiet 2>&1 &
DPID=$!
sleep 55
kill $DPID 2>/dev/null
echo '=== VERSIONS ==='
gcloud app versions list --service=f1 --project=vish-cloud 2>&1 | grep -E 'f1v5|SERVING' | tail -5
