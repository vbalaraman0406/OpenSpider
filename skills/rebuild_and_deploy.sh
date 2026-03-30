#!/bin/bash
set -e

echo '=== Rebuilding frontend ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npm run build 2>&1 | tail -20

echo ''
echo '=== Verifying build output ==='
head -5 /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html

echo ''
echo '=== Deploying f1 service to GCP App Engine ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet 2>&1 | tail -30

echo ''
echo '=== Deploying dispatch rules ==='
gcloud app deploy dispatch.yaml --project=vish-cloud --quiet 2>&1 | tail -10

echo ''
echo '=== DONE ==='
