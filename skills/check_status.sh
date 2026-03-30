#!/bin/bash
echo "=== Services ==="
gcloud app services list --project=vish-cloud

echo ""
echo "=== F1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Pending operations ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== Operation 1 status ==="
gcloud app operations describe 7adb9f1f-81b8-44b6-b82e-564bb6213b02 --project=vish-cloud 2>&1

echo ""
echo "=== Operation 2 status ==="
gcloud app operations describe ab6193c1-daf4-4f3a-a5c2-1fed9ef3b976 --project=vish-cloud 2>&1
