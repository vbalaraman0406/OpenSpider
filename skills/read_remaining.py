import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

files = [
    'frontend/src/App.tsx',
    'frontend/src/main.tsx',
    'frontend/vite.config.js',
    'app.yaml',
    '.gcloudignore',
    'requirements.txt',
]

for rel in files:
    full = os.path.join(BASE, rel)
    print('=' * 60)
    print('FILE:', rel)
    print('EXISTS:', os.path.exists(full))
    print('=' * 60)
    if os.path.exists(full):
        with open(full, 'r') as f:
            print(f.read())
    else:
        print('NOT FOUND')
    print()

# Check vite.config.ts
ts = os.path.join(BASE, 'frontend/vite.config.ts')
print('=' * 60)
print('vite.config.ts EXISTS:', os.path.exists(ts))
print('=' * 60)
if os.path.exists(ts):
    with open(ts, 'r') as f:
        print(f.read())
