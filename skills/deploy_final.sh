#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1final --promote --quiet
echo "DEPLOY EXIT CODE: $?"
gcloud app versions list --service=f1 --project=vish-cloud
echo "DONE"