#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
nohup gcloud app deploy app.yaml --project=vish-cloud --quiet --verbosity=error > /tmp/gae_deploy_f1.log 2>&1 &
DEPLOY_PID=$!
echo "Deploy PID: $DEPLOY_PID"
echo "Waiting 90 seconds for deploy to complete..."
sleep 90
echo "Checking if deploy completed..."
if kill -0 $DEPLOY_PID 2>/dev/null; then
  echo "Deploy still running after 90s"
else
  echo "Deploy process finished"
fi
echo "--- Deploy Log ---"
cat /tmp/gae_deploy_f1.log
echo "--- Services ---"
gcloud app services list --project=vish-cloud
