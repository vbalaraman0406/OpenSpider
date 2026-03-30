#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai

# Restore original .gcloudignore if backup exists
if [ -f .gcloudignore.bak ]; then
  mv .gcloudignore.bak .gcloudignore
fi

# Write proper .gcloudignore that excludes node_modules but includes dist
cat > .gcloudignore << 'EOF'
.git
.gitignore
node_modules/
frontend/node_modules/
frontend/src/
frontend/.vite/
__pycache__/
*.pyc
cache/
.env
*.md
frontend/vite.config.js
frontend/vite.config.ts
frontend/tsconfig.json
frontend/tsconfig.node.json
frontend/package.json
frontend/package-lock.json
frontend/tailwind.config.js
frontend/postcss.config.js
frontend/public/
EOF

echo "Created .gcloudignore"
echo "Contents:"
cat .gcloudignore

# Deploy
gcloud app deploy app.yaml --project=vish-cloud --version=f1clean --promote --quiet 2>&1

echo "DEPLOY DONE"