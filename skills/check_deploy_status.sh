#!/bin/bash
echo '=== Deploy log ==='
cat /tmp/gcloud_deploy.log 2>&1
echo ''
echo '=== Services ==='
gcloud app services list --project=vish-cloud 2>&1
echo ''
echo '=== Test f1 health ==='
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/health 2>&1
echo ''
curl -s -w '\nHTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/health 2>&1
echo ''
echo '=== Test via dispatch ==='
curl -s -w '\nHTTP=%{http_code}' https://vish-cloud.wl.r.appspot.com/f1/health 2>&1
