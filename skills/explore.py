import os
import subprocess

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Find all Python files
for root, dirs, files in os.walk(base):
    # Skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', '.next', 'cache')]
    for f in files:
        if f.endswith('.py') or f == 'requirements.txt':
            path = os.path.join(root, f)
            relpath = os.path.relpath(path, base)
            print(f'FILE: {relpath}')

print('\n--- END FILE LIST ---')

# Now read all key files
key_files = []
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', '.next', 'cache')]
    for f in files:
        if f.endswith('.py') or f == 'requirements.txt':
            path = os.path.join(root, f)
            relpath = os.path.relpath(path, base)
            key_files.append((relpath, path))

for relpath, path in key_files:
    print(f'\n========== {relpath} ==========')
    try:
        with open(path) as fh:
            content = fh.read()
            print(content)
    except Exception as e:
        print(f'ERROR reading: {e}')
