#!/bin/bash
echo "=== Routing traffic to f1v3 ==="
gcloud app services set-traffic f1 --splits=f1v3=1 --project=vish-cloud --quiet 2>&1
echo "Traffic route exit: $?"

echo ""
echo "=== Waiting 10 seconds ==="
sleep 10

echo ""
echo "=== Testing f1v3 directly ==="
curl -s -o /dev/null -w 'f1v3: HTTP %{http_code}' https://f1v3-dot-f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing f1 default ==="
curl -s -o /dev/null -w 'f1: HTTP %{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== F1 logs (last 10) ==="
gcloud app logs read --service=f1 --project=vish-cloud --limit=10 2>&1
