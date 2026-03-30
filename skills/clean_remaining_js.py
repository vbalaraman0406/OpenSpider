import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# Remove api.js since we have api.ts
api_js = os.path.join(base, 'api.js')
api_ts = os.path.join(base, 'api.ts')
if os.path.exists(api_js) and os.path.exists(api_ts):
    os.remove(api_js)
    print(f'REMOVED: {api_js} (has .ts counterpart)')

# Check index.js
index_js = os.path.join(base, 'index.js')
if os.path.exists(index_js):
    with open(index_js, 'r') as f:
        print(f'index.js content: {f.read()[:200]}')
    # Remove it - main.tsx is the entry point
    os.remove(index_js)
    print(f'REMOVED: {index_js}')

# Remove services/api.js if services/api.ts exists, otherwise check content
svc_js = os.path.join(base, 'services', 'api.js')
svc_ts = os.path.join(base, 'services', 'api.ts')
if os.path.exists(svc_js):
    if os.path.exists(svc_ts):
        os.remove(svc_js)
        print(f'REMOVED: {svc_js} (has .ts counterpart)')
    else:
        with open(svc_js, 'r') as f:
            print(f'services/api.js content: {f.read()[:200]}')
        os.remove(svc_js)
        print(f'REMOVED: {svc_js} (duplicate of src/api.ts)')

# Verify no .js files remain
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.js') or f.endswith('.js.map'):
            print(f'STILL EXISTS: {os.path.join(root, f)}')

print('Cleanup complete.')
