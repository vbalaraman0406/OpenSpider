import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Read api.ts fully
print('=== api.ts ===')
with open(f'{base}/frontend/src/api.ts', 'r') as f:
    print(f.read())

print('\n=== App.tsx ===')
with open(f'{base}/frontend/src/App.tsx', 'r') as f:
    print(f.read())

print('\n=== Dashboard.tsx ===')
with open(f'{base}/frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()
    print(content)

print('\n=== main.py (first 80 lines) ===')
with open(f'{base}/backend/main.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:80]):
        print(f'{i+1}: {line}', end='')
