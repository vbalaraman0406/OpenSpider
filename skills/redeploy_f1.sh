#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

echo '=== Current app.yaml ==='
cat app.yaml
echo ''
echo '=== Deploying f1 service ==='
gcloud app deploy app.yaml --project=vish-cloud --quiet --version=v1 2>&1
echo "DEPLOY_EXIT=$?"
echo ''
echo '=== Listing services ==='
gcloud app services list --project=vish-cloud 2>&1
