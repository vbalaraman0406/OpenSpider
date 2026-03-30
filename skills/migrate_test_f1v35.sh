#!/bin/bash
echo '=== Migrating traffic to f1v35 ==='
gcloud app services set-traffic f1 --splits=f1v35=1 --project=vish-cloud --quiet
echo "EXIT=$?"
echo ''
echo '=== Test /f1/api/races/2024 ==='
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/races/2024
echo ''
echo '=== Test /f1/api/race/schedule/2024 ==='
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/race/schedule/2024
echo ''
echo '=== Test /f1/api/drivers/2024 ==='
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/drivers/2024
echo ''
echo '=== Test /f1/api/health ==='
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
echo ''
echo '=== Check pending ops ==='
gcloud app operations list --project=vish-cloud --pending
