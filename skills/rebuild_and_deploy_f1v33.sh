#!/bin/bash
set -e

echo '=== Rebuilding frontend with base=/f1/ ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/

echo '=== Verifying index.html has /f1/ paths ==='
head -5 /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html

echo '=== Deploying f1v33 to GCP ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v33 --promote --quiet

echo 'DEPLOY_COMPLETE'
