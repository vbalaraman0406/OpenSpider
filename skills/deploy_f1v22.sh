#!/bin/bash
PROJECT_DIR="/Users/vbalaraman/OpenSpider/workspace/pitwall-ai"
cd "$PROJECT_DIR"

echo "=== Pending GCP operations ==="
gcloud app operations list --project=vish-cloud --pending 2>&1

echo ""
echo "=== Current versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Deploy f1v22 ==="
gcloud app deploy app.yaml --project=vish-cloud --version=f1v22 --promote --quiet 2>&1

echo ""
echo "=== Post-deploy versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1
