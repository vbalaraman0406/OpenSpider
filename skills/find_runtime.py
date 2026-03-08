import os
import subprocess

# Check for PM2 processes, running node processes, etc.
print('=== Looking for bot runtime ===')

# Check parent directory
parent = os.path.dirname(os.getcwd())
print(f'\nParent dir: {parent}')
try:
    items = os.listdir(parent)
    for item in sorted(items):
        fp = os.path.join(parent, item)
        if os.path.isdir(fp) and not item.startswith('.'):
            print(f'  {item}/')
        elif os.path.isfile(fp):
            print(f'  {item}')
except:
    print('  Cannot list parent')

# Search for whatsapp-related dirs in parent
print('\n=== Searching for whatsapp/bot dirs in parent ===')
for root, dirs, files in os.walk(parent):
    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '.next', '.cache')]
    depth = root.replace(parent, '').count(os.sep)
    if depth > 2:
        dirs.clear()
        continue
    for f in files:
        if any(kw in f.lower() for kw in ['whatsapp', 'wa.ts', 'wa.js', 'bot.ts', 'bot.js']):
            print(f'  {os.path.join(root, f)}')

# Check if there's a monorepo packages dir
print('\n=== Checking for monorepo structure ===')
for d in ['packages', 'apps', 'services', 'server', 'backend', 'bot']:
    check = os.path.join(parent, d)
    if os.path.isdir(check):
        print(f'  Found: {check}')
        for item in os.listdir(check)[:10]:
            print(f'    {item}')
