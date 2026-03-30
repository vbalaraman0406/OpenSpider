#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npm run build
echo "BUILD_EXIT_CODE=$?"
head -5 dist/index.html
