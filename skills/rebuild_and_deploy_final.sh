#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build --base=/f1/
echo "BUILD_EXIT_CODE=$?"
echo "--- INDEX.HTML ---"
head -10 dist/index.html
