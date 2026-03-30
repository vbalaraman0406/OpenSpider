#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
echo '=== Listing vite config files ==='
ls -la vite.config.*
echo ''
echo '=== vite.config.ts content ==='
cat vite.config.ts
echo ''
echo '=== Rebuilding with explicit base ==='
npx vite build --base=/f1/
echo ''
echo '=== Checking built index.html ==='
cat dist/index.html
