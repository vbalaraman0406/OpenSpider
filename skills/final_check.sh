#!/bin/bash
echo "=== Pending operations ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== F1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Testing f1v6 ==="
curl -s -o /dev/null -w 'f1v6: HTTP %{http_code}' https://f1v6-dot-f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing f1 default ==="
curl -s -o /dev/null -w 'f1: HTTP %{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing root ==="
curl -s -o /dev/null -w 'root: HTTP %{http_code}' https://vish-cloud.wl.r.appspot.com/
echo ""

echo ""
echo "=== F1 logs (last 15) ==="
gcloud app logs read --service=f1 --project=vish-cloud --limit=15 2>&1
