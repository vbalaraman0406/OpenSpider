import os
base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Read race.py imports
print('===== race.py IMPORTS =====')
with open(os.path.join(base, 'backend/routers/race.py')) as f:
    for line in f:
        if line.strip().startswith(('from ', 'import ')):
            print(line.rstrip())

print('\n===== drivers.py IMPORTS =====')
with open(os.path.join(base, 'backend/routers/drivers.py')) as f:
    for line in f:
        if line.strip().startswith(('from ', 'import ')):
            print(line.rstrip())

print('\n===== fastf1_loader.py FUNCTIONS =====')
with open(os.path.join(base, 'backend/data/fastf1_loader.py')) as f:
    for line in f:
        if line.strip().startswith('def ') or 'CACHE' in line or '/tmp' in line or 'makedirs' in line:
            print(line.rstrip())

print('\n===== App.tsx FULL =====')
with open(os.path.join(base, 'frontend/src/App.tsx')) as f:
    print(f.read())

print('\n===== main.tsx FULL =====')
with open(os.path.join(base, 'frontend/src/main.tsx')) as f:
    print(f.read())

print('\n===== api.ts FULL =====')
with open(os.path.join(base, 'frontend/src/api.ts')) as f:
    print(f.read())

print('\n===== vite.config.js FULL =====')
with open(os.path.join(base, 'frontend/vite.config.js')) as f:
    print(f.read())

print('\n===== index.html FULL =====')
with open(os.path.join(base, 'frontend/index.html')) as f:
    print(f.read())

print('\n===== main.py SPA catch-all =====')
with open(os.path.join(base, 'backend/main.py')) as f:
    content = f.read()
    # Print lines with /f1 routing
    for i, line in enumerate(content.split('\n')):
        if '/f1' in line or 'StaticFiles' in line or 'index.html' in line or 'catch' in line.lower() or 'health' in line:
            print(f'L{i+1}: {line}')
