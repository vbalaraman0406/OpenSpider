import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend'

# Fix 1: index.html - src must be /src/main.tsx (vite adds base during build)
index_html = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pitwall.ai - F1 Analytics</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { background-color: #0a0a0f; color: #fff; font-family: Inter, system-ui, sans-serif; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''

with open(os.path.join(BASE, 'index.html'), 'w') as f:
    f.write(index_html)
print('Fixed index.html (src=/src/main.tsx)')

# Fix 2: Delete public/index.html if it exists (interferes with build)
pub_idx = os.path.join(BASE, 'public', 'index.html')
if os.path.exists(pub_idx):
    os.remove(pub_idx)
    print('Deleted public/index.html')

# Fix 3: Clean dist directory
dist_dir = os.path.join(BASE, 'dist')
if os.path.exists(dist_dir):
    for root, dirs, files in os.walk(dist_dir, topdown=False):
        for fn in files:
            os.remove(os.path.join(root, fn))
            print(f'Removed dist file: {fn}')
        for dn in dirs:
            try:
                os.rmdir(os.path.join(root, dn))
            except:
                pass
    print('Cleaned dist/')

# Fix 4: Create minimal index.css (imported by some components)
css_path = os.path.join(BASE, 'src', 'index.css')
with open(css_path, 'w') as f:
    f.write('/* minimal reset */\n* { margin: 0; padding: 0; box-sizing: border-box; }\nbody { background-color: #0a0a0f; color: #fff; }\n')
print('Wrote minimal index.css')

print('\nAll fixes applied. Ready to build.')
