#!/bin/bash
PROJECT_DIR="/Users/vbalaraman/OpenSpider/workspace/pitwall-ai"
cd "$PROJECT_DIR"

# Add a unique comment to Dashboard.tsx to force new bundle hash
echo "// Force rebuild: $(date +%s)" >> frontend/src/pages/Dashboard.tsx

# Delete old dist completely
find frontend/dist -type f -delete 2>/dev/null

# Rebuild frontend
cd frontend
npx vite build --base=/f1/
cd ..

# Show new bundle filename
echo "=== New bundle filename ==="
grep -o 'index-[A-Za-z0-9_-]*\.js' frontend/dist/index.html

# Verify error handling exists in new bundle
echo "=== setError count in new bundle ==="
NEW_BUNDLE=$(grep -o 'index-[A-Za-z0-9_-]*\.js' frontend/dist/index.html)
curl_count=$(grep -c 'setError' frontend/dist/assets/$NEW_BUNDLE 2>/dev/null)
echo "setError count: $curl_count"

# Also add deploy marker to main.py
echo "# Force deploy: $(date +%s)" >> backend/main.py

echo "=== Ready for deploy ==="