import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Write strict .gcloudignore
gi_path = os.path.join(base, '.gcloudignore')
ignore_content = ".git\n.gitignore\nnode_modules/\nfrontend/node_modules/\nfrontend/src/\nfrontend/.vite/\n__pycache__/\n*.pyc\n*.pyo\ncache/\n.gcloudignore.bak\nskills/\n*.sh\n*.md\n.env\n.DS_Store\nfrontend/public/\nfrontend/tsconfig*.json\nfrontend/package-lock.json\nfrontend/eslint.config.js\nfrontend/vite.config.js\nfrontend/vite.config.ts\nfrontend/package.json\nfrontend/index.html\nbackend/test_*.py\nDEPLOY_MARKER.txt\n"

with open(gi_path, 'w') as f:
    f.write(ignore_content)
print('Wrote .gcloudignore')

# Count files that would be uploaded
count = 0
for root, dirs, files in os.walk(base):
    rel = os.path.relpath(root, base)
    skip = False
    for pattern in ['node_modules', '.git', '__pycache__', 'cache', 'skills', '.vite', 'frontend/src']:
        if pattern in rel or rel.startswith(pattern):
            skip = True
            break
    if skip:
        continue
    for f in files:
        if not f.endswith(('.pyc', '.pyo', '.sh', '.DS_Store')):
            count += 1
print(f'Estimated upload file count: {count}')
