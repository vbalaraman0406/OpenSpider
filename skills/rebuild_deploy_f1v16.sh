#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/
echo "BUILD_STATUS=$?"
echo "=== index.html check ==="
head -5 dist/index.html
echo ""
echo "=== deploying to GCP ==="
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v16 --promote --quiet 2>&1
echo "DEPLOY_STATUS=$?"
