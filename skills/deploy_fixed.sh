#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Add deploy timestamp to force GCP re-upload of backend files
echo "# FIXED_DEPLOY_$(date +%s)" >> backend/main.py

# Deploy new version
gcloud app deploy app.yaml --project=vish-cloud --version=f1fixed --promote --quiet 2>&1

echo '=== DEPLOY FINISHED ==='
