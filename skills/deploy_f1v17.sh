#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v17 --promote --quiet 2>&1
echo "DEPLOY_EXIT=$?"
