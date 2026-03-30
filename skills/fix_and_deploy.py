import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

gi_content = ".git\n.gitignore\nnode_modules/\nfrontend/node_modules/\nfrontend/src/\nfrontend/.vite/\nfrontend/public/\nfrontend/tsconfig*.json\nfrontend/package-lock.json\nfrontend/eslint.config.js\nfrontend/vite.config.js\nfrontend/vite.config.ts\nfrontend/package.json\nfrontend/index.html\n__pycache__/\n*.pyc\n*.pyo\ncache/\nbackend/venv/\nbackend/cache/\nbackend/.pytest_cache/\nbackend/test_*.py\nbackend/scripts/\n.gcloudignore.bak\nskills/\n*.sh\n*.md\n.env\n.DS_Store\nDEPLOY_MARKER.txt\n"

gi_path = os.path.join(base, '.gcloudignore')
with open(gi_path, 'w') as f:
    f.write(gi_content)
print('Wrote .gcloudignore')

# Count remaining files
exclude = ['node_modules', '.git', '__pycache__', 'venv', '.pytest_cache', '.vite', 'skills']
count = 0
for root, dirs, files in os.walk(base):
    rel = os.path.relpath(root, base)
    skip = False
    for ex in exclude:
        if ex in rel.split(os.sep):
            skip = True
            break
    if skip:
        continue
    if rel.startswith('cache') or rel.startswith('backend/cache'):
        continue
    if rel.startswith('frontend/src'):
        continue
    count += len(files)
print(f'Estimated files: {count}')
