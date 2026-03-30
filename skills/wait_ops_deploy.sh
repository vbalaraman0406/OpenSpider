#!/bin/bash
echo "=== All pending operations ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== Waiting for operation 03495bc8 ==="
gcloud app operations wait 03495bc8-44d4-4ae1-88c1-d81a8f5ad8a5 --project=vish-cloud
echo "Wait result: $?"

echo ""
echo "=== Waiting for operation ab6193c1 ==="
gcloud app operations wait ab6193c1-daf4-4f3a-a5c2-1fed9ef3b976 --project=vish-cloud
echo "Wait result: $?"

echo ""
echo "=== Checking operations again ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== Deploying f1 service as f1v4 ==="
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet --version=f1v4
echo "Deploy exit code: $?"
