#!/bin/bash
echo "Waiting for new deploy operation to complete..."
gcloud app operations wait ab6193c1-daf4-4f3a-a5c2-1fed9ef3b976 --project=vish-cloud
RESULT=$?
echo "Wait result: $RESULT"

echo ""
echo "=== Checking services ==="
gcloud app services list --project=vish-cloud

echo ""
echo "=== Checking f1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Checking pending operations ==="
gcloud app operations list --project=vish-cloud --pending
