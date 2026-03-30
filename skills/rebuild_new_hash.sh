#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build
echo '=== NEW BUILD ASSETS ==='
ls -la dist/assets/
echo '=== NEW INDEX.HTML ==='
cat dist/index.html
echo '=== VENDOR CHECK ==='
grep -o 'vendor[^"]*' dist/assets/*.js || echo 'No vendor references in JS - GOOD'
