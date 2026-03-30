#!/bin/bash
echo "Waiting for f1v5 deploy operation..."
gcloud app operations wait d134ed77-26ae-464c-aa8c-a70c62475a22 --project=vish-cloud
echo "Wait exit: $?"

echo ""
echo "=== F1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Testing f1v5 directly ==="
curl -s -o /dev/null -w 'f1v5: HTTP %{http_code}' https://f1v5-dot-f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== F1 logs ==="
gcloud app logs read --service=f1 --project=vish-cloud --limit=15 2>&1
