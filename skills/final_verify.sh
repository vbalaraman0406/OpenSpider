#!/bin/bash
echo '=== JS BUNDLE CONTENT TYPE ==='
curl -s -I https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-DcddWmmO.js | grep -i content-type
echo '=== JS FIRST 80 CHARS ==='
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/index-DcddWmmO.js | head -c 80
echo ''
echo '=== GIT STATUS ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
git add -A
git commit -m 'fix: complete rewrite to resolve blank screen - fixed imports, cache dir, routing, vite config'
git push origin main --force
echo 'GIT DONE'
