#!/bin/bash
echo '=== Migrating traffic to f1v32 ==='
gcloud app services set-traffic f1 --splits=f1v32=1 --project=vish-cloud --quiet
echo "TRAFFIC_EXIT=$?"
echo ''
echo '=== Testing API endpoints ==='
echo '--- /f1/api/health ---'
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
echo ''
echo '--- /f1/api/races/2024 ---'
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/races/2024
echo ''
echo '--- /f1/api/race/schedule/2024 ---'
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/race/schedule/2024
echo ''
echo '--- /f1/api/drivers/2024 ---'
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/drivers/2024
echo ''
echo '--- /f1/api/api/race/schedule/2024 (double prefix test) ---'
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/api/race/schedule/2024
echo ''
echo '--- /f1/ (root page) ---'
curl -s -o /dev/null -w 'HTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/
echo ''
