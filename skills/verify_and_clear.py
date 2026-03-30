import os
import json

# 1. Verify the fix was applied correctly
with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

print('=== Verified fix (lines 288-320) ===')
for i in range(287, min(320, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')

# 2. Check for stale sender-key files for the Family group
auth_dir = '/Users/vbalaraman/OpenSpider/baileys_auth_info'
family_jid = '14156249639-1373117853'
stale_files = []
for f in os.listdir(auth_dir):
    if family_jid in f and 'sender-key' in f:
        stale_files.append(f)

print(f'\n=== Stale sender-key files for Family group: {len(stale_files)} ===')
for f in stale_files:
    fp = os.path.join(auth_dir, f)
    print(f'  Removing: {f}')
    os.remove(fp)

if stale_files:
    print(f'Removed {len(stale_files)} stale sender-key files')
else:
    print('No stale sender-key files found (already clean)')

# 3. Check if there's a build step needed
print('\n=== Checking build config ===')
if os.path.exists('/Users/vbalaraman/OpenSpider/package.json'):
    with open('/Users/vbalaraman/OpenSpider/package.json', 'r') as f:
        pkg = json.load(f)
    scripts = pkg.get('scripts', {})
    print(f'Available scripts: {list(scripts.keys())}')
    if 'build' in scripts:
        print(f'Build command: {scripts["build"]}')
    if 'start' in scripts:
        print(f'Start command: {scripts["start"]}')
    if 'dev' in scripts:
        print(f'Dev command: {scripts["dev"]}')
