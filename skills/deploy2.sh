#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
echo '=== Current app.yaml ===' 
head -3 app.yaml
echo '=== Deploying f1 service ==='
gcloud app deploy app.yaml --project=vish-cloud --quiet 2>&1
echo '=== Deploy exit code: '$?' ==='
