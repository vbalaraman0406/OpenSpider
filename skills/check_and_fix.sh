#!/bin/bash
echo '=== Current versions ==='
gcloud app versions list --service=f1 --project=vish-cloud
echo ''
echo '=== Migrating traffic to f1v22 (latest created) ==='
gcloud app services set-traffic f1 --splits=f1v22=1 --project=vish-cloud --quiet
echo "TRAFFIC_EXIT=$?"
echo ''
echo '=== Testing health endpoint ==='
curl -s -o /dev/null -w 'HTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
echo ''
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
echo ''
echo '=== Testing root page ==='
curl -s -o /dev/null -w 'HTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ''
