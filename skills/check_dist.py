import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist'

# Check assets directory
assets_dir = os.path.join(base, 'assets')
if os.path.exists(assets_dir):
    files = os.listdir(assets_dir)
    print('Local dist/assets files:')
    for f in sorted(files):
        fpath = os.path.join(assets_dir, f)
        size = os.path.getsize(fpath)
        print(f'  {f} ({size} bytes)')
else:
    print('dist/assets directory does NOT exist')

# Check index.html
idx = os.path.join(base, 'index.html')
if os.path.exists(idx):
    with open(idx) as f:
        content = f.read()
    print('\nLocal index.html:')
    print(content)
else:
    print('dist/index.html does NOT exist')

# GCP serves index-DSBP2uHW.js - check if this file exists locally
target_js = 'index-DSBP2uHW.js'
if os.path.exists(os.path.join(assets_dir, target_js)):
    print(f'\n{target_js} EXISTS locally')
    with open(os.path.join(assets_dir, target_js)) as f:
        content = f.read()
    print(f'Size: {len(content)} bytes')
    print(f'First 200 chars: {content[:200]}')
    print(f'Last 200 chars: {content[-200:]}')
else:
    print(f'\n{target_js} does NOT exist locally - GCP is serving a STALE version!')
    print('Local JS files:', [f for f in os.listdir(assets_dir) if f.endswith(".js")])
