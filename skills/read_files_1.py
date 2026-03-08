import os

base = 'workspace/pitwall-ai'

# First batch of key files
key_files = [
    'backend/main.py',
    'backend/requirements.txt',
    'app.yaml',
    'backend/app.yaml',
    'README.md',
]

for kf in key_files:
    full = os.path.join(base, kf)
    if os.path.exists(full):
        print(f'\n===== {kf} =====')
        with open(full, 'r') as f:
            content = f.read()
        print(content[:2000])
        if len(content) > 2000:
            print(f'... [TRUNCATED, total {len(content)} chars]')
        print(f'===== END =====')
    else:
        print(f'\n[MISSING] {kf}')
