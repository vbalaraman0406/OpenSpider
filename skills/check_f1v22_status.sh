#!/bin/bash
echo "=== Pending operations ==="
gcloud app operations list --project=vish-cloud --pending 2>&1

echo ""
echo "=== All f1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Check if f1v22 exists ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1 | grep f1v22

echo ""
echo "=== Current traffic ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1 | grep -v '0.00'

echo ""
echo "=== Test site ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/ | grep -o 'index-[A-Za-z0-9_-]*\.js'

echo ""
echo "=== Test health ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
