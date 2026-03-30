#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/
echo "BUILD DONE"
echo "=== dist/index.html ==="
cat dist/index.html
echo "=== dist/assets ==="
ls -la dist/assets/
