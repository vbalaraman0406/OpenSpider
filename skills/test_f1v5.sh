#!/bin/bash
echo "=== F1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Pending operations ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== Testing f1v5 directly ==="
curl -s -o /dev/null -w 'f1v5: HTTP %{http_code}' https://f1v5-dot-f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing default f1 service ==="
curl -s -o /dev/null -w 'f1 default: HTTP %{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing root site ==="
curl -s -o /dev/null -w 'root: HTTP %{http_code}' https://vish-cloud.wl.r.appspot.com/
echo ""

echo ""
echo "=== Recent f1 logs ==="
gcloud app logs read --service=f1 --project=vish-cloud --limit=20 2>&1
