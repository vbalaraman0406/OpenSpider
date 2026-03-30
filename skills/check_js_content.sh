#!/bin/bash
echo '=== JS bundle content type and first 200 chars ==='
curl -s -D - https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-HfHv82_q.js | head -30
echo ''
echo '=== CSS bundle content type ==='
curl -s -D - https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-DVdGxoMw.css | head -15
