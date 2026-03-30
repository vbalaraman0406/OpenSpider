#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/
echo "BUILD DONE"
ls -la dist/
ls -la dist/assets/
cat dist/index.html