#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
nohup gcloud app deploy app.yaml --project=vish-cloud --quiet --promote > /tmp/gcloud_deploy.log 2>&1 &
echo "Deploy PID: $!"
echo "Waiting 90 seconds for deploy to complete..."
sleep 90
echo '=== Deploy log (last 30 lines) ==='
tail -30 /tmp/gcloud_deploy.log
echo ''
echo '=== Checking services ==='
gcloud app services list --project=vish-cloud 2>&1
