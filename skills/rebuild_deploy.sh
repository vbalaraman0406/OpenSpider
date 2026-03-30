#!/bin/bash
set -e

echo '=== Step 4: Rebuild frontend ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/

echo '=== Step 5: Verify index.html ==='
head -5 /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html

echo '=== Step 6: Deploy to GCP ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v30 --promote --quiet

echo '=== DEPLOY COMPLETE ==='
