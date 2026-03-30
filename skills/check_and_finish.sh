#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

echo '=== Listing GCP App Engine services ==='
gcloud app services list --project=vish-cloud 2>&1

echo ''
echo '=== Testing f1 health endpoint ==='
curl -s -w '\nHTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/health 2>&1

echo ''
echo '=== Testing root health ==='
curl -s -w '\nHTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/health 2>&1

echo ''
echo '=== DONE ==='
