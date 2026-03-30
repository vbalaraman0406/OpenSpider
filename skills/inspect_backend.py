import os

parent = os.path.dirname(os.getcwd())
src_dir = os.path.join(parent, 'src')

print('=== src/ directory contents ===')
for root, dirs, files in os.walk(src_dir):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
    level = root.replace(src_dir, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for f in files:
        filepath = os.path.join(root, f)
        size = os.path.getsize(filepath)
        print(f'{subindent}{f} ({size} bytes)')
