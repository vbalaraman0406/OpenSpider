#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
echo "# deploy-bust-$(date +%s)" >> backend/main.py
echo "<!-- deploy $(date +%s) -->" >> frontend/dist/index.html
gcloud app deploy app.yaml --project=vish-cloud --version=f1v2 --promote --quiet
