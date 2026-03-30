#!/bin/bash
set -e

PROJECT_DIR="/Users/vbalaraman/OpenSpider/workspace/pitwall-ai"
cd "$PROJECT_DIR"

echo "=== Step 1: Check pending GCP operations ==="
gcloud app operations list --project=vish-cloud --pending 2>&1 || echo "No pending ops or error checking"

echo ""
echo "=== Step 2: Check current f1 versions ==="
gcloud app versions list --service=f1 --project=vish-cloud 2>&1

echo ""
echo "=== Step 3: Verify local main.py has correct routing ==="
head -60 backend/main.py

echo ""
echo "=== Step 4: Verify Dashboard.tsx has error handling ==="
grep -c 'setError' frontend/src/pages/Dashboard.tsx 2>&1 || echo "setError not found"
grep -c 'Array.isArray' frontend/src/pages/Dashboard.tsx 2>&1 || echo "Array.isArray not found"

echo ""
echo "=== Step 5: Check vite configs ==="
ls -la frontend/vite.config.* 2>&1
echo "--- vite.config.js ---"
cat frontend/vite.config.js 2>&1 || echo "No vite.config.js"
echo "--- vite.config.ts ---"
cat frontend/vite.config.ts 2>&1 || echo "No vite.config.ts"

echo ""
echo "=== Step 6: Check current dist/index.html ==="
head -20 frontend/dist/index.html 2>&1 || echo "No dist/index.html"

echo ""
echo "=== Step 7: Current app.yaml ==="
cat app.yaml
