#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Remove the auto-generated .gcloudignore and restore proper one
rm -f .gcloudignore
rm -f .gcloudignore.bak

# Write proper .gcloudignore
cat > .gcloudignore << 'IGNORE'
.git
.gitignore
node_modules/
frontend/node_modules/
frontend/src/
frontend/.env
__pycache__/
*.pyc
.venv/
venv/
cache/
*.log
.DS_Store
skills/
IGNORE

# Verify file count
echo "=== File count check ==="
find . -not -path './node_modules/*' -not -path './frontend/node_modules/*' -not -path './frontend/src/*' -not -path './.git/*' -not -path './__pycache__/*' -not -path './cache/*' -not -path './venv/*' -not -path './.venv/*' -not -path './skills/*' -type f | wc -l

# Deploy
gcloud app deploy app.yaml --project=vish-cloud --version=f1fresh --promote --quiet 2>&1
