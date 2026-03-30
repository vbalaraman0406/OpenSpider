#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Rename .gcloudignore to force full upload
if [ -f .gcloudignore ]; then
  mv .gcloudignore .gcloudignore.bak
  echo "Renamed .gcloudignore to .gcloudignore.bak"
fi

# Deploy fresh version
gcloud app deploy app.yaml --project=vish-cloud --version=f1clean --promote --quiet 2>&1

# Restore .gcloudignore
if [ -f .gcloudignore.bak ]; then
  mv .gcloudignore.bak .gcloudignore
  echo "Restored .gcloudignore"
fi

echo "DEPLOY COMPLETE"