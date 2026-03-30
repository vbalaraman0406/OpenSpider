import os
import subprocess

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Add a unique comment to App.tsx to force new content hash
app_path = os.path.join(base, 'frontend', 'src', 'App.tsx')
with open(app_path, 'r') as f:
    content = f.read()

import time
timestamp = str(int(time.time()))
content = content.rstrip() + f'\n// build-{timestamp}\n'

with open(app_path, 'w') as f:
    f.write(content)
print(f'Added build timestamp {timestamp} to App.tsx')

# Verify vite.config.js has no code-splitting
vite_path = os.path.join(base, 'frontend', 'vite.config.js')
with open(vite_path, 'r') as f:
    vc = f.read()
print(f'vite.config.js:\n{vc}')

# List current dist assets before rebuild
dist_dir = os.path.join(base, 'frontend', 'dist', 'assets')
print(f'\nCurrent dist assets:')
for f2 in os.listdir(dist_dir):
    print(f'  {f2} ({os.path.getsize(os.path.join(dist_dir, f2))} bytes)')
