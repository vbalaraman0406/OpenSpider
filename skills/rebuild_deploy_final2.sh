#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/ 2>&1
echo '=== BUILT FILES ==='
ls dist/assets/
echo '=== INDEX HTML HEAD ==='
head -10 dist/index.html
echo '=== DEPLOYING ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project vish-cloud --version f1v60 --promote --quiet 2>&1 &
DPID=$!
sleep 55
kill $DPID 2>/dev/null
echo '=== CHECK VERSIONS ==='
gcloud app versions list --service f1 --project vish-cloud 2>&1
