#!/bin/bash
echo "=== Checking if f1 service exists ==="
gcloud app services list --project=vish-cloud

echo ""
echo "=== Checking pending operations ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== Trying to list f1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Attempting fresh deploy ==="
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet --no-promote --version=f1v2
echo "Deploy exit code: $?"
