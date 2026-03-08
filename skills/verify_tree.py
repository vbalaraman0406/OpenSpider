import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
print('Pitwall.ai Project File Tree:')
print('=' * 50)
total = 0
for root, dirs, fls in os.walk(BASE):
    dirs[:] = [d for d in sorted(dirs) if d not in ('cache', 'node_modules', '__pycache__', '.git')]
    level = root.replace(BASE, '').count(os.sep)
    indent = '  ' * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = '  ' * (level + 1)
    for f in sorted(fls):
        size = os.path.getsize(os.path.join(root, f))
        print(f'{subindent}{f} ({size}B)')
        total += 1
print(f'\nTotal files: {total}')
