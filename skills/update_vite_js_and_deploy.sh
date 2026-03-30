#!/bin/bash
set -e

# Update vite.config.js to have base: '/f1/'
cat > /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/vite.config.js << 'VITEEOF'
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/f1/",
  server: {
    proxy: {
      "/f1/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
VITEEOF
echo 'Updated vite.config.js'

# Verify app.yaml has service: f1
echo '=== app.yaml ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/app.yaml

# Verify .gcloudignore exists
echo '=== .gcloudignore ==='
cat /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/.gcloudignore

# Deploy f1 service
echo '=== Deploying f1 service ==='
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
gcloud app deploy app.yaml --project=vish-cloud --quiet
echo "DEPLOY_EXIT=$?"
