#!/bin/bash
echo "Waiting for pending operation to complete..."
gcloud app operations wait 7adb9f1f-81b8-44b6-b82e-564bb6213b02 --project=vish-cloud
echo "Operation wait result: $?"
echo "Attempting deployment..."
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet --no-promote
echo "Deploy result: $?"
