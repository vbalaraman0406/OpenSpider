import os

print('=== FILE LISTING ===')
count = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', 'cache', 'f1_cache')]
    for f in files:
        path = os.path.join(root, f)
        print(path)
        count += 1
print(f'\nTotal files: {count}')
