#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
echo '=== Verifying race.py imports ==='
head -5 backend/routers/race.py
echo '=== Verifying drivers.py imports ==='
head -5 backend/routers/drivers.py
echo '=== Deploying f1v7 ==='
gcloud app deploy app.yaml --project=vish-cloud --quiet --version=f1v7 2>&1
