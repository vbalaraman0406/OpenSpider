import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend'
counts = {}
for root, dirs, files in os.walk(base):
    rel = os.path.relpath(root, base)
    if 'node_modules' in rel or '.git' in rel or '__pycache__' in rel:
        continue
    top = rel.split(os.sep)[0] if rel != '.' else '.'
    counts[top] = counts.get(top, 0) + len(files)

for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'{v:6d}  {k}')
