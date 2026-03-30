#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1nuclear --promote --quiet
