import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# Read Navbar.tsx to check for issues
nav_path = os.path.join(base, 'components', 'Navbar.tsx')
print('=== Navbar.tsx ===')
if os.path.exists(nav_path):
    with open(nav_path) as f:
        print(f.read())
else:
    print('NOT FOUND')

# Read Dashboard.tsx
dash_path = os.path.join(base, 'pages', 'Dashboard.tsx')
print('\n=== Dashboard.tsx ===')
with open(dash_path) as f:
    dash_content = f.read()
    print(dash_content)

# Read RaceDetail.tsx
race_path = os.path.join(base, 'pages', 'RaceDetail.tsx')
print('\n=== RaceDetail.tsx ===')
if os.path.exists(race_path):
    with open(race_path) as f:
        print(f.read()[:1000])

# Read Drivers.tsx
drivers_path = os.path.join(base, 'pages', 'Drivers.tsx')
print('\n=== Drivers.tsx ===')
if os.path.exists(drivers_path):
    with open(drivers_path) as f:
        print(f.read()[:1000])

# Check tailwind config for pitwall colors
tw_path = os.path.join(base, '..', 'tailwind.config.js')
print('\n=== tailwind.config.js ===')
if os.path.exists(tw_path):
    with open(tw_path) as f:
        print(f.read())
else:
    print('NOT FOUND')

# Check index.css
css_path = os.path.join(base, 'index.css')
print('\n=== index.css ===')
if os.path.exists(css_path):
    with open(css_path) as f:
        print(f.read()[:1000])
