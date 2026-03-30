import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

files = [
    'frontend/src/main.tsx',
    'frontend/src/App.tsx',
    'frontend/src/api.ts',
    'frontend/src/pages/Dashboard.tsx',
    'backend/main.py',
    'backend/routers/race.py',
    'backend/routers/drivers.py',
    'frontend/index.html',
    'app.yaml',
]

for f in files:
    path = os.path.join(base, f)
    print(f'\n{"="*60}')
    print(f'FILE: {f}')
    print(f'{"="*60}')
    if os.path.exists(path):
        with open(path, 'r') as fh:
            content = fh.read()
            print(content)
    else:
        print('FILE NOT FOUND')
