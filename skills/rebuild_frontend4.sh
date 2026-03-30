#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend
node -e "const fs=require('fs'); fs.rmSync('dist',{recursive:true,force:true}); console.log('dist cleaned');"
npx vite build
echo "---BUILD COMPLETE---"
cat dist/index.html
