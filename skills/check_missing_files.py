import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# List ALL files in src recursively
print('=== ALL SOURCE FILES ===')
for root, dirs, files in os.walk(base):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), base)
        print(f'  {rel}')

# Check App.tsx imports
print('\n=== App.tsx FULL ===')
with open(f'{base}/App.tsx', 'r') as f:
    print(f.read())

# Check if Predictions page exists
pred_path = f'{base}/pages/Predictions.tsx'
print(f'\n=== Predictions.tsx exists: {os.path.exists(pred_path)} ===')
if os.path.exists(pred_path):
    with open(pred_path, 'r') as f:
        print(f.read()[:500])

# Check Navbar.tsx
print('\n=== Navbar.tsx ===')
with open(f'{base}/components/Navbar.tsx', 'r') as f:
    print(f.read())

# Check if there's a tailwind config issue
tw_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/tailwind.config.js'
print(f'\n=== tailwind.config.js exists: {os.path.exists(tw_path)} ===')
if os.path.exists(tw_path):
    with open(tw_path, 'r') as f:
        print(f.read())

# Check postcss config
pc_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/postcss.config.js'
print(f'\n=== postcss.config.js exists: {os.path.exists(pc_path)} ===')
if os.path.exists(pc_path):
    with open(pc_path, 'r') as f:
        print(f.read())

# Check index.css
print('\n=== index.css ===')
with open(f'{base}/index.css', 'r') as f:
    print(f.read()[:1000])
