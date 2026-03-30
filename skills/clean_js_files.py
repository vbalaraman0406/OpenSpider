import os
import glob

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# Find all .js files that have a corresponding .tsx file
removed = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.js') and not f.endswith('.config.js'):
            fpath = os.path.join(root, f)
            # Check if there's a corresponding .tsx file
            tsx_path = fpath.replace('.js', '.tsx')
            if os.path.exists(tsx_path):
                os.remove(fpath)
                removed.append(fpath)
                print(f'REMOVED: {fpath} (has .tsx counterpart)')
            else:
                print(f'KEPT: {fpath} (no .tsx counterpart)')
        if f.endswith('.js.map'):
            fpath = os.path.join(root, f)
            os.remove(fpath)
            removed.append(fpath)
            print(f'REMOVED: {fpath} (sourcemap)')

# Also check for standalone .js files without .tsx
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.js'):
            print(f'REMAINING .js: {os.path.join(root, f)}')

print(f'\nTotal removed: {len(removed)}')
