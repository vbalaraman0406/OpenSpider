import os, json, glob

auth_dir = 'baileys_auth_info'
print('=== Files in baileys_auth_info ===')
try:
    files = os.listdir(auth_dir)
    for f in sorted(files):
        if 'g.us' in f:
            print(f'  GROUP FILE: {f}')
    print(f'Total files: {len(files)}')
    group_files = [f for f in files if 'g.us' in f]
    print(f'Group-related files: {len(group_files)}')
except Exception as e:
    print(f'Error listing dir: {e}')

print('\n=== Creds Info ===')
try:
    with open(os.path.join(auth_dir, 'creds.json'), 'r') as f:
        creds = json.load(f)
    me = creds.get('me', {})
    print(f"Bot ID: {me.get('id', 'unknown')}")
    print(f"Bot name: {me.get('name', 'unknown')}")
except Exception as e:
    print(f'Error reading creds: {e}')

print('\n=== Looking for group metadata in store ===')
for root, dirs, fnames in os.walk(auth_dir):
    for fname in fnames:
        if 'group' in fname.lower() or 'g.us' in fname:
            print(f'  {os.path.join(root, fname)}')
