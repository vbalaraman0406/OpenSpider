#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/
echo "BUILD COMPLETE"
ls -la dist/
ls -la dist/assets/ 2>/dev/null
echo "INDEX HTML:"
cat dist/index.html
