import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'
pages_dir = os.path.join(base, 'pages')
components_dir = os.path.join(base, 'components')

# List what actually exists
print('=== pages/ ===')
if os.path.isdir(pages_dir):
    for f in os.listdir(pages_dir):
        print(f'  {f} ({os.path.getsize(os.path.join(pages_dir, f))} bytes)')
else:
    print('  DIRECTORY NOT FOUND')

print('=== components/ ===')
if os.path.isdir(components_dir):
    for f in os.listdir(components_dir):
        print(f'  {f} ({os.path.getsize(os.path.join(components_dir, f))} bytes)')
else:
    print('  DIRECTORY NOT FOUND')

# Check which pages exist
pages = []
for name in ['Dashboard', 'RaceDetail', 'Drivers', 'Compare']:
    path = os.path.join(pages_dir, f'{name}.tsx')
    if os.path.exists(path):
        pages.append(name)
        print(f'[EXISTS] pages/{name}.tsx')
    else:
        print(f'[MISSING] pages/{name}.tsx')

# Check Navbar
navbar_exists = os.path.exists(os.path.join(components_dir, 'Navbar.tsx'))
print(f'Navbar exists: {navbar_exists}')

# Build App.tsx with only existing components
imports = []
routes = []

if navbar_exists:
    imports.append("import Navbar from './components/Navbar'")

for page in pages:
    imports.append(f"import {page} from './pages/{page}'")

route_map = {
    'Dashboard': '/',
    'RaceDetail': '/race/:year/:round',
    'Drivers': '/drivers/:year',
    'Compare': '/compare',
}

for page in pages:
    if page in route_map:
        routes.append(f'            <Route path="{route_map[page]}" element={{<{page} />}} />')

imports_str = '\n'.join(imports)
routes_str = '\n'.join(routes)

nav_jsx = '<Navbar />' if navbar_exists else '{/* No Navbar */}'

app_tsx = f"""import {{ BrowserRouter, Routes, Route }} from 'react-router-dom'
{imports_str}
import './index.css'

function App() {{
  return (
    <BrowserRouter basename="/f1">
      <div className="min-h-screen bg-pitwall-bg text-pitwall-text">
        {nav_jsx}
        <main className="container mx-auto px-4 py-8">
          <Routes>
{routes_str}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}}

export default App
"""

app_path = os.path.join(base, 'App.tsx')
with open(app_path, 'w') as f:
    f.write(app_tsx)
print(f'\n[OK] Written App.tsx with {len(pages)} pages: {pages}')
print(app_tsx)
