import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
files = [
    'backend/main.py',
    'backend/routers/race.py',
    'backend/routers/drivers.py',
    'backend/data/fastf1_loader.py',
    'frontend/src/App.tsx',
    'frontend/src/main.tsx',
    'frontend/src/api.ts',
    'frontend/vite.config.js',
    'frontend/index.html',
    'app.yaml',
    'requirements.txt',
]

for f in files:
    path = os.path.join(base, f)
    print(f'\n===== {f} =====')
    if os.path.exists(path):
        with open(path, 'r') as fh:
            content = fh.read()
            # Print first 2000 chars to stay within token limits
            if len(content) > 2000:
                print(content[:2000])
                print(f'... [TRUNCATED, total {len(content)} chars]')
            else:
                print(content)
    else:
        print('FILE NOT FOUND')

# Also check for vite.config.ts
ts_path = os.path.join(base, 'frontend/vite.config.ts')
print(f'\n===== frontend/vite.config.ts =====')
if os.path.exists(ts_path):
    with open(ts_path, 'r') as fh:
        print(fh.read())
    print('WARNING: vite.config.ts EXISTS and may override vite.config.js')
else:
    print('NOT FOUND (good - no conflict)')

# Check __init__.py files
for d in ['backend', 'backend/routers', 'backend/data']:
    init = os.path.join(base, d, '__init__.py')
    print(f'\n===== {d}/__init__.py =====')
    print('EXISTS' if os.path.exists(init) else 'MISSING')

# Check dist
dist_assets = os.path.join(base, 'frontend/dist/assets')
print(f'\n===== frontend/dist/assets =====')
if os.path.exists(dist_assets):
    for f in os.listdir(dist_assets):
        size = os.path.getsize(os.path.join(dist_assets, f))
        print(f'  {f} ({size} bytes)')
else:
    print('NOT FOUND')
