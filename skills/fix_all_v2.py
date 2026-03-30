import os
import time

PROJECT = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'
TS = str(int(time.time()))

# STEP 1: Rewrite backend/main.py
lines = [
    'import os',
    'import sys',
    'import time',
    'from pathlib import Path',
    'from fastapi import FastAPI, Request',
    'from fastapi.middleware.cors import CORSMiddleware',
    'from fastapi.staticfiles import StaticFiles',
    'from fastapi.responses import JSONResponse, HTMLResponse',
    '',
    '# DEPLOY_TIMESTAMP_' + TS,
    '',
    'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))',
    '',
    'try:',
    '    from backend.routers import race, drivers',
    'except ImportError:',
    '    from routers import race, drivers',
    '',
    'app = FastAPI(title="Pitwall.ai", docs_url="/f1/docs", openapi_url="/f1/openapi.json")',
    '',
    'app.add_middleware(',
    '    CORSMiddleware,',
    '    allow_origins=["*"],',
    '    allow_credentials=True,',
    '    allow_methods=["*"],',
    '    allow_headers=["*"],',
    ')',
    '',
    'app.include_router(race.router, prefix="/f1/api")',
    'app.include_router(drivers.router, prefix="/f1/api")',
    '',
    '@app.get("/f1/api/health")',
    '@app.get("/api/health")',
    '@app.get("/health")',
    'async def health():',
    '    return {"status": "ok", "service": "pitwall-ai", "timestamp": time.time()}',
    '',
    'DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"',
    'ASSETS_DIR = DIST_DIR / "assets"',
    'if ASSETS_DIR.exists():',
    '    app.mount("/f1/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")',
    '',
    '@app.get("/f1")',
    'async def serve_spa_root(request: Request):',
    '    index_file = DIST_DIR / "index.html"',
    '    if index_file.exists():',
    '        return HTMLResponse(index_file.read_text())',
    '    return JSONResponse({"error": "Frontend not built"}, status_code=500)',
    '',
    '@app.get("/f1/{path:path}")',
    'async def serve_spa(request: Request, path: str = ""):',
    '    index_file = DIST_DIR / "index.html"',
    '    if index_file.exists():',
    '        return HTMLResponse(index_file.read_text())',
    '    return JSONResponse({"error": "Frontend not built"}, status_code=500)',
    '',
]

with open(os.path.join(PROJECT, 'backend', 'main.py'), 'w') as f:
    f.write('\n'.join(lines))
print('STEP 1 DONE: backend/main.py rewritten')

# STEP 2a: Fix race.py imports
import re
race_path = os.path.join(PROJECT, 'backend', 'routers', 'race.py')
with open(race_path, 'r') as f:
    content = f.read()

# Extract what's imported
match = re.search(r'from (?:backend\.)?data\.fastf1_loader import (.+)', content)
imports_str = match.group(1).strip() if match else 'get_race_results, get_race_laps, get_qualifying_results'

# Remove all fastf1_loader import lines and surrounding try/except
cleaned_lines = []
i = 0
orig_lines = content.split('\n')
while i < len(orig_lines):
    line = orig_lines[i]
    stripped = line.strip()
    # Skip standalone import lines
    if 'fastf1_loader' in line and ('from ' in line or 'import ' in line):
        i += 1
        continue
    # Skip try: blocks that contain fastf1_loader
    if stripped == 'try:' and i + 1 < len(orig_lines) and 'fastf1_loader' in orig_lines[i + 1]:
        i += 1
        # Skip indented lines and except block
        while i < len(orig_lines):
            s = orig_lines[i].strip()
            if s.startswith('except'):
                i += 1
                # Skip indented lines after except
                while i < len(orig_lines) and (orig_lines[i].startswith('    ') or orig_lines[i].strip() == ''):
                    if orig_lines[i].strip() == '' and i + 1 < len(orig_lines) and not orig_lines[i+1].startswith('    '):
                        break
                    i += 1
                break
            elif not s and i + 1 < len(orig_lines) and not orig_lines[i+1].startswith('    '):
                break
            else:
                i += 1
        continue
    cleaned_lines.append(line)
    i += 1

# Find insertion point (after last import)
insert_at = 0
for idx, line in enumerate(cleaned_lines):
    if line.startswith('from ') or line.startswith('import '):
        insert_at = idx + 1

new_import = [
    'try:',
    '    from backend.data.fastf1_loader import ' + imports_str,
    'except ImportError:',
    '    from data.fastf1_loader import ' + imports_str,
]
cleaned_lines = cleaned_lines[:insert_at] + new_import + cleaned_lines[insert_at:]

with open(race_path, 'w') as f:
    f.write('\n'.join(cleaned_lines))
print('STEP 2a DONE: race.py imports fixed (' + imports_str + ')')

# STEP 2b: Fix drivers.py imports
drivers_path = os.path.join(PROJECT, 'backend', 'routers', 'drivers.py')
with open(drivers_path, 'r') as f:
    content = f.read()

match = re.search(r'from (?:backend\.)?data\.fastf1_loader import (.+)', content)
imports_d = match.group(1).strip() if match else 'get_driver_standings, get_driver_season_stats'

cleaned_lines = []
i = 0
orig_lines = content.split('\n')
while i < len(orig_lines):
    line = orig_lines[i]
    stripped = line.strip()
    if 'fastf1_loader' in line and ('from ' in line or 'import ' in line):
        i += 1
        continue
    if stripped == 'try:' and i + 1 < len(orig_lines) and 'fastf1_loader' in orig_lines[i + 1]:
        i += 1
        while i < len(orig_lines):
            s = orig_lines[i].strip()
            if s.startswith('except'):
                i += 1
                while i < len(orig_lines) and (orig_lines[i].startswith('    ') or orig_lines[i].strip() == ''):
                    if orig_lines[i].strip() == '' and i + 1 < len(orig_lines) and not orig_lines[i+1].startswith('    '):
                        break
                    i += 1
                break
            elif not s and i + 1 < len(orig_lines) and not orig_lines[i+1].startswith('    '):
                break
            else:
                i += 1
        continue
    cleaned_lines.append(line)
    i += 1

insert_at = 0
for idx, line in enumerate(cleaned_lines):
    if line.startswith('from ') or line.startswith('import '):
        insert_at = idx + 1

new_import = [
    'try:',
    '    from backend.data.fastf1_loader import ' + imports_d,
    'except ImportError:',
    '    from data.fastf1_loader import ' + imports_d,
]
cleaned_lines = cleaned_lines[:insert_at] + new_import + cleaned_lines[insert_at:]

with open(drivers_path, 'w') as f:
    f.write('\n'.join(cleaned_lines))
print('STEP 2b DONE: drivers.py imports fixed (' + imports_d + ')')

# STEP 3: Fix fastf1_loader.py cache dir
loader_path = os.path.join(PROJECT, 'backend', 'data', 'fastf1_loader.py')
with open(loader_path, 'r') as f:
    lc = f.read()
# Replace all possible cache dir references
for old in ["'/workspace/cache'", '"cache"', "'cache'", "'./cache'", "'/workspace/fastf1_cache'"]:
    lc = lc.replace(old, "'/tmp/fastf1_cache'")
# Fix double replacements
lc = lc.replace("'/tmp/fastf1_/tmp/fastf1_cache'", "'/tmp/fastf1_cache'")
with open(loader_path, 'w') as f:
    f.write(lc)
print('STEP 3 DONE: cache dir -> /tmp/fastf1_cache')

# STEP 4: Ensure __init__.py files
for subdir in ['backend', 'backend/data', 'backend/routers']:
    init_path = os.path.join(PROJECT, subdir, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('')
        print('STEP 4: Created ' + init_path)
    else:
        print('STEP 4: ' + init_path + ' exists')

# STEP 5: Delete vite.config.ts
vite_ts = os.path.join(PROJECT, 'frontend', 'vite.config.ts')
if os.path.exists(vite_ts):
    os.remove(vite_ts)
    print('STEP 5 DONE: Deleted vite.config.ts')
else:
    print('STEP 5: vite.config.ts already gone')

# STEP 6: Rewrite vite.config.js
vite_js_path = os.path.join(PROJECT, 'frontend', 'vite.config.js')
vite_lines = [
    "import { defineConfig } from 'vite'",
    "import react from '@vitejs/plugin-react'",
    '',
    'export default defineConfig({',
    '  plugins: [react()],',
    "  base: '/f1/',",
    '  build: {',
    '    rollupOptions: {',
    '      output: {',
    '        manualChunks: undefined',
    '      }',
    '    }',
    '  }',
    '})',
    '',
]
with open(vite_js_path, 'w') as f:
    f.write('\n'.join(vite_lines))
print('STEP 6 DONE: vite.config.js rewritten')

# STEP 9: app.yaml
app_yaml_lines = [
    'runtime: python311',
    'service: f1',
    'instance_class: F2',
    'automatic_scaling:',
    '  min_instances: 0',
    '  max_instances: 3',
    'entrypoint: python -m gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.main:app --bind :$PORT',
    '',
]
with open(os.path.join(PROJECT, 'app.yaml'), 'w') as f:
    f.write('\n'.join(app_yaml_lines))
print('STEP 9 DONE: app.yaml written')

# STEP 10: requirements.txt
reqs = ['gunicorn>=21.2.0', 'uvicorn>=0.23.0', 'fastapi>=0.100.0', 'fastf1>=3.3.0', 'pandas>=2.0.0', 'numpy>=1.24.0', 'scikit-learn>=1.3.0', 'requests>=2.31.0', 'httpx>=0.24.0']
with open(os.path.join(PROJECT, 'requirements.txt'), 'w') as f:
    f.write('\n'.join(reqs) + '\n')
print('STEP 10 DONE: requirements.txt written')

# STEP 11: Rename .gcloudignore
gci = os.path.join(PROJECT, '.gcloudignore')
gci_bak = os.path.join(PROJECT, '.gcloudignore.bak')
if os.path.exists(gci):
    os.rename(gci, gci_bak)
    print('STEP 11 DONE: .gcloudignore -> .gcloudignore.bak')
elif os.path.exists(gci_bak):
    print('STEP 11: .gcloudignore.bak already exists')
else:
    print('STEP 11: No .gcloudignore found')

# Verify key files
print('\n=== VERIFICATION ===')
with open(os.path.join(PROJECT, 'backend', 'main.py'), 'r') as f:
    mp = f.read()
print('main.py has /f1/assets mount:', '/f1/assets' in mp)
print('main.py has /f1/api prefix:', '/f1/api' in mp)
print('main.py has root_path:', 'root_path' in mp)
print('main.py has DEPLOY_TIMESTAMP:', 'DEPLOY_TIMESTAMP' in mp)

with open(os.path.join(PROJECT, 'app.yaml'), 'r') as f:
    ay = f.read()
print('app.yaml has service: f1:', 'service: f1' in ay)

print('\n=== ALL ' + str(11) + ' STEPS COMPLETE (TS=' + TS + ') ===')
