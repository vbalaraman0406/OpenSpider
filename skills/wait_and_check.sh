#!/bin/bash
echo 'Waiting 45 seconds for GCP operation to complete...'
sleep 45
echo '=== Checking versions ==='
gcloud app versions list --service=f1 --project=vish-cloud
echo '=== Checking pending ops ==='
gcloud app operations list --project=vish-cloud --pending
