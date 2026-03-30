import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Remove the auto-created .gcloudignore if it exists
gcloudignore = os.path.join(BASE, '.gcloudignore')
bak = os.path.join(BASE, '.gcloudignore.bak')

# Write a proper .gcloudignore that excludes node_modules but includes frontend/dist
content = """.git
.gitignore
node_modules/
frontend/node_modules/
frontend/src/
frontend/.vite/
__pycache__/
*.pyc
.env
.venv/
venv/
*.log
.DS_Store
frontend/vite.config.js
frontend/vite.config.ts
frontend/tsconfig*.json
frontend/package-lock.json
frontend/index.html
README.md
.gcloudignore.bak
"""

with open(gcloudignore, 'w') as f:
    f.write(content)
print('Wrote .gcloudignore')

# Remove .bak if exists
if os.path.exists(bak):
    os.remove(bak)
    print('Removed .gcloudignore.bak')

# Verify frontend/dist exists and has the right files
dist_dir = os.path.join(BASE, 'frontend', 'dist')
if os.path.isdir(dist_dir):
    for root, dirs, files in os.walk(dist_dir):
        for f in files:
            fpath = os.path.join(root, f)
            print(f'  {os.path.relpath(fpath, BASE)}')
else:
    print('ERROR: frontend/dist does not exist!')
