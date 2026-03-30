import os
import subprocess

base = '/Users/vbalaraman/OpenSpider'

# Find creds.json files
for root, dirs, files in os.walk(base):
    # Skip node_modules
    if 'node_modules' in root:
        continue
    for f in files:
        if f == 'creds.json' and 'baileys' in root.lower():
            print(f'CREDS: {os.path.join(root, f)}')
        if 'g.us' in f:
            print(f'GROUP: {os.path.join(root, f)}')
        if 'group' in f.lower() and f.endswith('.json'):
            print(f'GROUP_META: {os.path.join(root, f)}')

# Also check for any baileys directories
for root, dirs, files in os.walk(base):
    if 'node_modules' in root:
        continue
    for d in dirs:
        if 'baileys' in d.lower() or 'auth' in d.lower():
            full = os.path.join(root, d)
            print(f'AUTH_DIR: {full}')
            try:
                contents = os.listdir(full)
                for c in sorted(contents)[:20]:
                    print(f'  -> {c}')
                if len(contents) > 20:
                    print(f'  ... and {len(contents)-20} more')
            except:
                pass
