#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/
echo '=== BUILD COMPLETE ==='
ls -la dist/
echo '=== INDEX.HTML ==='
cat dist/index.html
