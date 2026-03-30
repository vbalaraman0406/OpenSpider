import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Step 1: Remove .gcloudignore to force full upload
gcloudignore = os.path.join(base, '.gcloudignore')
if os.path.exists(gcloudignore):
    os.rename(gcloudignore, gcloudignore + '.bak')
    print('[OK] Renamed .gcloudignore to .gcloudignore.bak')

# Step 2: Create minimal .gcloudignore that only excludes node_modules and .git
with open(gcloudignore, 'w') as f:
    f.write('node_modules/\n.git/\nfrontend/node_modules/\nfrontend/src/\n__pycache__/\n*.pyc\ncache/\n')
print('[OK] Created minimal .gcloudignore')

# Step 3: Force hash change on ALL key Python files
ts = int(time.time())

# main.py
main_py = os.path.join(base, 'backend', 'main.py')
with open(main_py) as f:
    content = f.read()
# Remove old timestamps
lines = [l for l in content.split('\n') if 'DEPLOY_TIMESTAMP' not in l and 'FORCE_UPLOAD' not in l]
content = '\n'.join(lines)
content += f'\n# DEPLOY_TIMESTAMP={ts}\n'
with open(main_py, 'w') as f:
    f.write(content)
print(f'[OK] main.py hash forced with ts={ts}')

# race.py
race_py = os.path.join(base, 'backend', 'routers', 'race.py')
with open(race_py) as f:
    content = f.read()
lines = [l for l in content.split('\n') if 'DEPLOY_TIMESTAMP' not in l]
content = '\n'.join(lines) + f'\n# DEPLOY_TIMESTAMP={ts}\n'
with open(race_py, 'w') as f:
    f.write(content)
print('[OK] race.py hash forced')

# drivers.py
drivers_py = os.path.join(base, 'backend', 'routers', 'drivers.py')
with open(drivers_py) as f:
    content = f.read()
lines = [l for l in content.split('\n') if 'DEPLOY_TIMESTAMP' not in l]
content = '\n'.join(lines) + f'\n# DEPLOY_TIMESTAMP={ts}\n'
with open(drivers_py, 'w') as f:
    f.write(content)
print('[OK] drivers.py hash forced')

# fastf1_loader.py
loader_py = os.path.join(base, 'backend', 'data', 'fastf1_loader.py')
with open(loader_py) as f:
    content = f.read()
lines = [l for l in content.split('\n') if 'DEPLOY_TIMESTAMP' not in l]
content = '\n'.join(lines) + f'\n# DEPLOY_TIMESTAMP={ts}\n'
with open(loader_py, 'w') as f:
    f.write(content)
print('[OK] fastf1_loader.py hash forced')

# Step 4: Verify index.html has /f1/assets/
index_html = os.path.join(base, 'frontend', 'dist', 'index.html')
with open(index_html) as f:
    html = f.read()
print(f'[CHECK] index.html has /f1/assets/ = {"/f1/assets/" in html}')
print(f'[CHECK] index.html first 300 chars: {html[:300]}')

# Step 5: Verify app.yaml
app_yaml = os.path.join(base, 'app.yaml')
with open(app_yaml) as f:
    content = f.read()
print(f'[CHECK] app.yaml has service: f1 = {"service: f1" in content}')

print(f'\n[READY] All files prepared for nuclear deploy. Run gcloud app deploy now.')
