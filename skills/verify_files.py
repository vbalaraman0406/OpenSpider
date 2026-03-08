import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
all_files = []
for root, dirs, files in os.walk(base):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, base)
        size = os.path.getsize(full)
        all_files.append((rel, size))

all_files.sort()
for rel, size in all_files:
    print(f'{size:>6} bytes  {rel}')
print(f'\nTotal: {len(all_files)} files')
