import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Force hash change in main.py by adding unique deployment marker
main_path = os.path.join(base, 'backend', 'main.py')
with open(main_path, 'r') as f:
    content = f.read()

# Remove old deployment markers
lines = [l for l in content.split('\n') if not l.startswith('# DEPLOY_HASH_')]
content = '\n'.join(lines)

# Add new unique marker
marker = f'# DEPLOY_HASH_{int(time.time())}_{os.getpid()}'
content = marker + '\n' + content

with open(main_path, 'w') as f:
    f.write(content)

print(f'Added marker: {marker}')
print(f'main.py size: {os.path.getsize(main_path)} bytes')

# Also force hash change in routers
for fname in ['race.py', 'drivers.py']:
    fpath = os.path.join(base, 'backend', 'routers', fname)
    with open(fpath, 'r') as f:
        c = f.read()
    lines = [l for l in c.split('\n') if not l.startswith('# DEPLOY_HASH_')]
    c = marker + '\n' + '\n'.join(lines)
    with open(fpath, 'w') as f:
        f.write(c)
    print(f'{fname} updated, size: {os.path.getsize(fpath)}')

# Also force hash in fastf1_loader.py
fpath = os.path.join(base, 'backend', 'data', 'fastf1_loader.py')
with open(fpath, 'r') as f:
    c = f.read()
lines = [l for l in c.split('\n') if not l.startswith('# DEPLOY_HASH_')]
c = marker + '\n' + '\n'.join(lines)
with open(fpath, 'w') as f:
    f.write(c)
print(f'fastf1_loader.py updated, size: {os.path.getsize(fpath)}')

# Verify main.py has correct /f1/api prefixes
with open(main_path, 'r') as f:
    content = f.read()

if '/f1/api' in content:
    print('VERIFIED: main.py has /f1/api router prefixes')
else:
    print('ERROR: main.py missing /f1/api router prefixes!')

if 'root_path' in content:
    print('VERIFIED: main.py has root_path setting')

print('\nReady for deployment as f1v14')
