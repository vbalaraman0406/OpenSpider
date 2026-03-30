import os
import datetime
import subprocess
import hashlib

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# 1. Verify main.py has root_path='/f1'
with open(os.path.join(BASE, 'backend/main.py'), 'r') as f:
    main_content = f.read()
print('root_path in main.py:', 'root_path' in main_content)
print('/tmp/fastf1_cache in main.py:', '/tmp/fastf1_cache' in main_content)

# 2. Add unique deploy marker to main.py
timestamp = str(datetime.datetime.now())
if '# DEPLOY_MARKER:' in main_content:
    import re
    main_content = re.sub(r'# DEPLOY_MARKER:.*', f'# DEPLOY_MARKER: {timestamp}', main_content)
else:
    main_content = f'# DEPLOY_MARKER: {timestamp}\n' + main_content

with open(os.path.join(BASE, 'backend/main.py'), 'w') as f:
    f.write(main_content)
print(f'main.py updated with DEPLOY_MARKER: {timestamp}')

# 3. Verify index.html has /f1/ paths
index_path = os.path.join(BASE, 'frontend/dist/index.html')
with open(index_path, 'r') as f:
    index_content = f.read()
print('index.html has /f1/assets:', '/f1/assets' in index_content)
print('First 300 chars:', index_content[:300])

# 4. Add deploy marker comment to index.html to force hash change
marker = f'<!-- deploy:{timestamp} -->'
if '<!-- deploy:' in index_content:
    import re
    index_content = re.sub(r'<!-- deploy:.*? -->', marker, index_content)
else:
    index_content = index_content.replace('</head>', f'{marker}</head>')
with open(index_path, 'w') as f:
    f.write(index_content)
print(f'index.html updated with deploy marker')

# 5. Verify app.yaml has service: f1
with open(os.path.join(BASE, 'app.yaml'), 'r') as f:
    app_yaml = f.read()
print('app.yaml service: f1:', 'service: f1' in app_yaml)
print('app.yaml content:')
print(app_yaml)

# 6. Print file hashes to confirm they changed
for fpath in ['backend/main.py', 'frontend/dist/index.html', 'app.yaml']:
    full = os.path.join(BASE, fpath)
    with open(full, 'rb') as f:
        h = hashlib.md5(f.read()).hexdigest()
    print(f'  {fpath}: md5={h}')

print('\nAll files prepared for deployment. Run deploy next.')
