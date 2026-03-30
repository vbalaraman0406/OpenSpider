import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend'

# Read current index.html to see what vite is using
idx_path = os.path.join(BASE, 'index.html')
with open(idx_path) as f:
    content = f.read()
print('Current index.html:')
print(content)
print('---')

# Check if there are multiple index.html files
for root, dirs, files in os.walk(BASE):
    if 'node_modules' in root:
        continue
    for fn in files:
        if fn == 'index.html':
            print(f'Found index.html at: {root}')

# Check src directory
print('\nFiles in src/:')
for f in os.listdir(os.path.join(BASE, 'src')):
    print(f'  {f}')

# Read main.tsx
with open(os.path.join(BASE, 'src', 'main.tsx')) as f:
    print('\nmain.tsx:')
    print(f.read())

# Check if there's a CSS import in main.tsx that's missing
print('\nChecking for index.css...')
css_path = os.path.join(BASE, 'src', 'index.css')
if os.path.exists(css_path):
    print('index.css exists')
else:
    print('index.css does NOT exist')

# Check App.css
css2 = os.path.join(BASE, 'src', 'App.css')
if os.path.exists(css2):
    print('App.css exists')
else:
    print('App.css does NOT exist')
