import os

base = 'workspace/pitwall-ai'
print('=== ALL FILES ===')
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '__pycache__', '.next')]
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), base)
        print(rel)
