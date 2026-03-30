#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

echo '=== Verifying app.yaml ==='
cat app.yaml
echo ''

echo '=== Verifying files to deploy ==='
ls -la backend/main.py frontend/dist/index.html .gcloudignore
echo ''

echo '=== Deploying f1 service (attempt 2) ==='
gcloud app deploy app.yaml --project=vish-cloud --quiet --version=v1 --no-promote 2>&1
echo "EXIT_CODE=$?"
