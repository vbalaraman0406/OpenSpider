import os

base = 'workspace/pitwall-ai'

# List all files and dirs
print('=== DIRECTORY STRUCTURE ===')
for root, dirs, files in os.walk(base):
    # skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__')]
    level = root.replace(base, '').count(os.sep)
    indent = '  ' * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = '  ' * (level + 1)
    for file in files:
        print(f'{subindent}{file}')

print('\n\n')

# Key files to read
key_files = [
    'backend/main.py',
    'backend/requirements.txt',
    'frontend/package.json',
    'frontend/src/App.jsx',
    'frontend/src/App.tsx',
    'app.yaml',
    'README.md',
    'backend/app.yaml',
    'frontend/app.yaml',
]

for kf in key_files:
    full = os.path.join(base, kf)
    if os.path.exists(full):
        print(f'\n===== FILE: {kf} =====')
        with open(full, 'r') as f:
            print(f.read())
        print(f'===== END: {kf} =====')
