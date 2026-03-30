#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Kill any existing deploy processes
kill $(pgrep -f 'gcloud app deploy') 2>/dev/null

# Try deploy with verbose output
gcloud app deploy app.yaml --project=vish-cloud --quiet --promote --verbosity=info 2>&1 &
DEPLOY_PID=$!
echo "Deploy PID: $DEPLOY_PID"

# Wait up to 120 seconds
for i in $(seq 1 24); do
  sleep 5
  if ! kill -0 $DEPLOY_PID 2>/dev/null; then
    echo "Deploy process finished after $((i*5)) seconds"
    break
  fi
  echo "Waiting... $((i*5))s"
done

# Check result
echo ''
echo '=== Services ==='
gcloud app services list --project=vish-cloud 2>&1
echo ''
echo '=== Test health ==='
curl -s -w 'HTTP=%{http_code}' https://f1-dot-vish-cloud.wl.r.appspot.com/f1/health 2>&1
echo ''
