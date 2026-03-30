#!/bin/bash
echo "=== F1 service logs ==="
gcloud app logs read --service=f1 --project=vish-cloud --limit=30 2>&1

echo ""
echo "=== F1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1
