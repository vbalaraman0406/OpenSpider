#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Add deploy timestamp to force GCP re-upload
echo "# MINIMAL_DEPLOY_$(date +%s)" >> backend/main.py

# Deploy
gcloud app deploy app.yaml --project=vish-cloud --version=f1minimal --promote --quiet 2>&1

echo '=== DEPLOY COMMAND FINISHED ==='
