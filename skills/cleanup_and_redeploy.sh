#!/bin/bash
echo "=== Deleting old f1 versions to clear operations ==="
gcloud app versions delete 20260308t125804 --service=f1 --project=vish-cloud --quiet 2>&1
echo "Delete 20260308t125804: $?"

gcloud app versions delete f1v2 --service=f1 --project=vish-cloud --quiet 2>&1
echo "Delete f1v2: $?"

echo ""
echo "=== Checking pending operations ==="
gcloud app operations list --project=vish-cloud --pending

echo ""
echo "=== Trying deploy ==="
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet --version=f1v6
echo "Deploy exit: $?"
