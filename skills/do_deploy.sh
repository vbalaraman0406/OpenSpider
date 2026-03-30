#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
echo "Current dir: $(pwd)"
echo "app.yaml exists: $(test -f app.yaml && echo YES || echo NO)"
gcloud app deploy app.yaml --project=vish-cloud --version=f1live2 --promote --quiet
echo "Deploy exit code: $?"