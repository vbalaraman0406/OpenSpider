#!/bin/bash
echo 'Waiting 30 seconds for f1v33 build...'
sleep 30
echo '=== Versions ==='
gcloud app versions list --service=f1 --project=vish-cloud
echo '=== Pending ops ==='
gcloud app operations list --project=vish-cloud --pending
