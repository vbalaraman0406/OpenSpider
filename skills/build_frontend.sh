#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
npx vite build
echo "BUILD COMPLETE"
echo "Files in dist/assets:"
ls dist/assets/
echo "index.html content:"
cat dist/index.html