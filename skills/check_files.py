import os

base = 'workspace/pitwall-ai'
for root, dirs, files in os.walk(base):
    for f in files:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f'{size:>6}  {path}')
