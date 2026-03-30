#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# First rebuild frontend to ensure fresh dist
cd frontend
npx vite build --base=/f1/
cd ..

# Add a unique marker to force GCP to re-upload files
echo "# Deploy marker: $(date +%s)" >> backend/main.py

# Deploy to GCP
gcloud app deploy app.yaml --project=vish-cloud --version=f1v20 --promote --quiet 2>&1

echo "DEPLOY_EXIT_CODE: $?"

# Check if version was created
gcloud app versions list --service=f1 --project=vish-cloud 2>&1
