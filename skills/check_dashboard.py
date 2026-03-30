import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# Read Dashboard.tsx
dash_path = os.path.join(base, 'pages', 'Dashboard.tsx')
print('=== Dashboard.tsx ===')
with open(dash_path) as f:
    print(f.read())

# Read Navbar.tsx
nav_path = os.path.join(base, 'components', 'Navbar.tsx')
print('\n=== Navbar.tsx ===')
if os.path.exists(nav_path):
    with open(nav_path) as f:
        print(f.read())
else:
    print('FILE NOT FOUND')

# Read App.tsx
app_path = os.path.join(base, 'App.tsx')
print('\n=== App.tsx ===')
with open(app_path) as f:
    print(f.read())

# Read index.css
css_path = os.path.join(base, 'index.css')
print('\n=== index.css (first 500 chars) ===')
if os.path.exists(css_path):
    with open(css_path) as f:
        print(f.read()[:500])
else:
    print('FILE NOT FOUND')

# Check tailwind config
tw_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/tailwind.config.js'
print('\n=== tailwind.config.js ===')
if os.path.exists(tw_path):
    with open(tw_path) as f:
        print(f.read())
else:
    print('FILE NOT FOUND')
