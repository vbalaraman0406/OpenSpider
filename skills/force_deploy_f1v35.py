import os
import datetime
import re

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Update deploy marker in main.py
main_path = os.path.join(BASE, 'backend/main.py')
with open(main_path, 'r') as f:
    content = f.read()

timestamp = str(datetime.datetime.now())
content = re.sub(r'# DEPLOY_MARKER:.*', f'# DEPLOY_MARKER: {timestamp}', content)
with open(main_path, 'w') as f:
    f.write(content)
print(f'main.py DEPLOY_MARKER updated to: {timestamp}')

# Also update index.html deploy marker
index_path = os.path.join(BASE, 'frontend/dist/index.html')
with open(index_path, 'r') as f:
    idx = f.read()
marker = f'<!-- deploy:{timestamp} -->'
if '<!-- deploy:' in idx:
    idx = re.sub(r'<!-- deploy:.*? -->', marker, idx)
else:
    idx = idx.replace('</head>', f'{marker}</head>')
with open(index_path, 'w') as f:
    f.write(idx)
print(f'index.html deploy marker updated')

# Verify key files
print('\n=== Verification ===')
print(f'main.py root_path: {"root_path" in content}')
print(f'main.py /tmp/fastf1_cache: {"/tmp/fastf1_cache" in content}')
print(f'index.html /f1/assets: {"/f1/assets" in idx}')
print('Ready for deploy.')
