import os

files = [
    'workspace/pitwall-ai/app.yaml',
    'workspace/pitwall-ai/dispatch.yaml',
    'workspace/pitwall-ai/frontend/vite.config.ts',
    'workspace/pitwall-ai/frontend/src/App.tsx',
    'workspace/pitwall-ai/frontend/src/api.ts',
    'workspace/pitwall-ai/frontend/src/main.tsx',
]

for f in files:
    if os.path.exists(f):
        with open(f) as fh:
            content = fh.read()
        print(f'\n===== {f} ({len(content)} chars) =====')
        print(content[:800])
        if len(content) > 800:
            print(f'... [TRUNCATED {len(content)-800} more chars]')
    else:
        print(f'\n===== {f} NOT FOUND =====')
