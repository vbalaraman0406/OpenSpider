#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project vish-cloud --version f1v90 --no-promote --quiet 2>&1 &
DPID=$!
sleep 50
kill $DPID 2>/dev/null
gcloud app versions list --service f1 --project vish-cloud 2>&1
