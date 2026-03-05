import os

root = '.'
for dirpath, dirnames, filenames in os.walk(root):
    # Skip node_modules and .git
    dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.git', 'dist', '.next')]
    for f in filenames:
        fl = f.lower()
        if 'cookie' in fl or 'session' in fl or 'export' in fl or fl == 'f1.json' or fl == 'f1_fantasy.json':
            full = os.path.join(dirpath, f)
            size = os.path.getsize(full)
            mtime = os.path.getmtime(full)
            print(f'{full} ({size} bytes, mtime={mtime})')

# Also check recently modified files in workspace/ and root
print('\n--- Recently modified files in workspace/ ---')
workspace_files = []
for f in os.listdir('./workspace'):
    fp = os.path.join('./workspace', f)
    if os.path.isfile(fp):
        workspace_files.append((os.path.getmtime(fp), f, os.path.getsize(fp)))
workspace_files.sort(reverse=True)
for mtime, name, size in workspace_files[:15]:
    print(f'  {name} ({size} bytes)')

print('\n--- Recently modified files in root ---')
root_files = []
for f in os.listdir('.'):
    fp = os.path.join('.', f)
    if os.path.isfile(fp):
        root_files.append((os.path.getmtime(fp), f, os.path.getsize(fp)))
root_files.sort(reverse=True)
for mtime, name, size in root_files[:15]:
    print(f'  {name} ({size} bytes)')
