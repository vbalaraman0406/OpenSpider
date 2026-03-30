#!/bin/bash

echo "=== Check which JS bundle is referenced in index.html ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/ | grep -o 'index-[A-Za-z0-9_-]*\.js'

echo ""
echo "=== Check local dist index.html JS bundle reference ==="
grep -o 'index-[A-Za-z0-9_-]*\.js' /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html

echo ""
echo "=== Check if deployed JS has error handling (setError) ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-HfHv82_q.js 2>/dev/null | grep -c 'setError' || echo "Bundle not found or no setError"

echo ""
echo "=== Check deployed JS bundle for Array.isArray ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-HfHv82_q.js 2>/dev/null | grep -c 'Array.isArray' || echo "No Array.isArray found"

echo ""
echo "=== List local dist assets ==="
ls -la /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/assets/

echo ""
echo "=== Check pending GCP operations ==="
gcloud app operations list --project=vish-cloud --pending 2>&1

echo ""
echo "=== Check if f1v20 exists ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1 | grep f1v20
