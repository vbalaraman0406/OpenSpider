#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

echo "=== GCP f1 service versions ==="
gcloud app versions list --service=f1 --project=vish-cloud

echo ""
echo "=== Test health endpoint ==="
curl -s -o /dev/null -w "HTTP_CODE: %{http_code}" https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health

echo ""
echo "=== Test main page ==="
curl -s -o /dev/null -w "HTTP_CODE: %{http_code}" https://f1-dot-vish-cloud.wl.r.appspot.com/f1/

echo ""
echo "=== Check main page content (first 500 chars) ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/ | head -c 500

echo ""
echo "=== Check health endpoint content ==="
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
