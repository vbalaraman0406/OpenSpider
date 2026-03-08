import os
import glob

base = '/Users/vbalaraman/OpenSpider'

# Find all files related to 919940496224
print('=== Files containing 919940496224 in name ===')
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '.next')]
    for f in files:
        if '919940496224' in f:
            fp = os.path.join(root, f)
            print(f'  {fp} ({os.path.getsize(fp)} bytes)')

# Check auth/session directories
print('\n=== Auth/Session directories ===')
for d in ['auth_info', 'auth_info_baileys', 'auth', 'session', 'sessions', 'baileys_auth', 'baileys_store', 'store']:
    check = os.path.join(base, d)
    if os.path.isdir(check):
        print(f'\n{check}/')
        items = os.listdir(check)
        print(f'  Total files: {len(items)}')
        # Show files related to 919940496224
        for item in items:
            if '919940496224' in item:
                fp = os.path.join(check, item)
                print(f'  MATCH: {item} ({os.path.getsize(fp)} bytes)')
    check2 = os.path.join(base, 'workspace', d)
    if os.path.isdir(check2):
        print(f'\n{check2}/')
        items = os.listdir(check2)
        print(f'  Total files: {len(items)}')
        for item in items:
            if '919940496224' in item:
                fp = os.path.join(check2, item)
                print(f'  MATCH: {item} ({os.path.getsize(fp)} bytes)')

# Also check workspace/auth directories
print('\n=== Workspace subdirectories ===')
workspace = os.path.join(base, 'workspace')
if os.path.isdir(workspace):
    for item in sorted(os.listdir(workspace)):
        fp = os.path.join(workspace, item)
        if os.path.isdir(fp):
            print(f'  {item}/')
            subitems = os.listdir(fp)
            print(f'    ({len(subitems)} items)')
            for si in subitems:
                if '919940496224' in si:
                    print(f'    MATCH: {si}')
