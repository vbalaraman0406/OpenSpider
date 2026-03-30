#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet 2>&1
echo "DEPLOY_EXIT_CODE=$?"
