import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

files_to_read = [
    'backend/main.py',
    'frontend/src/api.ts',
    'frontend/src/main.tsx',
    'app.yaml',
]

for f in files_to_read:
    path = os.path.join(base, f)
    print(f'\n===== {f} =====')
    if os.path.exists(path):
        with open(path) as fh:
            print(fh.read())
    else:
        print('FILE NOT FOUND')

# Check vite configs
import glob
vite_files = glob.glob(os.path.join(base, 'frontend', 'vite.config.*'))
print(f'\n===== VITE CONFIG FILES =====')
for vf in vite_files:
    print(f'\n--- {os.path.basename(vf)} ---')
    with open(vf) as fh:
        print(fh.read())

# Check index.html
index = os.path.join(base, 'frontend', 'dist', 'index.html')
print(f'\n===== frontend/dist/index.html =====')
if os.path.exists(index):
    with open(index) as fh:
        print(fh.read())
else:
    print('NOT FOUND - frontend not built')
