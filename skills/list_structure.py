import os

root = 'workspace/pitwall-ai'
for dirpath, dirnames, filenames in os.walk(root):
    # Skip node_modules and .git
    dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.git', 'dist', '__pycache__', '.venv', 'venv')]
    level = dirpath.replace(root, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(dirpath)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in filenames:
        print(f'{subindent}{file}')
