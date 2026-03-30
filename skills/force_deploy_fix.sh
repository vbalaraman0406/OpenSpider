#!/bin/bash
PROJECT_DIR="/Users/vbalaraman/OpenSpider/workspace/pitwall-ai"
cd "$PROJECT_DIR"

echo "=== Check .gcloudignore for dist exclusion ==="
cat .gcloudignore

echo ""
echo "=== Check if frontend/dist is in the upload ==="
ls -la frontend/dist/
ls -la frontend/dist/assets/

echo ""
echo "=== Verify index.html has new bundle ==="
grep 'index-' frontend/dist/index.html
