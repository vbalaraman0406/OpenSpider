#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --version=f1v14 --no-promote --quiet 2>&1
