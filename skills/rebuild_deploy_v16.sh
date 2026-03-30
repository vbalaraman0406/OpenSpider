#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build
echo "BUILD_EXIT=$?"
echo "=== index.html ==="
head -5 dist/index.html
