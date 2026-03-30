import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

print('=== backend/main.py FULL ===')
with open(f'{base}/backend/main.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        print(f'{i:3d}: {line}', end='')

print('\n\n=== Directory structure check ===')
# Check what directories exist relative to project root
for d in ['frontend/dist', 'frontend/dist/assets', 'backend']:
    path = os.path.join(base, d)
    exists = os.path.exists(path)
    print(f'  {d}: {"EXISTS" if exists else "MISSING"}')
    if exists and os.path.isdir(path):
        files = os.listdir(path)
        for f in files[:10]:
            print(f'    - {f}')
