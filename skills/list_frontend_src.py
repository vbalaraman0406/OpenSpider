import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

for root, dirs, files in os.walk(base):
    level = root.replace(base, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        filepath = os.path.join(root, file)
        size = os.path.getsize(filepath)
        print(f'{subindent}{file} ({size} bytes)')

# Read key component files
print('\n\n===== App.tsx =====')
with open(os.path.join(base, 'App.tsx')) as f:
    print(f.read())

print('\n===== main.tsx =====')
with open(os.path.join(base, 'main.tsx')) as f:
    print(f.read())

print('\n===== api.ts =====')
with open(os.path.join(base, 'api.ts')) as f:
    print(f.read())

# Read pages directory if exists
pages_dir = os.path.join(base, 'pages')
if os.path.isdir(pages_dir):
    for fname in os.listdir(pages_dir):
        fpath = os.path.join(pages_dir, fname)
        if fname.endswith('.tsx') or fname.endswith('.ts'):
            print(f'\n===== pages/{fname} =====')
            with open(fpath) as f:
                print(f.read()[:2000])

# Read components directory if exists
comp_dir = os.path.join(base, 'components')
if os.path.isdir(comp_dir):
    for fname in os.listdir(comp_dir):
        fpath = os.path.join(comp_dir, fname)
        if fname.endswith('.tsx') or fname.endswith('.ts'):
            print(f'\n===== components/{fname} =====')
            with open(fpath) as f:
                print(f.read()[:2000])
