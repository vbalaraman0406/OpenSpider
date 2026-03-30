#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Add a unique file to force GCP to detect changes
echo "FORCE_UPLOAD_$(date +%s)_$$" > frontend/dist/assets/force_upload.txt

# Also modify main.py to force hash change
echo "# DEPLOY_TIMESTAMP=$(date +%s)" >> backend/main.py

# Check what's in dist
echo "=== dist/index.html ==="
cat frontend/dist/index.html
echo ""
echo "=== dist/assets/ ==="
ls -la frontend/dist/assets/

# Deploy with force
gcloud app deploy app.yaml --project=vish-cloud --version=f1final3 --promote --quiet 2>&1