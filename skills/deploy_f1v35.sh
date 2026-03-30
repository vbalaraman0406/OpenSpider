#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v35 --promote --quiet
echo "DEPLOY_EXIT=$?"
