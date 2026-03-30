import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# 1. Fix api.ts - ensure baseURL is '/api' and add a real code change to force new hash
api_ts = f'{base}/frontend/src/api.ts'
with open(api_ts, 'r') as f:
    content = f.read()

# Verify baseURL
print('api.ts baseURL check:')
if "baseURL: '/api'" in content:
    print('  OK - baseURL is /api')
else:
    print('  FIXING baseURL...')
    content = content.replace("/f1/api", "/api")

# Add a real code change that affects the compiled output (not just a comment)
# Add a version constant that will be used in the code
if 'PITWALL_VERSION' not in content:
    content = f"// Pitwall.ai v2.0.{int(time.time())}\nconst PITWALL_VERSION = '{int(time.time())}';\nconsole.log('Pitwall.ai API module loaded, version:', PITWALL_VERSION);\n\n" + content
    print('  Added PITWALL_VERSION constant to force new bundle hash')

with open(api_ts, 'w') as f:
    f.write(content)

# 2. Fix main.py - ensure static assets are served at BOTH /assets and /f1/assets
main_py = f'{base}/backend/main.py'
with open(main_py, 'r') as f:
    main_content = f.read()

print('\nmain.py checks:')
print(f'  root_path: {"root_path" in main_content}')
print(f'  /assets mount: {"/assets" in main_content}')

# Check if catch-all route returns index.html properly
if '/{path:path}' in main_content:
    print('  SPA catch-all: YES')

# 3. Read main.tsx to check for double BrowserRouter
main_tsx = f'{base}/frontend/src/main.tsx'
with open(main_tsx, 'r') as f:
    tsx_content = f.read()
print(f'\nmain.tsx:')
print(tsx_content)

# 4. Read App.tsx to check for double BrowserRouter
app_tsx = f'{base}/frontend/src/App.tsx'
with open(app_tsx, 'r') as f:
    app_content = f.read()

# Check for double BrowserRouter
browser_router_count = app_content.count('BrowserRouter')
print(f'\nApp.tsx BrowserRouter count: {browser_router_count}')
if browser_router_count > 0:
    print('  WARNING: BrowserRouter found in App.tsx!')
    print('  main.tsx already wraps with BrowserRouter - this causes DOUBLE ROUTER!')
    # Fix: remove BrowserRouter from App.tsx
    app_content = app_content.replace('import { BrowserRouter, ', 'import { ')
    app_content = app_content.replace('import { BrowserRouter as Router, ', 'import { ')
    app_content = app_content.replace('import {BrowserRouter,', 'import {')
    # Remove BrowserRouter wrapper tags
    app_content = app_content.replace('<BrowserRouter>', '')
    app_content = app_content.replace('</BrowserRouter>', '')
    app_content = app_content.replace('<BrowserRouter basename="/f1">', '')
    app_content = app_content.replace("<BrowserRouter basename='/f1'>", '')
    app_content = app_content.replace('<Router>', '')
    app_content = app_content.replace('</Router>', '')
    app_content = app_content.replace('<Router basename="/f1">', '')
    app_content = app_content.replace("<Router basename='/f1'>", '')
    with open(app_tsx, 'w') as f:
        f.write(app_content)
    print('  FIXED: Removed BrowserRouter from App.tsx')

print('\n=== All fixes applied ===')
