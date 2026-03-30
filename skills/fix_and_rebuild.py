import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Step 2a: Verify/fix main.py - read full content
print('===== VERIFYING main.py =====')
with open(os.path.join(base, 'backend/main.py')) as f:
    main_content = f.read()
print(f'Length: {len(main_content)} chars')
print('Has root_path:', 'root_path' in main_content)
print('Has /f1/assets mount:', '/f1/assets' in main_content)
print('Has /f1/api prefix:', '/f1/api' in main_content)
print('Has health endpoint:', '/f1/api/health' in main_content)
print('Has SPA catch-all:', '/f1/{path:path}' in main_content)

# Step 2b: Delete vite.config.ts if exists
ts_path = os.path.join(base, 'frontend/vite.config.ts')
if os.path.exists(ts_path):
    os.remove(ts_path)
    print('DELETED vite.config.ts')
else:
    print('No vite.config.ts (good)')

# Step 2c: Verify vite.config.js
print('\n===== VERIFYING vite.config.js =====')
with open(os.path.join(base, 'frontend/vite.config.js')) as f:
    vite_content = f.read()
print(vite_content)
print('Has base /f1/:', "'/f1/'" in vite_content)
print('Has manualChunks:', 'manualChunks' in vite_content)

# Step 2d: Check current dist
print('\n===== CURRENT DIST =====')
dist_dir = os.path.join(base, 'frontend/dist')
if os.path.exists(dist_dir):
    for root, dirs, files in os.walk(dist_dir):
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, dist_dir)
            print(f'  {rel} ({os.path.getsize(fp)} bytes)')
else:
    print('dist/ NOT FOUND')

# Step 2e: Read dist/index.html
print('\n===== dist/index.html =====')
idx_path = os.path.join(dist_dir, 'index.html')
if os.path.exists(idx_path):
    with open(idx_path) as f:
        print(f.read())
else:
    print('NOT FOUND')

# Step 4: Write DEPLOY_MARKER.txt
ts = int(time.time())
marker_path = os.path.join(base, 'DEPLOY_MARKER.txt')
with open(marker_path, 'w') as f:
    f.write(f'FORCE_UPLOAD_{ts}\n')
print(f'\nDEPLOY_MARKER.txt written with timestamp {ts}')
