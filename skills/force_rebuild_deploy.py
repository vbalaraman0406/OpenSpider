import os, time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# 1. Verify api.ts has /api not /f1/api
with open(f'{base}/frontend/src/api.ts', 'r') as f:
    api_content = f.read()
print('api.ts baseURL check:')
if '/f1/api' in api_content:
    print('  STILL HAS /f1/api - fixing...')
    api_content = api_content.replace('/f1/api', '/api')
    with open(f'{base}/frontend/src/api.ts', 'w') as f:
        f.write(api_content)
else:
    print('  OK - uses /api')

# 2. Force JS bundle hash change by adding timestamp to Dashboard.tsx
dash_path = f'{base}/frontend/src/pages/Dashboard.tsx'
with open(dash_path, 'r') as f:
    dash = f.read()

timestamp = str(time.time())
if '/* DEPLOY_MARKER' in dash:
    import re
    dash = re.sub(r'/\* DEPLOY_MARKER.*?\*/', f'/* DEPLOY_MARKER:{timestamp} */', dash)
else:
    dash = dash.replace('export default', f'/* DEPLOY_MARKER:{timestamp} */\nexport default')

with open(dash_path, 'w') as f:
    f.write(dash)
print(f'Dashboard.tsx deploy marker: {timestamp}')

# 3. Also force main.py timestamp change
main_path = f'{base}/backend/main.py'
with open(main_path, 'r') as f:
    main = f.read()
import re
main = re.sub(r'# DEPLOY_TS:.*', f'# DEPLOY_TS:{timestamp}', main)
if f'# DEPLOY_TS:{timestamp}' not in main:
    main += f'\n# DEPLOY_TS:{timestamp}\n'
with open(main_path, 'w') as f:
    f.write(main)
print(f'main.py deploy marker: {timestamp}')

print('\nAll files prepared. Ready for rebuild and deploy.')
