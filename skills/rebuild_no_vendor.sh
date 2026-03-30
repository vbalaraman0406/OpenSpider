#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend

# Rebuild with no code-splitting (dist will be overwritten by vite build)
npx vite build

echo '=== BUILD OUTPUT FILES ==='
ls -la dist/assets/

echo '=== INDEX.HTML ==='
cat dist/index.html

# Check for vendor chunks
echo '=== VENDOR CHECK ==='
ls dist/assets/vendor* 2>/dev/null || echo 'No vendor chunks found - single bundle confirmed'
