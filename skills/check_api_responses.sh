#!/bin/bash
echo '=== /f1/api/health ==='
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
echo ''
echo '=== /f1/api/races/2024 ==='
curl -s -w '\nHTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/races/2024
echo ''
echo '=== /f1/api/races/2026 ==='
curl -s -w '\nHTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/races/2026
echo ''
echo '=== /f1/api/drivers/2024 ==='
curl -s -w '\nHTTP_CODE=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/drivers/2024
echo ''
