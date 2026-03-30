import os

files = [
    'workspace/pitwall-ai/backend/main.py',
    'workspace/pitwall-ai/app.yaml',
    'workspace/pitwall-ai/dispatch.yaml',
    'workspace/pitwall-ai/frontend/vite.config.ts',
    'workspace/pitwall-ai/frontend/src/App.tsx',
    'workspace/pitwall-ai/frontend/src/api.ts',
    'workspace/pitwall-ai/frontend/src/main.tsx',
    'workspace/pitwall-ai/frontend/app.yaml',
    'workspace/pitwall-ai/backend/app.yaml',
    'workspace/pitwall-ai/backend/routers/drivers.py',
    'workspace/pitwall-ai/backend/routers/race.py',
]

for f in files:
    if os.path.exists(f):
        print(f'\n===== {f} =====')
        with open(f) as fh:
            print(fh.read())
    else:
        print(f'\n===== {f} (NOT FOUND) =====')
