#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet --version=f1v10 2>&1
