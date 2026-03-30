#!/bin/bash
echo "=== F1 service versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Testing f1 service ==="
curl -s -o /dev/null -w 'HTTP %{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing specific versions ==="
curl -s -o /dev/null -w 'f1v2: HTTP %{http_code}' https://f1v2-dot-f1-dot-vish-cloud.wl.r.appspot.com/f1/ 2>&1
echo ""
curl -s -o /dev/null -w 'f1v3: HTTP %{http_code}' https://f1v3-dot-f1-dot-vish-cloud.wl.r.appspot.com/f1/ 2>&1
echo ""

echo ""
echo "=== F1 service logs (last 10) ==="
gcloud app logs read --service=f1 --project=vish-cloud --limit=10 2>&1
