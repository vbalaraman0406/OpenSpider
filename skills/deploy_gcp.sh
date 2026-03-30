#!/bin/bash
echo '=== STEP 12: List and delete old f1 versions ==='
gcloud app versions list --service=f1 --project=vish-cloud

echo '=== Deleting old versions ==='
gcloud app versions delete 20260308t125352 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete 20260308t125804 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v2 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v3 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v4 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v5 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v6 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v7 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v8 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v9 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v10 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v11 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v16 --service=f1 --project=vish-cloud --quiet 2>/dev/null
gcloud app versions delete f1v22 --service=f1 --project=vish-cloud --quiet 2>/dev/null

echo '=== STEP 13: Deploy fresh ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1final --promote --quiet

echo '=== STEP 14: Restore .gcloudignore ==='
if [ -f /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/.gcloudignore.bak ]; then
    mv /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/.gcloudignore.bak /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/.gcloudignore
    echo 'Restored .gcloudignore'
fi

echo '=== DEPLOY COMPLETE ==='
