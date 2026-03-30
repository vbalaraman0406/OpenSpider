#!/bin/bash
echo "=== Testing f1 service directly ==="
curl -s -o /dev/null -w 'HTTP %{http_code}' https://20260308t125352-dot-f1-dot-vish-cloud.appspot.com/f1/
echo ""

echo ""
echo "=== Testing f1 service via main domain ==="
curl -s -o /dev/null -w 'HTTP %{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ""

echo ""
echo "=== Testing root documentation site ==="
curl -s -o /dev/null -w 'HTTP %{http_code}' https://vish-cloud.wl.r.appspot.com/
echo ""

echo ""
echo "=== Deleting stuck f1v2 version ==="
gcloud app versions delete f1v2 --service=f1 --project=vish-cloud --quiet 2>&1
